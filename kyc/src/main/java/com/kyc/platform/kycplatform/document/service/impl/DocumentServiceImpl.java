package com.kyc.platform.kycplatform.document.service.impl;

import com.kyc.platform.kycplatform.document.domain.Document;
import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;
import com.kyc.platform.kycplatform.document.domain.enums.VerificationStatus;
import com.kyc.platform.kycplatform.document.dto.DocumentDto;
import com.kyc.platform.kycplatform.document.dto.ExtractedData;
import com.kyc.platform.kycplatform.document.repository.DocumentRepository;
import com.kyc.platform.kycplatform.document.service.*;
import com.kyc.platform.kycplatform.onboarding.repository.KycCaseRepository;
import com.kyc.platform.kycplatform.shared.exception.ResourceNotFoundException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.time.Instant;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class DocumentServiceImpl implements DocumentService {

    private final DocumentRepository documentRepository;
    private final KycCaseRepository kycCaseRepository;
    private final FileStorageService fileStorageService;
    private final OcrService ocrService;
    private final DocumentValidationService validationService;

    @Override
    public DocumentDto uploadDocument(UUID caseId, DocumentType type, MultipartFile file) {
        var kycCase = kycCaseRepository.findById(caseId)
                .orElseThrow(() -> new ResourceNotFoundException("KYC Case", caseId));

        String documentReference = generateDocumentReference(type, caseId);
        String filePath = fileStorageService.storeFile(file, caseId, type);
        String hash = fileStorageService.computeFileHash(file);

        Document document = Document.builder()
                .documentReference(documentReference)
                .kycCase(kycCase)
                .type(type)
                .fileName(filePath.substring(filePath.lastIndexOf('/') + 1))
                .originalFileName(file.getOriginalFilename())
                .filePath(filePath)
                .mimeType(file.getContentType())
                .fileSize(file.getSize())
                .hash(hash)
                .verificationStatus(VerificationStatus.PENDING)
                .build();

        Document savedDocument = documentRepository.save(document);
        log.info("Document uploaded: {} for case: {}", documentReference, caseId);

        // Trigger async OCR processing
        processDocumentAsync(savedDocument);

        return toDto(savedDocument);
    }

    @Override
    @Transactional(readOnly = true)
    public DocumentDto getDocument(UUID documentId) {
        Document document = documentRepository.findById(documentId)
                .orElseThrow(() -> new ResourceNotFoundException("Document", documentId));
        return toDto(document);
    }

    @Override
    @Transactional(readOnly = true)
    public DocumentDto getDocumentByReference(String documentReference) {
        Document document = documentRepository.findByDocumentReference(documentReference)
                .orElseThrow(() -> new ResourceNotFoundException("Document", documentReference));
        return toDto(document);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<DocumentDto> getDocumentsByCase(UUID caseId, Pageable pageable) {
        return documentRepository.findByKycCaseId(caseId, pageable)
                .map(this::toDto);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<DocumentDto> getDocumentsByStatus(VerificationStatus status, Pageable pageable) {
        return documentRepository.findByVerificationStatus(status, pageable)
                .map(this::toDto);
    }

    @Override
    public DocumentDto verifyDocument(UUID documentId, boolean approve, String notes) {
        Document document = documentRepository.findById(documentId)
                .orElseThrow(() -> new ResourceNotFoundException("Document", documentId));

        if (approve) {
            document.markVerified(notes);
        } else {
            document.markRejected(notes);
        }

        Document savedDocument = documentRepository.save(document);
        log.info("Document {} verification: {}", documentId, approve ? "APPROVED" : "REJECTED");
        
        return toDto(savedDocument);
    }

    @Override
    public DocumentDto updateStatus(UUID documentId, VerificationStatus status) {
        Document document = documentRepository.findById(documentId)
                .orElseThrow(() -> new ResourceNotFoundException("Document", documentId));
        document.setVerificationStatus(status);
        return toDto(documentRepository.save(document));
    }

    private void processDocumentAsync(Document document) {
        // In a real application, this would be a @Async method or message queue consumer
        try {
            var extracted = ocrService.extractData(
                    fileStorageService.getFile(document.getFilePath()),
                    document.getType(),
                    document.getMimeType()
            );

            document.setExtractedData(new ObjectMapper().writeValueAsString(extracted));
            document.setOcrConfidenceScore(ocrService.getConfidenceScore());
            document.setPageCount(ocrService.getPageCount());

            // Validate extracted data
            var validationResult = validationService.validateDocument(extracted, document.getType());
            if (!validationResult.valid()) {
                document.setVerificationStatus(VerificationStatus.REJECTED);
                document.setVerificationNotes("Validation failed: " + validationResult.message());
            } else {
                document.setVerificationStatus(VerificationStatus.PROCESSING);
            }

            documentRepository.save(document);
        } catch (Exception e) {
            log.error("Document processing failed: {}", document.getId(), e);
            document.setVerificationStatus(VerificationStatus.ERROR);
            document.setVerificationNotes("Processing error: " + e.getMessage());
            documentRepository.save(document);
        }
    }

    private String generateDocumentReference(DocumentType type, UUID caseId) {
        String timestamp = String.valueOf(System.currentTimeMillis() % 100000000);
        return type.name().substring(0, 3).toUpperCase() + "-" + timestamp;
    }

    private DocumentDto toDto(Document document) {
        return DocumentDto.builder()
                .id(document.getId())
                .documentReference(document.getDocumentReference())
                .caseId(document.getKycCase().getId())
                .type(document.getType())
                .fileName(document.getFileName())
                .originalFileName(document.getOriginalFileName())
                .fileSize(document.getFileSize())
                .mimeType(document.getMimeType())
                .verificationStatus(document.getVerificationStatus())
                .verifiedAt(document.getVerifiedAt())
                .verificationNotes(document.getVerificationNotes())
                .ocrConfidenceScore(document.getOcrConfidenceScore())
                .pageCount(document.getPageCount())
                .createdAt(document.getCreatedAt())
                .updatedAt(document.getUpdatedAt())
                .build();
    }
}