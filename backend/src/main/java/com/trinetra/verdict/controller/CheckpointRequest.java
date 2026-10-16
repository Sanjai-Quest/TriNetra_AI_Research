package com.trinetra.verdict.controller;

import com.trinetra.verdict.model.CheckpointType;
import lombok.Data;

@Data
public class CheckpointRequest {
    private String checkpointId;
    private String clientEventId;
    private int sequenceNumber;
    private CheckpointType checkpointType;
    private String location;
    private String operatorId;
    private String capturedAt;
    private String observedSerial;
    private String observedImei;
    private String conditionStatus;

    public void setCondition(String condition) {
        if (this.conditionStatus == null || this.conditionStatus.isBlank()) {
            this.conditionStatus = condition;
        }
    }

    public String getCondition() {
        return conditionStatus;
    }
}
