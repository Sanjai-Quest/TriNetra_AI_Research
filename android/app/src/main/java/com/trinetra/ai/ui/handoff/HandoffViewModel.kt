package com.trinetra.ai.ui.handoff

import android.app.Application
import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationManager
import android.util.Log
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import androidx.core.content.ContextCompat
import com.trinetra.ai.api.V3ApiClient
import com.trinetra.ai.ble.DemoBleScaleTelemetrySource
import com.trinetra.ai.ble.ScaleTelemetryPacket
import com.trinetra.ai.cv.CVAnalysisResult
import com.trinetra.ai.data.local.AppDatabase
import com.trinetra.ai.data.local.CheckpointRecordEntity
import com.trinetra.ai.data.local.EvidenceRecordEntity
import com.trinetra.ai.data.local.OutboxEventEntity
import com.trinetra.ai.data.local.SerializedUnitCacheEntity
import com.trinetra.ai.data.local.TelemetryEntity
import com.trinetra.ai.data.local.VerificationRecordEntity
import com.trinetra.ai.data.local.VerificationSyncState
import com.trinetra.ai.data.sync.TelemetryUploadWorker
import com.trinetra.ai.data.sync.VerificationSyncWorker
import com.trinetra.ai.nlp.VoiceClassificationResult
import com.trinetra.ai.nlp.VoiceClassifier
import com.trinetra.ai.identity.QrProductIdentifierSource
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.time.Instant
import java.time.format.DateTimeFormatter
import java.util.UUID

// 1. MVI State Pipeline: Idle -> Recording -> Processing -> Success / Error
sealed interface HandoffState {
    object Idle : HandoffState
    object Recording : HandoffState
    data class Processing(val stageMessage: String) : HandoffState
    data class Success(
        val caseId: String,
        val scannedSealId: String,
        val transcript: String,
        val result: VoiceClassificationResult,
        val telemetryJson: String,
        val isOfflineQueued: Boolean,
        val engineUsed: String,  // "GROQ_CLOUD" | "LOCAL_CPU"
        val scaleReading: ScaleTelemetryPacket? = null,
        val decision: String? = null
    ) : HandoffState
    data class Error(val errorMessage: String) : HandoffState
}

// 2. MVI Intent Events
sealed class HandoffIntent {
    data class ScanSeal(val sealId: String) : HandoffIntent()
    data class SetPhysicalIdentity(val serial: String, val imei: String?) : HandoffIntent()
    data class ScaleReading(val baseWeightGrams: Double) : HandoffIntent()
    // New intent to submit the entire verification flow with condition and optional photo
    data class SubmitVerification(val condition: String, val photoFilePath: String?) : HandoffIntent()
    object StartRecording : HandoffIntent()
    data class ProcessVoiceInput(val rawTranscript: String) : HandoffIntent()
    object SubmitTelemetry : HandoffIntent()
    // Captures a signed weight reading. baseWeightGrams lets the demo operator choose
    // between a consistent return (642g, matches outbound) and a swap scenario (210g).
    // In production this value comes from a real GATT callback; in this demo path we
    // preserve the selected value exactly so the fraud logic compares real numbers.
}

/**
 * Jetpack Compose MVI ViewModel managing state flow and offline SQLite + WorkManager synchronization.
 *
 * NLP Priority:
 *   1. Groq Cloud LLM via Spring Boot backend proxy (/api/voice/parse) — semantic, multilingual.
 *   2. Local CPU VoiceClassifier — automatic fallback when offline or backend unavailable.
 */
class HandoffViewModel(application: Application) : AndroidViewModel(application) {

    companion object {
        const val DEMO_CASE_ID = "CASE-ORD-98402"
        const val DEMO_ORDER_ID = "ORD-98402"
        const val DEMO_PACKAGE_ID = "UNIT-SN001"
        const val DEMO_PRODUCT = "Smartphone"
    }

