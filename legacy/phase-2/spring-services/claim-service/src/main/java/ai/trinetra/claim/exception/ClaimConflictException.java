package ai.trinetra.claim.exception;

/**
 * Phase 3: Raised when attempting to create a claim for an order that already
 * has an active claim. Mapped to HTTP 409 Conflict by GlobalExceptionHandler.
 */
public class ClaimConflictException extends RuntimeException {

    private final String orderId;

    public ClaimConflictException(String orderId) {
        super("Active claim already exists for order: " + orderId);
        this.orderId = orderId;
    }

    public String getOrderId() {
        return orderId;
    }
}
