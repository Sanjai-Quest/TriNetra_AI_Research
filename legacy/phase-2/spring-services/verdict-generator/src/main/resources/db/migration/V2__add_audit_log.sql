-- ============================================================================
-- Flyway Migration: V2__add_audit_log.sql
-- TriNetra AI Phase 3 — Audit Log Table
--
-- Adds a unified system-level audit log for all service events.
-- Used by observability stack (Grafana dashboards) and compliance reporting.
-- Separate from investigator_actions (which is domain-level human actions).
--
-- Author: TriNetra Phase 3 Hardening
-- ============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- SYSTEM_AUDIT_LOG
-- Records all significant system events across microservices:
--   circuit breaker state changes, retry attempts, DLQ deliveries, etc.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS system_audit_log (
    log_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name    VARCHAR(100) NOT NULL,      -- e.g. claim-service, fraud-engine
    event_type      VARCHAR(100) NOT NULL,      -- e.g. CIRCUIT_BREAKER_OPEN, RETRY_EXHAUSTED, DLQ_RECEIVED
    claim_id        UUID REFERENCES claims(claim_id),
    severity        VARCHAR(20) NOT NULL DEFAULT 'INFO'
                        CHECK (severity IN ('DEBUG','INFO','WARN','ERROR','CRITICAL')),
    message         TEXT NOT NULL,
    metadata        JSONB,                      -- additional context (circuit name, retry count, etc.)
    trace_id        VARCHAR(64),               -- Micrometer tracing trace_id
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_log_service     ON system_audit_log(service_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_event_type  ON system_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_log_severity    ON system_audit_log(severity);
CREATE INDEX IF NOT EXISTS idx_audit_log_claim_id    ON system_audit_log(claim_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at  ON system_audit_log(created_at);

-- Partial index for fast querying of error-level events (Grafana alert panels)
CREATE INDEX IF NOT EXISTS idx_audit_log_errors
    ON system_audit_log(created_at DESC)
    WHERE severity IN ('ERROR', 'CRITICAL');

-- ─────────────────────────────────────────────────────────────────────────────
-- CIRCUIT_BREAKER_EVENTS
-- Records Resilience4j circuit breaker state transitions.
-- Populated by Resilience4j micrometer events listener (or manual inserts).
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS circuit_breaker_events (
    event_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name    VARCHAR(100) NOT NULL,
    breaker_name    VARCHAR(100) NOT NULL,       -- e.g. claimRepository, rabbitPublish
    state_from      VARCHAR(20),                 -- CLOSED, OPEN, HALF_OPEN
    state_to        VARCHAR(20),                 -- CLOSED, OPEN, HALF_OPEN
    failure_rate    FLOAT,                        -- % at time of state change
    slow_call_rate  FLOAT,
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cb_events_service  ON circuit_breaker_events(service_name);
CREATE INDEX IF NOT EXISTS idx_cb_events_breaker  ON circuit_breaker_events(breaker_name);
CREATE INDEX IF NOT EXISTS idx_cb_events_time     ON circuit_breaker_events(created_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- DLQ_MESSAGES
-- Tracks messages that landed in Dead Letter Queues.
-- Enables manual replay or investigation of failed claim events.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dlq_messages (
    dlq_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    queue_name      VARCHAR(200) NOT NULL,       -- e.g. dlq.failed_claims
    message_body    JSONB NOT NULL,
    failure_reason  TEXT,
    retry_count     INT DEFAULT 0,
    claim_id        UUID REFERENCES claims(claim_id),
    status          VARCHAR(50) DEFAULT 'PENDING'
                        CHECK (status IN ('PENDING','REPLAYED','ABANDONED','INVESTIGATING')),
    received_at     TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    resolved_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_dlq_queue    ON dlq_messages(queue_name);
CREATE INDEX IF NOT EXISTS idx_dlq_status   ON dlq_messages(status);
CREATE INDEX IF NOT EXISTS idx_dlq_claim_id ON dlq_messages(claim_id);
