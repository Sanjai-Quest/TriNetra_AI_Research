package com.trinetra.verdict.repository;

import com.trinetra.verdict.model.Evidence;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface EvidenceRepository extends JpaRepository<Evidence, String> {
    List<Evidence> findByClaimId(String claimId);
    List<Evidence> findByVerificationIdOrderByCreatedAtAsc(String verificationId);
    Optional<Evidence> findByClientEventId(String clientEventId);
}
