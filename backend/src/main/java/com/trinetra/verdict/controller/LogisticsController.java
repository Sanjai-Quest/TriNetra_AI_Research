package com.trinetra.verdict.controller;

import com.trinetra.verdict.model.*;
import com.trinetra.verdict.service.LogisticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/verifications")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class LogisticsController {
    private final LogisticsService logisticsService;

    @PostMapping
    public ResponseEntity<?> open(@RequestBody CreateVerificationRequest request) {
        try {
            return ResponseEntity.status(HttpStatus.CREATED).body(logisticsService.openVerification(request));
        } catch (IllegalArgumentException error) {
            return error(HttpStatus.BAD_REQUEST, error.getMessage());
        } catch (IllegalStateException error) {
            return error(HttpStatus.CONFLICT, error.getMessage());
        }
    }

    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> list() {
        List<Map<String, Object>> result = new java.util.ArrayList<>();
        for (Verification verification : logisticsService.listVerifications()) {
            SerializedUnit unit = logisticsService.unitFor(verification.getUnitId());
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("verificationId", verification.getVerificationId());
            item.put("unitId", verification.getUnitId());
            item.put("operatorId", verification.getOperatorId());
            item.put("state", verification.getState());
            item.put("createdAt", verification.getCreatedAt());
            item.put("updatedAt", verification.getUpdatedAt());
            item.put("product", unit.getProduct());
            item.put("sourceCaseId", unit.getSourceCaseId());
            item.put("sourcePlatform", unit.getSourcePlatform());
            item.put("sourceComplaintType", unit.getSourceComplaintType());
            result.add(item);
        }
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{verificationId}")
    public ResponseEntity<?> get(@PathVariable String verificationId) {
        try {
            return ResponseEntity.ok(logisticsService.getVerification(verificationId));
        } catch (IllegalArgumentException error) {
            return error(HttpStatus.NOT_FOUND, error.getMessage());
        }
    }

    @PostMapping("/{verificationId}/checkpoints")
    public ResponseEntity<?> checkpoint(@PathVariable String verificationId,
                                        @RequestBody CheckpointRequest request) {
        try {
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(logisticsService.submitCheckpoint(verificationId, request));
        } catch (IllegalArgumentException error) {
            return error(HttpStatus.BAD_REQUEST, error.getMessage());
        } catch (IllegalStateException error) {
            return error(HttpStatus.CONFLICT, error.getMessage());
        }
    }

    @GetMapping("/{verificationId}/checkpoints")
    public ResponseEntity<?> checkpoints(@PathVariable String verificationId) {
        try {
            return ResponseEntity.ok(logisticsService.checkpoints(verificationId));
        } catch (IllegalArgumentException error) {
            return error(HttpStatus.NOT_FOUND, error.getMessage());
        }
    }

    @PostMapping("/{verificationId}/custody")
    public ResponseEntity<?> custody(@PathVariable String verificationId,
                                     @RequestBody CustodyRequest request) {
        try {
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(logisticsService.recordCustody(verificationId, request));
        } catch (IllegalArgumentException error) {
            return error(HttpStatus.BAD_REQUEST, error.getMessage());
        } catch (IllegalStateException error) {
            return error(HttpStatus.CONFLICT, error.getMessage());
        }
    }

    @GetMapping("/{verificationId}/custody")
    public ResponseEntity<?> custody(@PathVariable String verificationId) {
        try {
            return ResponseEntity.ok(logisticsService.custody(verificationId));
        } catch (IllegalArgumentException error) {
            return error(HttpStatus.NOT_FOUND, error.getMessage());
        }
    }

    @GetMapping("/{verificationId}/audit")
    public ResponseEntity<?> audit(@PathVariable String verificationId) {
        try {
            return ResponseEntity.ok(logisticsService.audit(verificationId));
        } catch (IllegalArgumentException error) {
            return error(HttpStatus.NOT_FOUND, error.getMessage());
        }
    }

    @PostMapping("/{verificationId}/evidence")
    public ResponseEntity<?> evidence(@PathVariable String verificationId,
                                      @RequestBody EvidenceRequest request) {
        try {
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(logisticsService.recordEvidence(verificationId, request));
        } catch (IllegalArgumentException error) {
            return error(HttpStatus.BAD_REQUEST, error.getMessage());
        }
    }

    @GetMapping("/{verificationId}/evidence")
    public ResponseEntity<?> evidence(@PathVariable String verificationId) {
        try {
            return ResponseEntity.ok(logisticsService.evidence(verificationId));
        } catch (IllegalArgumentException error) {
            return error(HttpStatus.NOT_FOUND, error.getMessage());
        }
    }

    @GetMapping("/{verificationId}/investigation")
    public ResponseEntity<?> investigation(@PathVariable String verificationId) {
        try {
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("verification", logisticsService.getVerification(verificationId));
            result.put("unit", logisticsService.unitFor(logisticsService.getVerification(verificationId).getUnitId()));
            result.put("checkpoints", logisticsService.checkpoints(verificationId));
            result.put("custody", logisticsService.custody(verificationId));
            result.put("audit", logisticsService.audit(verificationId));
            result.put("evidence", logisticsService.evidence(verificationId));
            result.put("investigations", logisticsService.investigations(verificationId));
            return ResponseEntity.ok(result);
        } catch (IllegalArgumentException error) {
            return error(HttpStatus.NOT_FOUND, error.getMessage());
        }
    }

    @PostMapping("/{verificationId}/release")
    public ResponseEntity<?> release(@PathVariable String verificationId,
                                     @RequestBody ReleaseRequest request) {
        try {
            return ResponseEntity.ok(logisticsService.release(verificationId, request));
        } catch (SecurityException error) {
            return error(HttpStatus.FORBIDDEN, error.getMessage());
        } catch (IllegalArgumentException error) {
            return error(HttpStatus.NOT_FOUND, error.getMessage());
        } catch (IllegalStateException error) {
            return error(HttpStatus.CONFLICT, error.getMessage());
        }
    }

    private ResponseEntity<Map<String, String>> error(HttpStatus status, String message) {
        Map<String, String> body = new LinkedHashMap<>();
        body.put("error", status.getReasonPhrase());
        body.put("message", message);
        return ResponseEntity.status(status).body(body);
    }
}
