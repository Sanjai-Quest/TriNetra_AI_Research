package ai.trinetra.fraud.service;

import ai.trinetra.fraud.detector.BehavioralAnomalyDetector;
import ai.trinetra.fraud.detector.SerialFraudDetector;
import ai.trinetra.fraud.detector.WardrobingDetector;
import ai.trinetra.fraud.domain.FraudSignal;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.time.OffsetDateTime;
import java.util.*;

/**
 * Phase 3 hardened FraudDetectionService.
 *
 * Changes from Phase 2:
 * 1. @CircuitBreaker + @Retry on DB queries and signal inserts (instance "fraudRepository")
 * 2. @CircuitBreaker + @Retry on Redis cache writes/reads (instance "redisCache")
 * 3. @CircuitBreaker + @Retry on RabbitMQ publish (instance "rabbitPublish")
 * 4. Micrometer counters for analysis runs and signals detected
 * 5. Explicit Redis TTL: fraud signals = 24h, customer profile = 1h
 * 6. Fallback for Redis: silently skip caching (cache is best-effort)
 * 7. Fallback for DB: throw hard failure (analysis cannot proceed without data)
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class FraudDetectionService {

    private final SerialFraudDetector serialFraudDetector;
    private final BehavioralAnomalyDetector behavioralAnomalyDetector;
    private final WardrobingDetector wardrobingDetector;
    private final JdbcTemplate jdbcTemplate;
    private final RabbitTemplate rabbitTemplate;
    private final StringRedisTemplate redisTemplate;
    private final MeterRegistry meterRegistry;

    // Lazily registered meters (avoid @Autowired on bean method here since
    // FraudDetectionService is @RequiredArgsConstructor)
    private Counter analysisRunsCounter() {
        return Counter.builder("trinetra.fraud.analysis.runs")
                .description("Fraud analysis runs completed")
                .tag("service", "fraud-detection-engine")
                .register(meterRegistry);
    }

    private Counter signalsDetectedCounter() {
        return Counter.builder("trinetra.fraud.signals.detected")
                .description("Total fraud signals detected across all analyses")
                .tag("service", "fraud-detection-engine")
                .register(meterRegistry);
    }

    // ─── Main Analysis ────────────────────────────────────────────────────────

    @Transactional
    @CircuitBreaker(name = "fraudRepository", fallbackMethod = "analyzeClaimFallback")
    @Retry(name = "fraudRepository")
    public void analyzeClaim(UUID claimId) {
        log.info("[fraud-engine] fraud.analysis.start claimId={}", claimId);

        List<Map<String, Object>> claimRows = jdbcTemplate.queryForList(
                "SELECT * FROM claims WHERE claim_id = ?", claimId
        );
        if (claimRows.isEmpty()) {
            log.warn("[fraud-engine] Claim not found for fraud analysis: {}", claimId);
            return;
        }
        Map<String, Object> claimData = claimRows.get(0);
        UUID customerId = (UUID) claimData.get("customer_id");

        List<FraudSignal> detectedSignals = new ArrayList<>();

        // 1. Serial Fraudster
        serialFraudDetector.detect(claimId, customerId).ifPresent(detectedSignals::add);

        // 2. Behavioral Anomalies
        detectedSignals.addAll(behavioralAnomalyDetector.detect(claimId, claimData));

        // 3. Wardrobing
        wardrobingDetector.detect(claimId).ifPresent(detectedSignals::add);

        // Save detected signals to DB
        for (FraudSignal sig : detectedSignals) {
            jdbcTemplate.update(
                    "INSERT INTO fraud_signals (signal_id, claim_id, signal_type, severity, confidence_score, source_evidence_id, reasoning, cross_claim_indicators, created_at) " +
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?::jsonb, CURRENT_TIMESTAMP)",
                    sig.getSignalId(), sig.getClaimId(), sig.getSignalType(), sig.getSeverity(), sig.getConfidenceScore(),
                    sig.getSourceEvidenceId(), sig.getReasoning(), sig.getCrossClaimIndicators() != null ? sig.getCrossClaimIndicators() : "{}"
            );
        }

        // Update claim status
        jdbcTemplate.update(
                "UPDATE claims SET status = 'DECISION_PENDING_REVIEW', updated_at = CURRENT_TIMESTAMP WHERE claim_id = ?",
                claimId
        );

        // Phase 3: cache fraud signals in Redis with 24h TTL
        cacheAnalysisResult(claimId, detectedSignals.size());

        analysisRunsCounter().increment();
        signalsDetectedCounter().increment(detectedSignals.size());
        log.info("[fraud-engine] fraud.analysis.complete claimId={} signals={}", claimId, detectedSignals.size());

        // Publish fraud.analysis.complete
        publishFraudAnalysisComplete(claimId, detectedSignals.size());
    }

    public void analyzeClaimFallback(UUID claimId, Throwable t) {
        log.error("[fraud-engine] analyzeClaim CIRCUIT OPEN — DB unavailable for claimId={}: {}", claimId, t.getMessage());
        throw new RuntimeException("Fraud analysis temporarily unavailable for claim: " + claimId);
    }

    // ─── Redis Cache Write ────────────────────────────────────────────────────

    @CircuitBreaker(name = "redisCache", fallbackMethod = "cacheAnalysisResultFallback")
    @Retry(name = "redisCache")
    private void cacheAnalysisResult(UUID claimId, int signalCount) {
        // 24h TTL for fraud signal counts (used by verdict-generator for fast lookup)
        redisTemplate.opsForValue().set(
                "trinetra:fraud:signals:" + claimId,
                String.valueOf(signalCount),
                Duration.ofHours(24)          // Phase 3: explicit TTL = 24h
        );
        log.debug("[fraud-engine] Redis: cached signal count for claimId={} ttl=24h", claimId);
    }

    /** Fallback: Redis unavailable — skip caching (analysis already saved to DB) */
    public void cacheAnalysisResultFallback(UUID claimId, int signalCount, Throwable t) {
        log.warn("[fraud-engine] Redis CIRCUIT OPEN — skipping cache for claimId={}: {}", claimId, t.getMessage());
        // Non-fatal: verdict-generator will fall back to DB query
    }

    // ─── RabbitMQ Publish ────────────────────────────────────────────────────

    @CircuitBreaker(name = "rabbitPublish", fallbackMethod = "publishFraudAnalysisCompleteFallback")
    @Retry(name = "rabbitPublish")
    private void publishFraudAnalysisComplete(UUID claimId, int signalCount) {
        rabbitTemplate.convertAndSend("trinetra.events", "fraud.analyzed", Map.of(
                "eventType", "fraud.analysis.complete",
                "claimId", claimId.toString(),
                "signalCount", signalCount,
                "timestamp", OffsetDateTime.now().toString()
        ));
    }

    public void publishFraudAnalysisCompleteFallback(UUID claimId, int signalCount, Throwable t) {
        log.error("[fraud-engine] RabbitMQ CIRCUIT OPEN — fraud.analysis.complete not published for claimId={}", claimId);
    }
}
