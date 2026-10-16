package com.trinetra.verdict.model;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "evidence")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Evidence {

    @Id
    @Column(name = "evidence_id", length = 36)
    private String evidenceId;

    @Column(name = "claim_id", length = 36)
    private String claimId;

    @Column(name = "verification_id", length = 64)
    private String verificationId;

    @Column(name = "checkpoint_id", length = 64)
    private String checkpointId;

    @Enumerated(EnumType.STRING)
    @Column(name = "type", length = 32)
    private EvidenceType type;

    @Column(name = "storage_reference", length = 512)
    private String storageReference;

    @Column(name = "captured_by", length = 64)
    private String capturedBy;

    @Column(name = "file_hash", length = 128)
    private String fileHash;

    @Column(name = "client_event_id", unique = true, length = 64)
    private String clientEventId;

    @Enumerated(EnumType.STRING)
    @Column(name = "source", nullable = false)
    private EvidenceSource source;

    @Column(name = "payload_json", columnDefinition = "TEXT", nullable = false)
    private String payloadJson;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
}
