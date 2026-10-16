package com.trinetra.ai.data.sync

import android.content.Context
import androidx.work.BackoffPolicy
import androidx.work.Constraints
import androidx.work.CoroutineWorker
import androidx.work.ExistingWorkPolicy
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkerParameters
import com.trinetra.ai.api.V3ApiClient
import com.trinetra.ai.data.local.AppDatabase
import com.trinetra.ai.data.local.VerificationSyncState
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.util.UUID
import java.util.concurrent.TimeUnit

class VerificationSyncWorker(
    appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val database = AppDatabase.getInstance(applicationContext)
        val dao = database.verificationDao()
        val items = dao.getPendingOutboxItems()
        if (items.isEmpty()) return Result.success()

        var hasRetry = false
        for (item in items) {
            val payload = JSONObject(item.payload)
            val isSuccess = when (item.eventType) {
                "CHECKPOINT" -> syncCheckpoint(item, payload)
                "EVIDENCE" -> syncEvidence(item, payload)
                else -> true
            }
            if (isSuccess) {
                dao.deleteOutboxItem(item.outboxId)
                dao.updateOutboxStatus(item.outboxId, VerificationSyncState.SYNCED.name, null)
            } else {
                hasRetry = true
                dao.incrementOutboxAttempts(item.outboxId)
                dao.updateOutboxStatus(item.outboxId, VerificationSyncState.FAILED_RETRYABLE.name, "Sync failed")
            }
        }
        return if (hasRetry) Result.retry() else Result.success()
    }

    private fun syncCheckpoint(item: com.trinetra.ai.data.local.OutboxEventEntity, payload: JSONObject): Boolean {
        val verificationId = item.verificationId
        val checkpointId = payload.optString("checkpointId", "")
        if (verificationId.isBlank() || checkpointId.isBlank()) return false
        val response = V3ApiClient.submitCheckpoint(
            context = applicationContext,
            verificationId = verificationId,
            checkpointId = checkpointId,
            clientEventId = payload.optString("clientEventId", UUID.randomUUID().toString()),
            sequenceNumber = payload.optInt("sequenceNumber", 1),
            location = "offline-sync",
            operatorId = payload.optString("operatorId", "mobile-operator"),
            observedSerial = payload.optString("observedSerial", "").takeIf { it.isNotBlank() },
            observedImei = payload.optString("observedImei", "").takeIf { it.isNotBlank() },
            condition = payload.optString("condition", "NORMAL"),
            photoFilePath = item.localFilePath
        )
        return response != null
    }

    private fun syncEvidence(item: com.trinetra.ai.data.local.OutboxEventEntity, payload: JSONObject): Boolean {
        val filePath = item.localFilePath ?: return false
        val response = V3ApiClient.uploadEvidence(
            context = applicationContext,
            verificationId = item.verificationId,
            checkpointId = item.checkpointId ?: "",
            clientEventId = payload.optString("clientEventId", UUID.randomUUID().toString()),
            type = payload.optString("type", "CAMERA_OBSERVATION"),
            source = payload.optString("source", "CAMERAX_OPENCV"),
            photoFilePath = filePath,
            capturedBy = payload.optString("capturedBy", "android_app"),
            capturedAt = payload.optString("timestamp", null)
        )
        return response != null
    }

    companion object {
        fun enqueue(context: Context) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()

            val request = OneTimeWorkRequestBuilder<VerificationSyncWorker>()
                .setConstraints(constraints)
                .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
                .build()

            WorkManager.getInstance(context).enqueueUniqueWork(
                "trinetra_verification_sync",
                ExistingWorkPolicy.KEEP,
                request
            )
        }
    }
}
