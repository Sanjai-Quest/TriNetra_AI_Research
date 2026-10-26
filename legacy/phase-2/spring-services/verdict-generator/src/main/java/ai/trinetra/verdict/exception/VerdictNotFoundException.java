package ai.trinetra.verdict.exception;

public class VerdictNotFoundException extends RuntimeException {
    private final String claimId;
    public VerdictNotFoundException(String claimId) {
        super("No verdict generated yet for claim: " + claimId);
        this.claimId = claimId;
    }
    public String getClaimId() { return claimId; }
}
