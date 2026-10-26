package ai.trinetra.claim.config;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.config.SimpleRabbitListenerContainerFactory;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Phase 3: Explicit RabbitMQ queue, exchange, and DLQ configuration.
 *
 * Replaces implicit auto-created queues from Phase 2 with:
 * - Durable queues with Dead Letter Exchange (DLX) binding
 * - TTL on messages (60s) to prevent poison-pill buildup
 * - dlq.failed_claims for messages that fail after 3 retries
 * - All queues are durable (survive broker restart)
 *
 * Queue routing:
 *   claims.input          → on 3x failure → trinetra.dlx → dlq.failed_claims
 *   evidence.uploaded     → on 3x failure → trinetra.dlx → dlq.failed_evidence
 *   evidence.processing   → on 3x failure → trinetra.dlx → dlq.failed_evidence
 *   verdict.generated     → on 3x failure → trinetra.dlx → dlq.failed_verdicts
 */
@Configuration
public class RabbitMQConfig {

    // ─── Exchange Declarations ───────────────────────────────────────────────

    /** Main topic exchange for TriNetra business events */
    @Bean
    TopicExchange trinetraExchange() {
        return new TopicExchange("trinetra.events", true, false);
    }

    /** Dead Letter Exchange — receives messages after max retries exhausted */
    @Bean
    DirectExchange deadLetterExchange() {
        return new DirectExchange("trinetra.dlx", true, false);
    }

    // ─── Main Queues (with DLX binding) ─────────────────────────────────────

    /** Primary claim ingestion queue (high priority) */
    @Bean
    Queue claimsInputQueue() {
        return QueueBuilder.durable("claims.input")
                .withArgument("x-dead-letter-exchange", "trinetra.dlx")
                .withArgument("x-dead-letter-routing-key", "dlq.failed_claims")
                .withArgument("x-message-ttl", 60000)       // 60s message TTL
                .build();
    }

    /** Evidence uploaded notification queue (medium priority) */
    @Bean
    Queue evidenceUploadedQueue() {
        return QueueBuilder.durable("evidence.uploaded")
                .withArgument("x-dead-letter-exchange", "trinetra.dlx")
                .withArgument("x-dead-letter-routing-key", "dlq.failed_evidence")
                .withArgument("x-message-ttl", 60000)
                .build();
    }

    /** Evidence processing queue (medium priority) */
    @Bean
    Queue evidenceProcessingQueue() {
        return QueueBuilder.durable("evidence.processing")
                .withArgument("x-dead-letter-exchange", "trinetra.dlx")
                .withArgument("x-dead-letter-routing-key", "dlq.failed_evidence")
                .withArgument("x-message-ttl", 60000)
                .build();
    }

    /** Verdict output queue (high priority) */
    @Bean
    Queue verdictGeneratedQueue() {
        return QueueBuilder.durable("verdict.generated")
                .withArgument("x-dead-letter-exchange", "trinetra.dlx")
                .withArgument("x-dead-letter-routing-key", "dlq.failed_verdicts")
                .withArgument("x-message-ttl", 60000)
                .build();
    }

    // ─── Dead Letter Queues (no DLX — terminal holding) ─────────────────────

    /** DLQ: failed claim messages — alerts monitoring */
    @Bean
    Queue dlqFailedClaims() {
        return QueueBuilder.durable("dlq.failed_claims").build();
    }

    /** DLQ: failed evidence messages */
    @Bean
    Queue dlqFailedEvidence() {
        return QueueBuilder.durable("dlq.failed_evidence").build();
    }

    /** DLQ: failed verdict messages */
    @Bean
    Queue dlqFailedVerdicts() {
        return QueueBuilder.durable("dlq.failed_verdicts").build();
    }

    // ─── Bindings ────────────────────────────────────────────────────────────

    @Bean Binding bindClaimsInput()      { return BindingBuilder.bind(claimsInputQueue()).to(trinetraExchange()).with("claim.created"); }
    @Bean Binding bindEvidenceUploaded() { return BindingBuilder.bind(evidenceUploadedQueue()).to(trinetraExchange()).with("evidence.uploaded"); }
    @Bean Binding bindEvidenceProcessing(){ return BindingBuilder.bind(evidenceProcessingQueue()).to(trinetraExchange()).with("evidence.processing"); }
    @Bean Binding bindVerdictGenerated() { return BindingBuilder.bind(verdictGeneratedQueue()).to(trinetraExchange()).with("verdict.generated"); }

    // DLQ bindings (to DLX, not main exchange)
    @Bean Binding bindDlqClaims()    { return BindingBuilder.bind(dlqFailedClaims()).to(deadLetterExchange()).with("dlq.failed_claims"); }
    @Bean Binding bindDlqEvidence()  { return BindingBuilder.bind(dlqFailedEvidence()).to(deadLetterExchange()).with("dlq.failed_evidence"); }
    @Bean Binding bindDlqVerdicts()  { return BindingBuilder.bind(dlqFailedVerdicts()).to(deadLetterExchange()).with("dlq.failed_verdicts"); }

    // ─── Message Converter ───────────────────────────────────────────────────

    @Bean
    Jackson2JsonMessageConverter messageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    @Bean
    RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setMessageConverter(messageConverter());
        template.setReceiveTimeout(60_000L);       // 1min
        template.setReplyTimeout(30_000L);         // 30s
        template.setExchange("trinetra.events");   // default exchange
        return template;
    }

    @Bean
    SimpleRabbitListenerContainerFactory rabbitListenerContainerFactory(
            ConnectionFactory connectionFactory) {
        SimpleRabbitListenerContainerFactory factory = new SimpleRabbitListenerContainerFactory();
        factory.setConnectionFactory(connectionFactory);
        factory.setMessageConverter(messageConverter());
        factory.setDefaultRequeueRejected(false);  // reject → DLQ (not requeue infinitely)
        factory.setPrefetchCount(10);              // prefetch 10 messages per consumer
        return factory;
    }
}
