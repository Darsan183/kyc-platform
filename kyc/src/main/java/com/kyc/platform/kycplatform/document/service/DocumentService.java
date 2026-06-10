package com.kyc.platform.kycplatform.document.service;

import com.kyc.platform.kycplatform.document.dto.DocumentDto;
import com.kyc.platform.kycplatform.document.dto.DocumentMetadata;
import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;
import com.kyc.platform.kycplatform.document.domain.enums.VerificationStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.web.multipart.MultipartFile;

import java.util.UUID;

public interface DocumentService {

    DocumentDto uploadDocument(UUID caseId, DocumentType type, MultipartFile file);

    DocumentDto getDocument(UUID documentId);

    DocumentDto getDocumentByReference(String documentReference);

    Page<DocumentDto> getDocumentsByCase(UUID caseId, Pageable pageable);

    Page<DocumentDto> getDocumentsByStatus(VerificationStatus status, Pageable pageable);

    DocumentDto verifyDocument(UUID documentId, boolean approve, String notes);

    DocumentDto updateStatus(UUID documentId, VerificationStatus status);
}