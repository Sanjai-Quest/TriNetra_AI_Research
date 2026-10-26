package ai.trinetra.claim.exception;

import io.github.resilience4j.circuitbreaker.CallNotPermittedException;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.OffsetDateTime;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.TimeoutException;
import java.util.stream.Collectors;

/**
 * Phase 3: Centralized exception handler for claim-service.
 *
 * Maps typed exceptions to clean HTTP status codes with structured error bodies.
 * Never leaks stack traces to clients. Includes trace_id for debugging.
 *
 * HTTP mapping:
 *  ClaimNotFoundException          → 404 Not Found
 *  ClaimConflictException          → 409 Conflict
 *  MethodArgumentNotValidException → 400 Bad Request
 *  CallNotPermittedException       → 503 Service Unavailable (circuit breaker open)
 *  TimeoutException                → 504 Gateway Timeout
 *  Exception (catch-all)           → 500 Internal Server Error
 */
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    // ─── 404 Not Found ──────────────────────────────────────────────────────
    @ExceptionHandler(ClaimNotFoundException.class)
    public ResponseEntity<Map<String, Object>> handleClaimNotFound(
            ClaimNotFoundException ex, HttpServletRequest request) {
        log.warn("[claim-service] ClaimNotFound: claimId={} path={}", ex.getClaimId(), request.getRequestURI());
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(errorBody("CLAIM_NOT_FOUND", ex.getMessage(), request));
    }

    // ─── 409 Conflict ───────────────────────────────────────────────────────
    @ExceptionHandler(ClaimConflictException.class)
    public ResponseEntity<Map<String, Object>> handleClaimConflict(
            ClaimConflictException ex, HttpServletRequest request) {
        log.warn("[claim-service] ClaimConflict: orderId={} path={}", ex.getOrderId(), request.getRequestURI());
        return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(errorBody("CLAIM_CONFLICT", ex.getMessage(), request));
    }

    // ─── 400 Bad Request (validation) ───────────────────────────────────────
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidation(
            MethodArgumentNotValidException ex, HttpServletRequest request) {
        String fieldErrors = ex.getBindingResult().getFieldErrors().stream()
                .map(FieldError::getDefaultMessage)
                .collect(Collectors.joining("; "));
        log.warn("[claim-service] ValidationError: {} path={}", fieldErrors, request.getRequestURI());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(errorBody("VALIDATION_ERROR", fieldErrors, request));
    }

    // ─── 503 Service Unavailable (Resilience4j circuit breaker open) ────────
    @ExceptionHandler(CallNotPermittedException.class)
    public ResponseEntity<Map<String, Object>> handleCircuitBreakerOpen(
            CallNotPermittedException ex, HttpServletRequest request) {
        log.error("[claim-service] CircuitBreakerOpen: breaker={} path={}", ex.getCausingCircuitBreakerName(), request.getRequestURI());
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(errorBody("CIRCUIT_OPEN",
                        "Service temporarily unavailable. Circuit breaker is open. Please retry in 30s.",
                        request));
    }

    // ─── 504 Gateway Timeout (Resilience4j time limiter) ────────────────────
    @ExceptionHandler(TimeoutException.class)
    public ResponseEntity<Map<String, Object>> handleTimeout(
            TimeoutException ex, HttpServletRequest request) {
        log.error("[claim-service] Timeout: path={} msg={}", request.getRequestURI(), ex.getMessage());
        return ResponseEntity.status(HttpStatus.GATEWAY_TIMEOUT)
                .body(errorBody("REQUEST_TIMEOUT", "Operation timed out. Please retry.", request));
    }

    // ─── 500 Internal Server Error (catch-all) ───────────────────────────────
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGeneral(
            Exception ex, HttpServletRequest request) {
        // Log full stack trace server-side, never send to client
        log.error("[claim-service] UnhandledException: path={}", request.getRequestURI(), ex);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(errorBody("INTERNAL_ERROR",
                        "An unexpected error occurred. Check trace_id for investigation.",
                        request));
    }

    // ─── Helper: build structured error response body ────────────────────────
    private Map<String, Object> errorBody(String code, String message, HttpServletRequest request) {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("error", code);
        body.put("message", message);
        body.put("path", request.getRequestURI());
        body.put("timestamp", OffsetDateTime.now().toString());
        // trace_id from MDC (populated by Logback/Micrometer Tracing if present)
        String traceId = (String) request.getAttribute("traceId");
        body.put("trace_id", traceId != null ? traceId : "N/A");
        return body;
    }
}
