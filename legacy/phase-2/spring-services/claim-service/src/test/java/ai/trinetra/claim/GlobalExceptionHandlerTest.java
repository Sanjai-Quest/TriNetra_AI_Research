package ai.trinetra.claim;

import ai.trinetra.claim.exception.ClaimConflictException;
import ai.trinetra.claim.exception.ClaimNotFoundException;
import ai.trinetra.claim.exception.GlobalExceptionHandler;
import io.github.resilience4j.circuitbreaker.CallNotPermittedException;
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import jakarta.servlet.http.HttpServletRequest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.validation.BindingResult;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;

import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeoutException;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

/**
 * Phase 3 Unit Tests for claim-service GlobalExceptionHandler.
 *
 * Test coverage:
 * 1. ClaimNotFoundException → HTTP 404 with CLAIM_NOT_FOUND code
 * 2. ClaimConflictException → HTTP 409 with CLAIM_CONFLICT code
 * 3. MethodArgumentNotValidException → HTTP 400 with VALIDATION_ERROR code
 * 4. CallNotPermittedException (circuit breaker) → HTTP 503 with CIRCUIT_OPEN code
 * 5. TimeoutException → HTTP 504 with REQUEST_TIMEOUT code
 * 6. Generic Exception → HTTP 500 with INTERNAL_ERROR code (no stack trace leaked)
 * 7. Error body contains required fields: error, message, path, timestamp, trace_id
 */
@DisplayName("Phase 3 GlobalExceptionHandler Tests")
class GlobalExceptionHandlerTest {

    private GlobalExceptionHandler handler;
    private HttpServletRequest request;

    @BeforeEach
    void setUp() {
        handler = new GlobalExceptionHandler();
        request = new MockHttpServletRequest("GET", "/api/v2/claims/test-id");
    }

    @Test
    @DisplayName("T01: ClaimNotFoundException maps to HTTP 404")
    void claimNotFound_returns404() {
        ClaimNotFoundException ex = new ClaimNotFoundException("claim-123");
        ResponseEntity<Map<String, Object>> response = handler.handleClaimNotFound(ex, request);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
        assertThat(response.getBody()).containsEntry("error", "CLAIM_NOT_FOUND");
        assertThat(response.getBody().get("message").toString()).contains("claim-123");
    }

    @Test
    @DisplayName("T02: ClaimConflictException maps to HTTP 409")
    void claimConflict_returns409() {
        ClaimConflictException ex = new ClaimConflictException("order-456");
        ResponseEntity<Map<String, Object>> response = handler.handleClaimConflict(ex, request);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CONFLICT);
        assertThat(response.getBody()).containsEntry("error", "CLAIM_CONFLICT");
        assertThat(response.getBody().get("message").toString()).contains("order-456");
    }

    @Test
    @DisplayName("T03: MethodArgumentNotValidException maps to HTTP 400")
    void validationError_returns400() {
        MethodArgumentNotValidException ex = mock(MethodArgumentNotValidException.class);
        BindingResult bindingResult = mock(BindingResult.class);
        FieldError fieldError = new FieldError("obj", "claimAmount", "must be positive");
        when(ex.getBindingResult()).thenReturn(bindingResult);
        when(bindingResult.getFieldErrors()).thenReturn(List.of(fieldError));

        ResponseEntity<Map<String, Object>> response = handler.handleValidation(ex, request);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
        assertThat(response.getBody()).containsEntry("error", "VALIDATION_ERROR");
        assertThat(response.getBody().get("message").toString()).contains("must be positive");
    }

    @Test
    @DisplayName("T04: CallNotPermittedException (circuit open) maps to HTTP 503")
    void circuitBreakerOpen_returns503() {
        CircuitBreaker cb = CircuitBreaker.of("test", CircuitBreakerConfig.ofDefaults());
        CallNotPermittedException ex = CallNotPermittedException.createCallNotPermittedException(cb);

        ResponseEntity<Map<String, Object>> response = handler.handleCircuitBreakerOpen(ex, request);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.SERVICE_UNAVAILABLE);
        assertThat(response.getBody()).containsEntry("error", "CIRCUIT_OPEN");
    }

    @Test
    @DisplayName("T05: TimeoutException maps to HTTP 504")
    void timeout_returns504() {
        TimeoutException ex = new TimeoutException("DB operation timed out");
        ResponseEntity<Map<String, Object>> response = handler.handleTimeout(ex, request);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.GATEWAY_TIMEOUT);
        assertThat(response.getBody()).containsEntry("error", "REQUEST_TIMEOUT");
    }

    @Test
    @DisplayName("T06: Generic Exception maps to HTTP 500 and does not leak stack trace")
    void genericException_returns500_noStackTrace() {
        Exception ex = new RuntimeException("Unexpected database error with sensitive info");
        ResponseEntity<Map<String, Object>> response = handler.handleGeneral(ex, request);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.INTERNAL_SERVER_ERROR);
        assertThat(response.getBody()).containsEntry("error", "INTERNAL_ERROR");
        // Ensure message does NOT contain the raw exception message (no stack trace leak)
        assertThat(response.getBody().get("message").toString())
                .doesNotContain("sensitive info")
                .doesNotContain("RuntimeException");
    }

    @Test
    @DisplayName("T07: Error body always contains required fields")
    void errorBody_containsRequiredFields() {
        ClaimNotFoundException ex = new ClaimNotFoundException("claim-xyz");
        ResponseEntity<Map<String, Object>> response = handler.handleClaimNotFound(ex, request);

        Map<String, Object> body = response.getBody();
        assertThat(body).containsKeys("error", "message", "path", "timestamp", "trace_id");
        assertThat(body.get("path").toString()).isEqualTo("/api/v2/claims/test-id");
    }
}
