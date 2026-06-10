package com.kyc.platform.kycplatform.onboarding.repository;

import com.kyc.platform.kycplatform.infrastructure.BaseRepository;
import com.kyc.platform.kycplatform.onboarding.domain.KycCase;
import com.kyc.platform.kycplatform.onboarding.domain.enums.CaseStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface KycCaseRepository extends BaseRepository<KycCase> {

    Optional<KycCase> findByCaseReference(String caseReference);

    Page<KycCase> findByCustomerId(UUID customerId, Pageable pageable);

    Page<KycCase> findByStatus(CaseStatus status, Pageable pageable);

    List<KycCase> findByAssignedToAndStatus(UUID assignedTo, CaseStatus status);

    Page<KycCase> findByAssignedTo(UUID assignedTo, Pageable pageable);

    boolean existsByCaseReference(String caseReference);
}