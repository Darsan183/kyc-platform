package com.kyc.platform.kycplatform.document.repository;

import com.kyc.platform.kycplatform.document.domain.Document;
import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;
import com.kyc.platform.kycplatform.document.domain.enums.VerificationStatus;
import com.kyc.platform.kycplatform.infrastructure.BaseRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface DocumentRepository extends BaseRepository<Document> {

    Optional<Document> findByDocumentReference(String documentReference);

    Page<Document> findByKycCaseId(UUID caseId, Pageable pageable);

    List<Document> findByKycCaseId(UUID caseId);

    Page<Document> findByVerificationStatus(VerificationStatus status, Pageable pageable);

    List<Document> findByTypeAndKycCaseId(DocumentType type, UUID caseId);

    boolean existsByDocumentReference(String documentReference);
}