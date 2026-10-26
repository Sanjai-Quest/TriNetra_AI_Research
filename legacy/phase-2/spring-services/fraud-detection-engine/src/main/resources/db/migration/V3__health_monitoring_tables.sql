-- ============================================================================
-- Flyway Migration: V3__health_monitoring_tables.sql
-- TriNetra AI Phase 3 — Health Monitoring & Performance Baselines
--
-- Adds tables for:
-- 1. Service health snapshots (Actuator health poll results)
-- 2. SLA performance baselines (p50/p95/p99 latency snapshots)
-- 3. Hikari pool utilization tracking
--
-- Author: TriNetra Phase 3 Hardening
-- ============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- SERVICE_HEALTH_SNAPSHOTS
-- Stores periodic Actuator /health poll results for trend analysis.
-- Populated by a monitoring cron or health check script.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS service_health_snapshots (
    snapshot_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name    VARCHAR(100) NOT NULL,
    port            INT NOT NULL,
    status          VARCHAR(20) NOT NULL CHECK (status IN ('UP','DOWN','DEGRADED','UNKNOWN')),
    db_status       VARCHAR(20),        -- from actuator health.db
    redis_status    VARCHAR(20),        -- from actuator health.redis
    rabbit_status   VARCHAR(20),        -- from actuator health.rabbit
    minio_status    VARCHAR(20),        -- from actuator health.diskSpace (proxy for MinIO)
    response_ms     INT,               -- how long the health check took
    details         JSONB,             -- raw /health response body
    checked_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_health_snapshots_service ON service_health_snapshots(service_name);
CREATE INDEX IF NOT EXISTS idx_health_snapshots_status  ON service_health_snapshots(status);
CREATE INDEX IF NOT EXISTS idx_health_snapshots_time    ON service_health_snapshots(checked_at DESC);

-- Partial index for DOWN events (alerting)
CREATE INDEX IF NOT EXISTS idx_health_snapshots_down
    ON service_health_snapshots(checked_at DESC)
    WHERE status IN ('DOWN', 'DEGRADED');

-- ─────────────────────────────────────────────────────────────────────────────
-- SLA_PERFORMANCE_BASELINES
-- Stores p50/p95/p99 latency snapshots from Micrometer/Prometheus metrics.
-- Used to track SLA degradation over time and trigger Grafana alerts.
-- Target SLAs (per implementation plan):
--   claim creation     → p95 < 2000ms
--   fraud analysis     → p95 < 5000ms
--   verdict generation → p95 < 3000ms
--   evidence upload    → p95 < 15000ms (file I/O)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sla_performance_baselines (
    baseline_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name        VARCHAR(100) NOT NULL,
    operation_name      VARCHAR(200) NOT NULL,  -- e.g. trinetra.claims.processing.duration
    window_start        TIMESTAMPTZ NOT NULL,
    window_end          TIMESTAMPTZ NOT NULL,
    sample_count        INT NOT NULL,
    p50_ms              FLOAT,
    p95_ms              FLOAT,
    p99_ms              FLOAT,
    max_ms              FLOAT,
    sla_p95_target_ms   INT,                   -- configured SLA target
    sla_breached        BOOLEAN DEFAULT FALSE, -- true if p95_ms > sla_p95_target_ms
    recorded_at         TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sla_baseline_service   ON sla_performance_baselines(service_name);
CREATE INDEX IF NOT EXISTS idx_sla_baseline_operation ON sla_performance_baselines(operation_name);
CREATE INDEX IF NOT EXISTS idx_sla_baseline_breached  ON sla_performance_baselines(sla_breached) WHERE sla_breached = TRUE;
CREATE INDEX IF NOT EXISTS idx_sla_baseline_time      ON sla_performance_baselines(recorded_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- HIKARI_POOL_SNAPSHOTS
-- Tracks connection pool utilization. Alert if active > 85% of max.
-- Populated from Micrometer hikari.* metrics scraped by Prometheus.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hikari_pool_snapshots (
    snapshot_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name        VARCHAR(100) NOT NULL,
    pool_name           VARCHAR(200) NOT NULL,
    active_connections  INT,
    idle_connections    INT,
    total_connections   INT,
    pending_threads     INT,         -- threads waiting for a connection
    max_pool_size       INT DEFAULT 20,
    utilization_pct     FLOAT,       -- active / max * 100
    recorded_at         TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_hikari_service ON hikari_pool_snapshots(service_name);
CREATE INDEX IF NOT EXISTS idx_hikari_time    ON hikari_pool_snapshots(recorded_at DESC);

-- Alert index: high utilization (>= 85%)
CREATE INDEX IF NOT EXISTS idx_hikari_high_util
    ON hikari_pool_snapshots(recorded_at DESC)
    WHERE utilization_pct >= 85.0;
