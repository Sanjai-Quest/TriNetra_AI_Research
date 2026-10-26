package ai.trinetra.claim.config;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Phase 3: Custom Micrometer business metrics for claim-service.
 *
 * All meters are exported to the Prometheus endpoint at /actuator/prometheus.
 *
 * Registered meters:
 *   trinetra.claims.ingested             - Counter: total claims created
 *   trinetra.claims.processing.duration  - Timer:   claim processing duration
 *   trinetra.claims.overrides.applied    - Counter: investigator verdict overrides
 *   trinetra.claims.bulk.imported        - Counter: claims imported via CSV
 *   trinetra.rabbitmq.publish.failures   - Counter: RabbitMQ publish failures
 *   trinetra.circuit.breaker.events      - Counter: circuit breaker state changes
 */
@Configuration
public class MetricsConfig {

    // ─── Claim Counters ──────────────────────────────────────────────────────

    @Bean
    public Counter claimsIngestedCounter(MeterRegistry registry) {
        return Counter.builder("trinetra.claims.ingested")
                .description("Total number of claims successfully created")
                .tag("service", "claim-service")
                .register(registry);
    }

    @Bean
    public Counter claimsOverridesCounter(MeterRegistry registry) {
        return Counter.builder("trinetra.claims.overrides.applied")
                .description("Total number of investigator verdict overrides")
                .tag("service", "claim-service")
                .register(registry);
    }

    @Bean
    public Counter claimsBulkImportedCounter(MeterRegistry registry) {
        return Counter.builder("trinetra.claims.bulk.imported")
                .description("Total number of claims imported via CSV bulk upload")
                .tag("service", "claim-service")
                .register(registry);
    }

    @Bean
    public Counter rabbitPublishFailuresCounter(MeterRegistry registry) {
        return Counter.builder("trinetra.rabbitmq.publish.failures")
                .description("RabbitMQ publish failures (circuit breaker events)")
                .tag("service", "claim-service")
                .register(registry);
    }

    // ─── Claim Timers ────────────────────────────────────────────────────────

    @Bean
    public Timer claimCreationTimer(MeterRegistry registry) {
        return Timer.builder("trinetra.claims.processing.duration")
                .description("Duration of claim creation including DB write and MQ publish")
                .tag("service", "claim-service")
                .publishPercentiles(0.5, 0.95, 0.99)  // expose p50, p95, p99
                .register(registry);
    }

    @Bean
    public Timer claimSearchTimer(MeterRegistry registry) {
        return Timer.builder("trinetra.claims.search.duration")
                .description("Duration of claim search queries")
                .tag("service", "claim-service")
                .publishPercentiles(0.5, 0.95, 0.99)
                .register(registry);
    }
}
