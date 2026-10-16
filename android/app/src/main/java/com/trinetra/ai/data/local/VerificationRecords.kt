package com.trinetra.ai.data.local

import androidx.room.Dao
import androidx.room.Entity
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.PrimaryKey
import androidx.room.Query

enum class VerificationSyncState {
    PENDING,
    SYNCING,
    SYNCED,
    FAILED_RETRYABLE,
    FAILED_PERMANENT
}

@Entity(tableName = "serialized_unit_cache")
data class SerializedUnitCacheEntity(
    @PrimaryKey val unitId: String,
    val product: String,
    val expectedSerial: String,
    val expectedImei: String?,
    val lastSyncedAt: String?,
    val source: String = "LOCAL_CACHE"
)

@Entity(tableName = "verification_records")
data class VerificationRecordEntity(
    @PrimaryKey val verificationId: String,
    val unitId: String,
    val operatorId: String,
    val state: String,
    val localDecision: String?,
    val serverDecision: String?,
    val createdAt: String,
    val updatedAt: String,
    val lastSyncError: String?
)

@Entity(tableName = "checkpoint_records")
data class CheckpointRecordEntity(
    @PrimaryKey val checkpointId: String,
    val verificationId: String,
    val clientEventId: String,
    val sequenceNumber: Int,
    val unitId: String,
    val expectedSerial: String,
    val observedSerial: String,
    val expectedImei: String?,
    val observedImei: String?,
    val condition: String?,
    val decision: String,
    val timestamp: String,
    val syncState: String = VerificationSyncState.PENDING.name
)

@Entity(tableName = "evidence_records")
data class EvidenceRecordEntity(
    @PrimaryKey val evidenceId: String,
    val verificationId: String,
    val checkpointId: String,
    val clientEventId: String,
    val type: String,
    val source: String,
    val storageReference: String,
    val capturedBy: String,
    val timestamp: String,
    val payloadJson: String,
    val syncState: String = VerificationSyncState.PENDING.name
)

@Entity(tableName = "outbox_events")
data class OutboxEventEntity(
    @PrimaryKey val outboxId: String,
    val eventType: String,
    val verificationId: String,
    val checkpointId: String?,
    val evidenceId: String?,
    val clientEventId: String,
    val payload: String,
    val localFilePath: String?,
    val createdAt: String,
    val attemptCount: Int = 0,
    val status: String = VerificationSyncState.PENDING.name,
    val lastError: String? = null
)

@Dao
interface VerificationDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertSerializedUnit(entity: SerializedUnitCacheEntity)

    @Query("SELECT * FROM serialized_unit_cache WHERE unitId = :unitId LIMIT 1")
    suspend fun getSerializedUnit(unitId: String): SerializedUnitCacheEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertVerification(entity: VerificationRecordEntity)

    @Query("SELECT * FROM verification_records WHERE verificationId = :verificationId LIMIT 1")
    suspend fun getVerification(verificationId: String): VerificationRecordEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertCheckpoint(entity: CheckpointRecordEntity)

    @Query("SELECT * FROM checkpoint_records WHERE verificationId = :verificationId ORDER BY sequenceNumber ASC")
    suspend fun getCheckpointsForVerification(verificationId: String): List<CheckpointRecordEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertEvidence(entity: EvidenceRecordEntity)

    @Query("SELECT * FROM evidence_records WHERE verificationId = :verificationId ORDER BY timestamp ASC")
    suspend fun getEvidenceForVerification(verificationId: String): List<EvidenceRecordEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOutboxItem(entity: OutboxEventEntity)

    @Query("SELECT * FROM outbox_events WHERE status IN ('PENDING', 'FAILED_RETRYABLE') ORDER BY createdAt ASC")
    suspend fun getPendingOutboxItems(): List<OutboxEventEntity>

    @Query("UPDATE outbox_events SET status = :status, lastError = :lastError WHERE outboxId = :outboxId")
    suspend fun updateOutboxStatus(outboxId: String, status: String, lastError: String?)

    @Query("UPDATE outbox_events SET attemptCount = attemptCount + 1 WHERE outboxId = :outboxId")
    suspend fun incrementOutboxAttempts(outboxId: String)

    @Query("DELETE FROM outbox_events WHERE outboxId = :outboxId")
    suspend fun deleteOutboxItem(outboxId: String)
}
