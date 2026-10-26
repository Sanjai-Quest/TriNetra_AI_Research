package ai.trinetra.evidence.exception;

public class EvidenceNotFoundException extends RuntimeException {
    private final String evidenceId;
    public EvidenceNotFoundException(String evidenceId) {
        super("Evidence not found: " + evidenceId);
        this.evidenceId = evidenceId;
    }
    public String getEvidenceId() { return evidenceId; }
}
