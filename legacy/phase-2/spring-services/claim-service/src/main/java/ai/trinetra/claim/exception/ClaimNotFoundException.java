package ai.trinetra.claim.exception;

/**
 * Phase 3: Typed exception for claim not found.
 * Mapped to HTTP 404 by GlobalExceptionHandler.
 * Replaces bare NoSuchElementException throws in ClaimService.
 */
public class ClaimNotFoundException extends RuntimeException {

    private final String claimId;

    public ClaimNotFoundException(String claimId) {
        super("Claim not found: " + claimId);
        this.claimId = claimId;
    }

    public String getClaimId() {
        return claimId;
    }
}
