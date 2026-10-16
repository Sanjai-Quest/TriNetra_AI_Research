package com.trinetra.ai.data.local

import org.junit.Assert.assertEquals
import org.junit.Test

class VerificationThreadTest {
    @Test
    fun verificationThreadUsesStableIdsAndSyncStates() {
        assertEquals("PENDING", VerificationSyncState.PENDING.name)
        assertEquals("SYNCED", VerificationSyncState.SYNCED.name)
        assertEquals("FAILED_RETRYABLE", VerificationSyncState.FAILED_RETRYABLE.name)
    }
}
