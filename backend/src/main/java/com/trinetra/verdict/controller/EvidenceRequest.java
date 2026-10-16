package com.trinetra.verdict.controller;

import com.trinetra.verdict.model.EvidenceSource;
import com.trinetra.verdict.model.EvidenceType;
import lombok.Data;

@Data
public class EvidenceRequest {
    private String evidenceId;
    private String clientEventId;
    private String checkpointId;
    private EvidenceType type;
    private EvidenceSource source;
    private String storageReference;
    private String payloadJson;
    private String capturedBy;
    private String capturedAt;
    private String fileHash;
}