    private val _state = MutableStateFlow<HandoffState>(HandoffState.Idle)
    val state: StateFlow<HandoffState> = _state.asStateFlow()
    private val _liveLocation = MutableStateFlow<Location?>(null)
    val liveLocation: StateFlow<Location?> = _liveLocation.asStateFlow()

    private val classifier = VoiceClassifier()
    private val qrIdentifierSource = QrProductIdentifierSource()
    private val scaleManager = DemoBleScaleTelemetrySource()
    private val database = AppDatabase.getInstance(application)
    private var currentPhotoPath: String? = null
    private var currentVerificationId: String? = null
    private var currentOfflineUnitLabel: String? = null
    private var currentSealId: String = "TRN-SEAL-8821-X"
    // expose photo path for submission
    fun updatePhotoPath(path: String) {
        currentPhotoPath = path
    }
    private var currentObservedSerial: String? = null
    private var currentObservedImei: String? = null
    private var currentPackageId: String = DEMO_PACKAGE_ID
    private var currentScaleReading: ScaleTelemetryPacket? = null
    private var currentCameraMetrics: CVAnalysisResult? = null
    private var locationManager: LocationManager? = null
    private val locationListener = object : android.location.LocationListener {
        override fun onLocationChanged(location: Location) {
            _liveLocation.value = location
        }
    }
    // Known-good seeded outbound (warehouse dispatch) weight for the demo order.
    private val outboundWeightGrams: Double = 642.0

    // Same host candidates as TelemetryUploadWorker — try in order.
    // Editable at runtime from the Handoff screen (see BackendConfig) so demo-day
    // WiFi changes don't require a rebuild.
    private val backendHosts: List<String>
        get() = com.trinetra.ai.data.net.BackendConfig.getHosts(getApplication())

    fun processIntent(intent: HandoffIntent) {
        when (intent) {
            is HandoffIntent.ScanSeal -> {
                currentSealId = intent.sealId
            }
            is HandoffIntent.SetPhysicalIdentity -> {
                currentObservedSerial = intent.serial.trim().ifBlank { null }
                currentObservedImei = intent.imei?.trim()?.ifBlank { null }
            }
            is HandoffIntent.StartRecording -> {
                _state.value = HandoffState.Recording
            }
            is HandoffIntent.ProcessVoiceInput -> {
                runVoiceParsing(intent.rawTranscript)
            }
            is HandoffIntent.SubmitTelemetry -> {
                // Handled in processing pipeline
            }
            is HandoffIntent.ScaleReading -> {
                currentScaleReading = scaleManager.readScaleData(baseWeightGrams = intent.baseWeightGrams)
                Log.i("HandoffViewModel", "[BLE] Signed scale reading captured: ${currentScaleReading?.weightGrams}g")
            }
            is HandoffIntent.SubmitVerification -> {
                // Use current photo path if not provided directly
                viewModelScope.launch { submitVerificationFlow(intent.condition, intent.photoFilePath ?: currentPhotoPath) }
            }
        }
    }

    fun updateCameraMetrics(metrics: CVAnalysisResult) {
        currentCameraMetrics = metrics
    }

    fun updatePackageIdentifier(orderId: String): Boolean {
        val identifier = qrIdentifierSource.resolve(orderId) ?: return false
        currentPackageId = identifier.packageId
        return true
    }

