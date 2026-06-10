package com.kyc.platform.kycplatform.document.dto;

import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;
import com.kyc.platform.kycplatform.document.domain.enums.VerificationStatus;
import lombok.*;

import java.time.Instant;
import java.util.UUID;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DocumentDto {

    private UUID id;
    private String documentReference;
    private UUID caseId;
    private DocumentType type;
    private String fileName;
    private String originalFileName;
    private Long fileSize;
    private String mimeType;
    private VerificationStatus verificationStatus;
    private Instant verifiedAt;
    private String verificationNotes;
    private Double ocrConfidenceScore;
    private Integer pageCount;
    private Instant createdAt;
    private Instant updatedAt;
}