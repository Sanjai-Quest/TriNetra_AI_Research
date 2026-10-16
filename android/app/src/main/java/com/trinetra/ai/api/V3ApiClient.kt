package com.trinetra.ai.api

import android.content.Context
import android.util.Base64
import android.util.Log
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

object V3ApiClient {
    private const val TAG = "V3ApiClient"

    // Helper to get backend hosts – reuse existing config
    private fun getHosts(context: Context): List<String> {
        return com.trinetra.ai.data.net.BackendConfig.getHosts(context)
    }

    /** Open a verification (identity pending) */
    fun openVerification(context: Context, unitId: String, operatorId: String): String? {
        val payload = JSONObject().apply {
            put("unitId", unitId)
            put("operatorId", operatorId)
        }.toString()
        for (host in getHosts(context)) {
            var conn: HttpURLConnection? = null
            try {
                val url = URL("$host/api/verifications")
                conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json; utf-8")
                conn.setRequestProperty("Accept", "application/json")
                conn.doOutput = true
                OutputStreamWriter(conn.outputStream, "UTF-8").use { it.write(payload) }
                val responseCode = conn.responseCode
                Log.i(TAG, "POST $url -> HTTP $responseCode")
                if (responseCode in 200..299) {
                    val resp = conn.inputStream.bufferedReader().use { it.readText() }
                    val json = JSONObject(resp)
                    return json.getString("verificationId")
                } else {
                    Log.w(TAG, "Open verification failed $host code $responseCode")
                }
            } catch (e: Exception) {
                Log.w(TAG, "Open verification error $host: ${e.message}")
            } finally {
                conn?.disconnect()
            }
        }
        return null
    }

    /** Submit a checkpoint with observed identity, condition and optional photo */
    fun submitCheckpoint(
        context: Context,
        verificationId: String,
        checkpointId: String,
        clientEventId: String,
        sequenceNumber: Int,
        location: String,
        operatorId: String,
        observedSerial: String?,
        observedImei: String?,
        condition: String?,
        photoFilePath: String?
    ): JSONObject? {
        // Build checkpoint JSON payload
        val payload = JSONObject().apply {
            put("checkpointId", checkpointId)
            put("clientEventId", clientEventId)
            put("sequenceNumber", sequenceNumber)
            put("location", location)
            put("operatorId", operatorId)
            observedSerial?.let { put("observedSerial", it) }
            observedImei?.let { put("observedImei", it) }
            condition?.let {
                put("condition", it)
                put("conditionStatus", it)
            }
        }
        // Photo handling – if a path is provided, include as Base64 string under "photoBase64"
        if (photoFilePath != null) {
            try {
                val bytes = java.io.File(photoFilePath).readBytes()
                val base64 = Base64.encodeToString(bytes, Base64.NO_WRAP)
                payload.put("photoBase64", base64)
                payload.put("photoFilename", java.io.File(photoFilePath).name)
            } catch (e: Exception) {
                Log.w(TAG, "Failed to read photo file: ${e.message}")
            }
        }

        for (host in getHosts(context)) {
            var conn: HttpURLConnection? = null
            try {
                val url = URL("$host/api/verifications/$verificationId/checkpoints")
                conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json; utf-8")
                conn.setRequestProperty("Accept", "application/json")
                conn.doOutput = true
                OutputStreamWriter(conn.outputStream, "UTF-8").use { it.write(payload.toString()) }
                val responseCode = conn.responseCode
                Log.i(TAG, "POST $url -> HTTP $responseCode")
                if (responseCode in 200..299) {
                    val resp = conn.inputStream.bufferedReader().use { it.readText() }
                    return JSONObject(resp)
                } else {
                    val errorBody = conn.errorStream?.bufferedReader()?.use { it.readText() }
                    Log.w(TAG, "Checkpoint submit failed $host code $responseCode body=$errorBody")
                }
            } catch (e: Exception) {
                Log.w(TAG, "Checkpoint submit error $host: ${e.message}")
            } finally {
                conn?.disconnect()
            }
        }
        return null
    }

    /** Upload evidence (photo) for a checkpoint */
    fun uploadEvidence(
        context: Context,
        verificationId: String,
        checkpointId: String,
        clientEventId: String,
        type: String = "CAMERA_OBSERVATION",
        source: String = "CAMERAX_OPENCV",
        photoFilePath: String,
        capturedBy: String = "android_app",
        capturedAt: String? = null
    ): JSONObject? {
        val file = java.io.File(photoFilePath)
        if (!file.exists()) {
            Log.w(TAG, "Evidence file not found: $photoFilePath")
            return null
        }
        val bytes = file.readBytes()
        val base64 = Base64.encodeToString(bytes, Base64.NO_WRAP)
        val payload = JSONObject().apply {
            put("evidenceId", java.util.UUID.randomUUID().toString())
            put("clientEventId", clientEventId)
            put("checkpointId", checkpointId)
            put("type", type)
            put("source", source)
            put("storageReference", file.name)
            put("payloadJson", JSONObject().apply { put("photoBase64", base64) }.toString())
            put("capturedBy", capturedBy)
            capturedAt?.let { put("capturedAt", it) }
        }
        for (host in getHosts(context)) {
            var conn: HttpURLConnection? = null
            try {
                val url = URL("$host/api/verifications/$verificationId/evidence")
                conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json; utf-8")
                conn.setRequestProperty("Accept", "application/json")
                conn.doOutput = true
                OutputStreamWriter(conn.outputStream, "UTF-8").use { it.write(payload.toString()) }
                val responseCode = conn.responseCode
                if (responseCode in 200..299) {
                    val resp = conn.inputStream.bufferedReader().use { it.readText() }
                    return JSONObject(resp)
                } else {
                    Log.w(TAG, "Evidence upload failed $host code $responseCode")
                }
            } catch (e: Exception) {
                Log.w(TAG, "Evidence upload error $host: ${e.message}")
            } finally {
                conn?.disconnect()
            }
        }
        return null
    }
}
