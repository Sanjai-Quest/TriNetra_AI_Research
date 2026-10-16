package com.trinetra.ai.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

@Database(
    entities = [
        TelemetryEntity::class,
        SerializedUnitCacheEntity::class,
        VerificationRecordEntity::class,
        CheckpointRecordEntity::class,
        EvidenceRecordEntity::class,
        OutboxEventEntity::class
    ],
    version = 6,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {

    abstract fun telemetryDao(): TelemetryDao
    abstract fun verificationDao(): VerificationDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "trinetra_edge.db"
                )
                    .fallbackToDestructiveMigration()
                    .build()
                INSTANCE = instance
                instance
            }
        }

        /**
         * Encrypted SharedPreferences helper for storing sensitive session tokens & secrets offline.
         */
        fun getEncryptedPreferences(context: Context) = EncryptedSharedPreferences.create(
            context,
            "trinetra_secure_prefs",
            MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }
}
