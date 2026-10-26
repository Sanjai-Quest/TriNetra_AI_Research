package com.trinetra.ai.api

import android.content.Context
import android.util.Log
import org.json.JSONArray
import org.json.JSONObject
import java.io.DataOutputStream
import java.io.File
import java.io.FileInputStream
import java.net.HttpURLConnection
import java.net.URL

/**
 * Mobile Ingest HTTP Client for TriNetra-Link (Phase B).
 * Submits CP1–CP4 physical observations (repeated weights, photos, and seal QR)
 * to the FastAPI capture server.
 */
object TriNetraLinkClient {
    private const val TAG = "TriNetraLinkClient"

    data class CheckpointUploadPayload(
        val journeyCode: String,
        val cpIndex: Int,
        val deviceId: String,
        val operatorId: String,
        val weightsG: List<Double>,
        val scaleId: String = "SCALE-BLE-01",
        val scaleStatus: String = "OK",
        val sealQr: String? = null,
        val serial: String? = null,
        val imei: String? = null,
        val carrierLog: String? = null,
        val permittedPackagingChange: Boolean = false,
        val tareDeltaG: Double = 0.0,
        val photoFile: File? = null,
        val photoSide: String = "front"
    )

    fun submitCheckpoint(
        baseUrl: String,
        token: String,
        payload: CheckpointUploadPayload
    ): String? {
        val boundary = "===TriNetraLinkBoundary" + System.currentTimeMillis() + "==="
        val lineEnd = "\r\n"
        val twoHyphens = "--"
        var conn: HttpURLConnection? = null
        try {
            val endpoint = "$baseUrl/journeys/${payload.journeyCode}/checkpoints/${payload.cpIndex}"
            val url = URL(endpoint)
            conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Connection", "Keep-Alive")
            conn.setRequestProperty("Cache-Control", "no-cache")
            conn.setRequestProperty("Content-Type", "multipart/form-data;boundary=$boundary")
            conn.setRequestProperty("X-Device-Token", token)
            conn.doInput = true
            conn.doOutput = true

            val outputStream = DataOutputStream(conn.outputStream)

            // Metadata JSON payload
            val metaJson = JSONObject().apply {
                put("journey_code", payload.journeyCode)
                put("cp_index", payload.cpIndex)
                put("device_id", payload.deviceId)
                put("operator_id", payload.operatorId)
                put("weights_g", JSONArray(payload.weightsG))
                put("scale_id", payload.scaleId)
                put("scale_status", payload.scaleStatus)
                put("seal_qr", payload.sealQr)
                put("serial", payload.serial)
                put("imei", payload.imei)
                put("carrier_log", payload.carrierLog)
                put("permitted_packaging_change", payload.permittedPackagingChange)
                put("tare_delta_g", payload.tareDeltaG)
            }

            outputStream.writeBytes(twoHyphens + boundary + lineEnd)
            outputStream.writeBytes("Content-Disposition: form-data; name=\"data\"" + lineEnd)
            outputStream.writeBytes("Content-Type: text/plain; charset=UTF-8" + lineEnd)
            outputStream.writeBytes(lineEnd)
            outputStream.write(metaJson.toString().toByteArray(Charsets.UTF_8))
            outputStream.writeBytes(lineEnd)

            // Image file attachment
            if (payload.photoFile != null && payload.photoFile.exists()) {
                val fileName = "cp${payload.cpIndex}_${payload.photoSide}.jpg"
                outputStream.writeBytes(twoHyphens + boundary + lineEnd)
                outputStream.writeBytes("Content-Disposition: form-data; name=\"files\"; filename=\"$fileName\"" + lineEnd)
                outputStream.writeBytes("Content-Type: image/jpeg" + lineEnd)
                outputStream.writeBytes(lineEnd)

                FileInputStream(payload.photoFile).use { fis ->
                    val buffer = ByteArray(4096)
                    var bytesRead: Int
                    while (fis.read(buffer).also { bytesRead = it } != -1) {
                        outputStream.write(buffer, 0, bytesRead)
                    }
                }
                outputStream.writeBytes(lineEnd)
            }

            outputStream.writeBytes(twoHyphens + boundary + twoHyphens + lineEnd)
            outputStream.flush()
            outputStream.close()

            val responseCode = conn.responseCode
            Log.i(TAG, "POST $endpoint -> HTTP $responseCode")
            if (responseCode in 200..299) {
                return conn.inputStream.bufferedReader().use { it.readText() }
            } else {
                val err = conn.errorStream?.bufferedReader()?.use { it.readText() }
                Log.w(TAG, "Ingest failed with HTTP $responseCode: $err")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Exception during TriNetra-Link checkpoint upload: ${e.message}", e)
        } finally {
            conn?.disconnect()
        }
        return null
    }
}