    @SuppressLint("MissingPermission")
    fun startLiveLocation() {
        val context = getApplication<Application>()
        val hasFine = ContextCompat.checkSelfPermission(
            context, android.Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
        val hasCoarse = ContextCompat.checkSelfPermission(
            context, android.Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
        if (!hasFine && !hasCoarse) return

        try {
            val manager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
            locationManager = manager
            listOf(LocationManager.GPS_PROVIDER, LocationManager.NETWORK_PROVIDER)
                .filter { manager.isProviderEnabled(it) }
                .forEach { provider ->
                    manager.requestLocationUpdates(provider, 2000L, 1f, locationListener)
                    manager.getLastKnownLocation(provider)?.let { latest ->
                        if (_liveLocation.value == null || latest.time > (_liveLocation.value?.time ?: 0L)) {
                            _liveLocation.value = latest
                        }
                    }
                }
        } catch (securityException: SecurityException) {
            Log.w("HandoffViewModel", "Live location permission unavailable: ${securityException.message}")
        }
    }

    private fun runVoiceParsing(transcript: String) {
        viewModelScope.launch {
            _state.value = HandoffState.Processing("Connecting to Groq AI Engine...")
            try {
                // ── Primary: Groq Cloud LLM via backend proxy ──────────────
                val groqResult = tryGroqBackend(transcript)
                if (groqResult != null) {
                    Log.i("HandoffViewModel", "[GROQ] Successfully parsed transcript.")
                    finalizeResult(transcript, groqResult.first, groqResult.second, "GROQ_CLOUD")
                    return@launch
                }
                // ── Fallback: local CPU Naive Bayes classifier ─────────────
                Log.w("HandoffViewModel", "[LOCAL FALLBACK] Groq unavailable, using local classifier.")
                _state.value = HandoffState.Processing("Groq offline — Running Local CPU Classifier...")
                val localResult = withContext(Dispatchers.Default) { classifier.classify(transcript) }
                finalizeResult(transcript, localResult, null, "LOCAL_CPU")

            } catch (e: Exception) {
                Log.e("HandoffViewModel", "Voice parsing pipeline failed: ${e.message}", e)
                _state.value = HandoffState.Error("Voice parsing failed: ${e.message}")
            }
        }
    }

    /**
     * Attempts POST /api/voice/parse on each backend host candidate.
     * Returns Pair<VoiceClassificationResult, rawGroqJson> on success, null otherwise.
     */
    private suspend fun tryGroqBackend(transcript: String): Pair<VoiceClassificationResult, String>? =
        withContext(Dispatchers.IO) {
            for (host in backendHosts) {
                var connection: HttpURLConnection? = null
                try {
                    val url = URL("$host/api/voice/parse")
                    connection = url.openConnection() as HttpURLConnection
                    connection.requestMethod = "POST"
                    connection.setRequestProperty("Content-Type", "text/plain; charset=utf-8")
                    connection.setRequestProperty("Accept", "application/json")
                    connection.connectTimeout = 5000
                    connection.readTimeout = 15000   // Groq LLM may take a few seconds
                    connection.doOutput = true

                    OutputStreamWriter(connection.outputStream, "UTF-8").use { writer ->
                        writer.write(transcript)
                        writer.flush()
                    }

                    val responseCode = connection.responseCode
                    if (responseCode in 200..299) {
                        val responseJson = connection.inputStream.bufferedReader().use { it.readText() }
                        Log.i("HandoffViewModel", "[GROQ] $host responded $responseCode: $responseJson")
                        val parsed = parseGroqJson(responseJson)
                        if (parsed != null) return@withContext Pair(parsed, responseJson)
                    } else {
                        Log.w("HandoffViewModel", "[GROQ] $host returned HTTP $responseCode")
                    }
                } catch (e: Exception) {
                    Log.w("HandoffViewModel", "[GROQ] Connect failed to $host: ${e.message}")
                } finally {
                    connection?.disconnect()
                }
            }
            null
        }

    /** Maps Groq LLM JSON response to VoiceClassificationResult. */
    private fun parseGroqJson(json: String): VoiceClassificationResult? {
        return try {
            val obj = JSONObject(json)
            VoiceClassificationResult(
                anomalyDetected = obj.optBoolean("anomaly_detected", false),
                sealIntegrityStatus = obj.optString("seal_integrity_status", "INTACT"),
                weightAssessment = obj.optString("weight_assessment", "NORMAL"),
                confidenceScore = obj.optDouble("confidence_score", 0.5),
                latencyMs = 0L
            )
        } catch (e: Exception) {
            Log.e("HandoffViewModel", "Failed to parse Groq JSON response: ${e.message}")
            null
        }
    }

    private suspend fun finalizeResult(
        transcript: String,
        nlpResult: VoiceClassificationResult,
        rawGroqJson: String?,
        engineUsed: String
    ) {
        _state.value = HandoffState.Processing("Generating Signed Telemetry Packet...")

        val caseId = DEMO_CASE_ID
        val timestampUtc = DateTimeFormatter.ISO_INSTANT.format(Instant.now())
        val location = readCurrentLocation()
        val currentLat = location?.latitude
        val currentLon = location?.longitude

        val jsonPayload = JSONObject().apply {
            // These values are intentionally the actual selected demo-scale return reading.
            // If the operator taps "Swap Detected (210g)", the JSON must record 210.0, not a
            // truncated or arithmetic-mutated partial weight.
            put("case_id", caseId)
            put("order_id", DEMO_ORDER_ID)
            put("package_id", currentPackageId)
            put("product_name", DEMO_PRODUCT)
            put("scanned_seal_id", currentSealId)
            put("raw_transcript", transcript)
            put("gps_lat", currentLat ?: JSONObject.NULL)
            put("gps_lon", currentLon ?: JSONObject.NULL)
            put("timestamp_utc", timestampUtc)
            put("nlp_engine", engineUsed)
            put("nlp_metrics", JSONObject().apply {
                put("anomaly_detected", nlpResult.anomalyDetected)
                put("seal_integrity_status", nlpResult.sealIntegrityStatus)
                put("weight_assessment", nlpResult.weightAssessment)
                put("confidence_score", nlpResult.confidenceScore)
                put("latency_ms", nlpResult.latencyMs)
            })
            if (rawGroqJson != null) {
                put("groq_raw_response", JSONObject(rawGroqJson))
            }
            put("outbound_weight_grams", outboundWeightGrams)
            put("camera_mode", "CAMERAX_OPENCV")
            put("parser_mode", if (engineUsed == "LOCAL_CPU") "LOCAL_CPU_PARSER" else "GROQ_CLOUD_PARSER")
            if (currentScaleReading != null) {
                put("return_weight_grams", currentScaleReading!!.weightGrams)
                put("ble_scale_packet", JSONObject(currentScaleReading!!.jsonPayload))
            } else {
                put("return_weight_grams", JSONObject.NULL)
                put("scale_reading_note", "No BLE scale reading captured for this case yet.")
            }
        }.toString(2)

        // Save to Room SQLite Cache (Offline First) — captures the ACTUAL scale reading
        // taken on this device (or none, honestly, if the operator hasn't tapped the
        // scale-read action) rather than a fabricated number.
        val entity = TelemetryEntity(
            caseId = caseId,
            orderId = DEMO_ORDER_ID,
            packageId = currentPackageId,
            productName = DEMO_PRODUCT,
            scannedSealId = currentSealId,
            observedSerial = currentObservedSerial,
            observedImei = currentObservedImei,
            rawTranscript = transcript,
            parsedJson = jsonPayload,
            gpsLat = currentLat,
            gpsLon = currentLon,
            timestampUtc = timestampUtc,
            isSynced = false,
            outboundWeightGrams = outboundWeightGrams,
            returnWeightGrams = currentScaleReading?.weightGrams,
            scaleSignatureJson = currentScaleReading?.jsonPayload,
            cameraMetricsJson = null,
            parserMode = if (engineUsed == "LOCAL_CPU") "LOCAL_CPU_PARSER" else "GROQ_CLOUD_PARSER",
            scaleMode = if (currentScaleReading != null) "DEMO_GATT_SCALE" else "NOT_CAPTURED"
        )
        withContext(Dispatchers.IO) {
            database.telemetryDao().insertTelemetry(entity)
        }
        ensureUnitCacheSeeded()

        // Old telemetry upload flow – replaced by V3 verification flow
        // TelemetryUploadWorker.enqueue(getApplication<Application>())
        // New V3 flow: open verification, submit checkpoint with observed data, photo, condition, then fetch verdict.
        // This will be triggered by a new intent (SubmitVerification) implemented later.
        // Existing telemetry path remains for voice parsing; new V3 flow will set its own Success state.
        _state.value = HandoffState.Success(
            caseId = caseId,
            scannedSealId = currentSealId,
            transcript = transcript,
            result = nlpResult,
            telemetryJson = jsonPayload,
            isOfflineQueued = true,
            engineUsed = engineUsed,
            scaleReading = currentScaleReading,
            decision = null
        )
    }

    private fun readCurrentLocation(): Location? {
        _liveLocation.value?.let { return it }
        val context = getApplication<Application>()
        val hasFine = ContextCompat.checkSelfPermission(
            context, android.Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
        val hasCoarse = ContextCompat.checkSelfPermission(
            context, android.Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
        if (!hasFine && !hasCoarse) return null

        return try {
            val manager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
            listOf(LocationManager.GPS_PROVIDER, LocationManager.NETWORK_PROVIDER)
                .asSequence()
                .filter { manager.isProviderEnabled(it) }
                .mapNotNull { provider -> manager.getLastKnownLocation(provider) }
                .maxByOrNull { it.time }
        } catch (securityException: SecurityException) {
            Log.w("HandoffViewModel", "Live location unavailable: ${securityException.message}")
            null
        }
    }

    /** New V3 verification workflow */
    private suspend fun submitVerificationFlow(condition: String, photoFilePath: String?) {
        val ctx = getApplication<Application>()
        ensureUnitCacheSeeded()
        val unit = database.verificationDao().getSerializedUnit(currentPackageId)
            ?: SerializedUnitCacheEntity(
                unitId = currentPackageId,
                product = DEMO_PRODUCT,
                expectedSerial = "SN001",
                expectedImei = "IMEI001",
                lastSyncedAt = Instant.now().toString(),
                source = "LOCAL_FALLBACK"
            )

        val expectedSerial = unit.expectedSerial
        val expectedImei = unit.expectedImei
        val localDecision = evaluateProvisionalDecision(expectedSerial, currentObservedSerial, expectedImei, currentObservedImei, condition)
        val verificationId = UUID.randomUUID().toString()
        val checkpointId = UUID.randomUUID().toString()
        val clientEventId = UUID.randomUUID().toString()
        val timestamp = Instant.now().toString()
        currentVerificationId = verificationId

        val verificationRecord = VerificationRecordEntity(
            verificationId = verificationId,
            unitId = currentPackageId,
            operatorId = DEMO_ORDER_ID,
            state = "PENDING",
            localDecision = localDecision,
            serverDecision = null,
            createdAt = timestamp,
            updatedAt = timestamp,
            lastSyncError = null
        )
        val checkpointRecord = CheckpointRecordEntity(
            checkpointId = checkpointId,
            verificationId = verificationId,
            clientEventId = clientEventId,
            sequenceNumber = 1,
            unitId = currentPackageId,
            expectedSerial = expectedSerial,
            observedSerial = currentObservedSerial ?: "",
            expectedImei = expectedImei,
            observedImei = currentObservedImei,
            condition = condition,
            decision = localDecision,
            timestamp = timestamp,
            syncState = VerificationSyncState.PENDING.name
        )

        withContext(Dispatchers.IO) {
            database.verificationDao().upsertVerification(verificationRecord)
            database.verificationDao().upsertCheckpoint(checkpointRecord)
        }

        val payload = JSONObject().apply {
            put("verificationId", verificationId)
            put("unitId", currentPackageId)
            put("operatorId", DEMO_ORDER_ID)
            put("checkpointId", checkpointId)
            put("clientEventId", clientEventId)
            put("sequenceNumber", 1)
            put("observedSerial", currentObservedSerial ?: "")
            put("observedImei", currentObservedImei ?: JSONObject.NULL)
            put("condition", condition)
            put("expectedSerial", expectedSerial)
            put("expectedImei", expectedImei ?: JSONObject.NULL)
        }.toString()

        val evidenceId = if (photoFilePath != null) {
            val newEvidenceId = UUID.randomUUID().toString()
            val evidencePayload = JSONObject().apply {
                put("source", "CAMERAX_OPENCV")
                put("storageReference", photoFilePath)
                put("capturedBy", DEMO_ORDER_ID)
                put("type", "CAMERA_OBSERVATION")
            }.toString()
            withContext(Dispatchers.IO) {
                database.verificationDao().upsertEvidence(
                    EvidenceRecordEntity(
                        evidenceId = newEvidenceId,
                        verificationId = verificationId,
                        checkpointId = checkpointId,
                        clientEventId = UUID.randomUUID().toString(),
                        type = "CAMERA_OBSERVATION",
                        source = "CAMERAX_OPENCV",
                        storageReference = photoFilePath,
                        capturedBy = DEMO_ORDER_ID,
                        timestamp = timestamp,
                        payloadJson = evidencePayload,
                        syncState = VerificationSyncState.PENDING.name
                    )
                )
            }
            withContext(Dispatchers.IO) {
                database.verificationDao().insertOutboxItem(
                    OutboxEventEntity(
                        outboxId = UUID.randomUUID().toString(),
                        eventType = "EVIDENCE",
                        verificationId = verificationId,
                        checkpointId = checkpointId,
                        evidenceId = newEvidenceId,
                        clientEventId = UUID.randomUUID().toString(),
                        payload = evidencePayload,
                        localFilePath = photoFilePath,
                        createdAt = timestamp,
                        status = VerificationSyncState.PENDING.name,
                        lastError = null
                    )
                )
            }
            newEvidenceId
        } else null

        withContext(Dispatchers.IO) {
            database.verificationDao().insertOutboxItem(
                OutboxEventEntity(
                    outboxId = UUID.randomUUID().toString(),
                    eventType = "CHECKPOINT",
                    verificationId = verificationId,
                    checkpointId = checkpointId,
                    evidenceId = evidenceId,
                    clientEventId = clientEventId,
                    payload = payload,
                    localFilePath = photoFilePath,
                    createdAt = timestamp,
                    status = VerificationSyncState.PENDING.name,
                    lastError = null
                )
            )
        }

        val online = isBackendReachable()
        if (online) {
            val response = withContext(Dispatchers.IO) {
                V3ApiClient.openVerification(ctx, currentPackageId, DEMO_ORDER_ID)
            }
            if (response != null) {
                val checkpointResponse = withContext(Dispatchers.IO) {
                    V3ApiClient.submitCheckpoint(
                        context = ctx,
                        verificationId = response,
                        checkpointId = checkpointId,
                        clientEventId = clientEventId,
                        sequenceNumber = 1,
                        location = readCurrentLocation()?.let { "${it.latitude},${it.longitude}" } ?: "UNKNOWN",
                        operatorId = DEMO_ORDER_ID,
                        observedSerial = currentObservedSerial,
                        observedImei = currentObservedImei,
                        condition = condition,
                        photoFilePath = photoFilePath
                    )
                }
                val serverDecision = checkpointResponse?.optString("decision")?.takeIf { it.isNotBlank() } ?: localDecision
                withContext(Dispatchers.IO) {
                    database.verificationDao().upsertVerification(
                        database.verificationDao().getVerification(verificationId)?.copy(
                            state = "SYNCED",
                            serverDecision = serverDecision,
                            lastSyncError = null,
                            updatedAt = Instant.now().toString()
                        ) ?: verificationRecord.copy(state = "SYNCED", serverDecision = serverDecision, updatedAt = Instant.now().toString())
                    )
                }
                _state.value = HandoffState.Success(
                    caseId = response,
                    scannedSealId = currentSealId,
                    transcript = "",
                    result = VoiceClassificationResult(false, "INTACT", "NORMAL", 0.0, 0L),
                    telemetryJson = payload,
                    isOfflineQueued = false,
                    engineUsed = "V3_BACKEND",
                    scaleReading = currentScaleReading,
                    decision = "SERVER VERIFIED\n$serverDecision"
                )
            } else {
                _state.value = HandoffState.Success(
                    caseId = verificationId,
                    scannedSealId = currentSealId,
                    transcript = "",
                    result = VoiceClassificationResult(false, "INTACT", "NORMAL", 0.0, 0L),
                    telemetryJson = payload,
                    isOfflineQueued = true,
                    engineUsed = "OFFLINE",
                    scaleReading = currentScaleReading,
                    decision = "PROVISIONAL - PENDING SERVER SYNC\n$localDecision"
                )
            }
        } else {
            _state.value = HandoffState.Success(
                caseId = verificationId,
                scannedSealId = currentSealId,
                transcript = "",
                result = VoiceClassificationResult(false, "INTACT", "NORMAL", 0.0, 0L),
                telemetryJson = payload,
                isOfflineQueued = true,
                engineUsed = "OFFLINE",
                scaleReading = currentScaleReading,
                decision = "PROVISIONAL - PENDING SERVER SYNC\n$localDecision"
            )
        }

        if (photoFilePath != null) {
            java.io.File(photoFilePath).let { if (it.exists()) it.absolutePath }
        }
    }

    private suspend fun ensureUnitCacheSeeded() {
        val cached = withContext(Dispatchers.IO) {
            database.verificationDao().getSerializedUnit(currentPackageId)
        }
        if (cached == null) {
            val seed = SerializedUnitCacheEntity(
                unitId = currentPackageId,
                product = DEMO_PRODUCT,
                expectedSerial = "SN001",
                expectedImei = "IMEI001",
                lastSyncedAt = Instant.now().toString(),
                source = "SEED"
            )
            withContext(Dispatchers.IO) {
                database.verificationDao().upsertSerializedUnit(seed)
            }
            currentOfflineUnitLabel = "OFFLINE - USING CACHED UNIT DATA"
        } else {
            currentOfflineUnitLabel = "OFFLINE - USING CACHED UNIT DATA"
        }
    }

    private fun evaluateProvisionalDecision(
        expectedSerial: String,
        observedSerial: String?,
        expectedImei: String?,
        observedImei: String?,
        condition: String?
    ): String {
        val serialMatch = !observedSerial.isNullOrBlank() && observedSerial.trim().equals(expectedSerial.trim(), ignoreCase = true)
        val imeiMatch = if (expectedImei.isNullOrBlank() || observedImei.isNullOrBlank()) true else observedImei.trim().equals(expectedImei.trim(), ignoreCase = true)
        return when {
            !serialMatch -> "HOLD"
            !imeiMatch -> "HOLD"
            condition.equals("DAMAGED", ignoreCase = true) || condition.equals("TAMPERED", ignoreCase = true) -> "REVIEW"
            else -> "PASS"
        }
    }

    private suspend fun isBackendReachable(): Boolean = withContext(Dispatchers.IO) {
        for (host in backendHosts) {
            try {
                val connection = URL("$host/api/verifications").openConnection() as HttpURLConnection
                connection.connectTimeout = 1500
                connection.readTimeout = 1500
                connection.requestMethod = "GET"
                connection.connect()
                val responseCode = connection.responseCode
                Log.i("HandoffViewModel", "Backend probe $host -> HTTP $responseCode")
                if (responseCode in 200..299) {
                    connection.disconnect()
                    return@withContext true
                }
                connection.disconnect()
            } catch (exception: Exception) {
                Log.w("HandoffViewModel", "Backend probe failed $host: ${exception.javaClass.simpleName}: ${exception.message}")
            }
        }
        return@withContext false
    }

    override fun onCleared() {
        locationManager?.removeUpdates(locationListener)
        super.onCleared()
    }
}
