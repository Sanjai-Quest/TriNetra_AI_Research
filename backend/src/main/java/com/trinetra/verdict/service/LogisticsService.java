package com.trinetra.verdict.service;

import com.trinetra.verdict.controller.*;
import com.trinetra.verdict.model.*;
import com.trinetra.verdict.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import java.util.LinkedHashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class LogisticsService {
    private final SerializedUnitRepository unitRepository;
    private final VerificationRepository verificationRepository;
    private final CheckpointRepository checkpointRepository;
    private final CustodyEventRepository custodyRepository;
    private final AuditEventRepository auditRepository;
    private final InvestigationRepository investigationRepository;
    private final EvidenceRepository evidenceRepository;
    private final VerdictService verdictService;

    @Transactional
    public Verification openVerification(CreateVerificationRequest request) {
        requireText(request.getUnitId(), "unitId");
        requireText(request.getOperatorId(), "operatorId");
        if (!unitRepository.existsById(request.getUnitId())) {
            throw new IllegalArgumentException("Serialized unit not found: " + request.getUnitId());
        }
        LocalDateTime now = LocalDateTime.now();
        Verification verification = Verification.builder()
                .verificationId(UUID.randomUUID().toString())
                .unitId(request.getUnitId())
                .operatorId(request.getOperatorId())
                .state(VerificationState.IDENTITY_PENDING)
                .createdAt(now)
                .updatedAt(now)
                .build();
        Verification saved = verificationRepository.save(verification);
        audit(saved.getVerificationId(), "VERIFICATION_OPENED", request.getOperatorId(), "{}");
        return saved;
    }

    @Transactional
    public Checkpoint submitCheckpoint(String verificationId, CheckpointRequest request) {
        Verification verification = getVerification(verificationId);
        requireText(request.getClientEventId(), "clientEventId");
        var duplicate = checkpointRepository.findByClientEventId(request.getClientEventId());
        if (duplicate.isPresent()) return duplicate.get();
        requireText(request.getCheckpointId(), "checkpointId");
        requireText(request.getOperatorId(), "operatorId");
        requireText(request.getObservedSerial(), "observedSerial");

        List<Checkpoint> previous = checkpointRepository.findByVerificationIdOrderBySequenceNumberAsc(verificationId);
        int expectedSequence = previous.size() + 1;
        if (request.getSequenceNumber() != expectedSequence) {
            throw new IllegalStateException("Checkpoint sequence must be " + expectedSequence);
        }
        SerializedUnit unit = unitRepository.findById(verification.getUnitId())
                .orElseThrow(() -> new IllegalArgumentException("Serialized unit not found"));
        Checkpoint prior = previous.isEmpty() ? null : previous.get(previous.size() - 1);
        boolean continuityBroken = prior != null && (!same(prior.getObservedSerial(), request.getObservedSerial())
                || !sameNullable(prior.getObservedImei(), request.getObservedImei()));
        Verdict verdict = verdictService.evaluateCheckpoint(unit.getExpectedSerial(), request.getObservedSerial(),
            unit.getExpectedImei(), request.getObservedImei(), request.getConditionStatus(), continuityBroken,
            request.getCheckpointId());
        if (continuityBroken) {
            verdict.setConflictType(ConflictType.CONTINUITY_BROKEN);
            verdict.setReasoning("Unit continuity broken after checkpoint " + prior.getCheckpointId()
                    + ". Expected prior identity: " + prior.getObservedSerial() + ". Observed: "
                    + request.getObservedSerial() + ". Status: HOLD.");
        }
        Checkpoint checkpoint = Checkpoint.builder()
                .checkpointId(request.getCheckpointId())
                .verificationId(verificationId)
                .sequenceNumber(request.getSequenceNumber())
                .checkpointType(request.getCheckpointType() == null ? CheckpointType.RETURN_RECEIVING : request.getCheckpointType())
                .location(request.getLocation())
                .operatorId(request.getOperatorId())
                .capturedAt(parseTime(request.getCapturedAt()))
                .expectedSerial(unit.getExpectedSerial())
                .observedSerial(request.getObservedSerial())
                .expectedImei(unit.getExpectedImei())
                .observedImei(request.getObservedImei())
                .conditionStatus(request.getConditionStatus())
                .identityResult(verdict.getDecision() == DecisionStatus.PASS ? "MATCH" : "CONFLICT")
                .decision(verdict.getDecision())
                .clientEventId(request.getClientEventId())
                .build();
        Checkpoint saved = checkpointRepository.save(checkpoint);
        verification.setState(stateFor(verdict.getDecision()));
        verification.setUpdatedAt(LocalDateTime.now());
        verificationRepository.save(verification);
        if (verdict.getDecision() == DecisionStatus.HOLD) {
            createInvestigation(verification, unit, checkpoint, prior);
        }
        audit(verificationId, "CHECKPOINT_SUBMITTED", request.getOperatorId(),
                "{\"checkpointId\":\"" + saved.getCheckpointId() + "\",\"decision\":\""
                        + saved.getDecision() + "\"}");
        return saved;
    }

    @Transactional
    public CustodyEvent recordCustody(String verificationId, CustodyRequest request) {
        Verification verification = getVerification(verificationId);
        requireText(request.getClientEventId(), "clientEventId");
        var duplicate = custodyRepository.findByClientEventId(request.getClientEventId());
        if (duplicate.isPresent()) return duplicate.get();
        requireText(request.getCheckpointId(), "checkpointId");
        requireText(request.getToActor(), "toActor");
        if (verification.getState() != VerificationState.PASS) {
            throw new IllegalStateException("Handoff blocked while verification is " + verification.getState());
        }
        if (!checkpointRepository.existsById(request.getCheckpointId())) {
            throw new IllegalArgumentException("Checkpoint not found: " + request.getCheckpointId());
        }
        CustodyEvent event = CustodyEvent.builder()
                .custodyEventId(request.getCustodyEventId() == null || request.getCustodyEventId().isBlank()
                        ? UUID.randomUUID().toString() : request.getCustodyEventId())
                .verificationId(verificationId)
                .checkpointId(request.getCheckpointId())
                .fromActor(request.getFromActor())
                .toActor(request.getToActor())
                .location(request.getLocation())
                .action(request.getAction() == null ? "HANDOFF" : request.getAction())
                .occurredAt(parseTime(request.getOccurredAt()))
                .clientEventId(request.getClientEventId())
                .build();
        CustodyEvent saved = custodyRepository.save(event);
        verification.setState(VerificationState.HANDOFF);
        verification.setUpdatedAt(LocalDateTime.now());
        verificationRepository.save(verification);
        audit(verificationId, "HANDOFF_RECORDED", request.getToActor(),
                "{\"custodyEventId\":\"" + saved.getCustodyEventId() + "\"}");
        return saved;
    }

    @Transactional
    public Verification release(String verificationId, ReleaseRequest request) {
        Verification verification = getVerification(verificationId);
        String role = request.getActorRole() == null ? "" : request.getActorRole().trim().toUpperCase(Locale.ROOT);
        if (!"SUPERVISOR".equals(role) && !"ADMIN".equals(role)) {
            throw new SecurityException("Only SUPERVISOR or ADMIN may release a verification");
        }
        if (verification.getState() != VerificationState.PASS) {
            throw new IllegalStateException("Release blocked while verification is " + verification.getState());
        }
        verification.setState(VerificationState.RELEASED);
        verification.setUpdatedAt(LocalDateTime.now());
        Verification saved = verificationRepository.save(verification);
        audit(verificationId, "RELEASE_COMPLETED", request.getActorId(), "{}");
        return saved;
    }

    public Verification getVerification(String verificationId) {
        return verificationRepository.findById(verificationId)
                .orElseThrow(() -> new IllegalArgumentException("Verification not found: " + verificationId));
    }

    public List<Verification> listVerifications() {
        return verificationRepository.findAll();
    }

    public SerializedUnit unitFor(String unitId) {
        return unitRepository.findById(unitId)
                .orElseThrow(() -> new IllegalArgumentException("Serialized unit not found: " + unitId));
    }

    public List<Checkpoint> checkpoints(String verificationId) {
        getVerification(verificationId);
        return checkpointRepository.findByVerificationIdOrderBySequenceNumberAsc(verificationId);
    }

    public List<CustodyEvent> custody(String verificationId) {
        getVerification(verificationId);
        return custodyRepository.findByVerificationIdOrderByOccurredAtAsc(verificationId);
    }

    public List<AuditEvent> audit(String verificationId) {
        getVerification(verificationId);
        return auditRepository.findByVerificationIdOrderByCreatedAtAsc(verificationId);
    }

    public List<Investigation> investigations(String verificationId) {
        getVerification(verificationId);
        return investigationRepository.findByVerificationId(verificationId).map(List::of).orElse(List.of());
    }

    @Transactional
    public Evidence recordEvidence(String verificationId, EvidenceRequest request) {
        Verification verification = getVerification(verificationId);
        requireText(request.getClientEventId(), "clientEventId");
        var duplicate = evidenceRepository.findByClientEventId(request.getClientEventId());
        if (duplicate.isPresent()) return duplicate.get();
        requireText(request.getCheckpointId(), "checkpointId");
        if (!checkpointRepository.existsById(request.getCheckpointId())) {
            throw new IllegalArgumentException("Checkpoint not found: " + request.getCheckpointId());
        }
        Evidence evidence = Evidence.builder()
                .evidenceId(request.getEvidenceId() == null || request.getEvidenceId().isBlank()
                        ? UUID.randomUUID().toString() : request.getEvidenceId())
                .verificationId(verificationId)
                .checkpointId(request.getCheckpointId())
                .type(request.getType() == null ? EvidenceType.OTHER : request.getType())
                .source(request.getSource() == null ? EvidenceSource.CAMERAX_OPENCV : request.getSource())
                .storageReference(request.getStorageReference())
                .payloadJson(request.getPayloadJson() == null ? "{}" : request.getPayloadJson())
                .capturedBy(request.getCapturedBy())
                .createdAt(parseTime(request.getCapturedAt()))
                .fileHash(request.getFileHash())
                .clientEventId(request.getClientEventId())
                .build();
        Evidence saved = evidenceRepository.save(evidence);
        audit(verificationId, "EVIDENCE_SUBMITTED", request.getCapturedBy(),
                "{\"evidenceId\":\"" + saved.getEvidenceId() + "\",\"checkpointId\":\""
                        + saved.getCheckpointId() + "\"}");
        return saved;
    }

    public List<Evidence> evidence(String verificationId) {
        getVerification(verificationId);
        return evidenceRepository.findByVerificationIdOrderByCreatedAtAsc(verificationId);
    }

    public Map<String, Object> unitHistory(String unitId) {
        SerializedUnit unit = unitFor(unitId);
        List<Map<String, Object>> verificationHistory = new java.util.ArrayList<>();
        Checkpoint firstDivergence = null;
        Checkpoint lastMatch = null;
        for (Verification verification : verificationRepository.findByUnitIdOrderByCreatedAtAsc(unitId)) {
            List<Checkpoint> checkpoints = checkpointRepository
                    .findByVerificationIdOrderBySequenceNumberAsc(verification.getVerificationId());
            for (Checkpoint checkpoint : checkpoints) {
                if (same(unit.getExpectedSerial(), checkpoint.getObservedSerial())
                        && sameNullable(unit.getExpectedImei(), checkpoint.getObservedImei())) {
                    lastMatch = checkpoint;
                } else if (firstDivergence == null) {
                    firstDivergence = checkpoint;
                }
                Map<String, Object> item = new LinkedHashMap<>();
                item.put("verificationId", verification.getVerificationId());
                item.put("checkpoint", checkpoint);
                item.put("isFirstKnownDivergence", firstDivergence == checkpoint);
                verificationHistory.add(item);
            }
        }
        Map<String, Object> history = new LinkedHashMap<>();
        history.put("unit", unit);
        history.put("checkpoints", verificationHistory);
        history.put("firstKnownDivergence", firstDivergence);
        history.put("lastKnownMatchingCheckpoint", lastMatch);
        return history;
    }

    private void audit(String verificationId, String type, String actorId, String payload) {
        auditRepository.save(AuditEvent.builder()
                .auditEventId(UUID.randomUUID().toString())
                .verificationId(verificationId)
                .eventType(type)
                .actorId(actorId == null ? "SYSTEM" : actorId)
                .payloadJson(payload)
                .createdAt(LocalDateTime.now())
                .build());
    }

        private void createInvestigation(Verification verification, SerializedUnit unit,
                         Checkpoint current, Checkpoint prior) {
        if (investigationRepository.findByVerificationId(verification.getVerificationId()).isPresent()) return;
        investigationRepository.save(Investigation.builder()
            .investigationId("INV-" + UUID.randomUUID())
            .verificationId(verification.getVerificationId())
            .unitId(unit.getUnitId())
            .status(InvestigationStatus.OPEN)
            .reason("UNIT_CONTINUITY_BROKEN")
            .expectedSerial(unit.getExpectedSerial())
            .observedSerial(current.getObservedSerial())
            .lastMatchingCheckpointId(prior == null ? null : prior.getCheckpointId())
            .firstDivergenceCheckpointId(current.getCheckpointId())
            .createdAt(LocalDateTime.now())
            .build());
        audit(verification.getVerificationId(), "INVESTIGATION_OPENED", verification.getOperatorId(),
            "{\"checkpointId\":\"" + current.getCheckpointId() + "\",\"reason\":\"UNIT_CONTINUITY_BROKEN\"}");
        }

    private VerificationState stateFor(DecisionStatus decision) {
        return switch (decision) {
            case PASS -> VerificationState.PASS;
            case HOLD -> VerificationState.HOLD;
            case REVIEW -> VerificationState.REVIEW;
        };
    }

    private LocalDateTime parseTime(String value) {
        if (value == null || value.isBlank()) return LocalDateTime.now();
        try {
            return OffsetDateTime.parse(value).toLocalDateTime();
        } catch (RuntimeException ignored) {
            return LocalDateTime.parse(value);
        }
    }

    private boolean same(String left, String right) {
        return left != null && right != null && left.trim().equalsIgnoreCase(right.trim());
    }

    private boolean sameNullable(String left, String right) {
        return left == null ? right == null : same(left, right);
    }

    private void requireText(String value, String field) {
        if (value == null || value.isBlank()) throw new IllegalArgumentException(field + " is required");
    }
}
