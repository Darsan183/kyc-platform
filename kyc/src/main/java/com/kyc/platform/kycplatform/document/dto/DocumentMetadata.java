package com.kyc.platform.kycplatform.document.dto;

import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;
import jakarta.validation.constraints.NotNull;
import lombok.*;

import java.util.UUID;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DocumentMetadata {

    private String documentReference;
    private UUID caseId;
    private DocumentType type;
    private String fileName;
    private Long fileSize;
    private String mimeType;
    private String hash;
    private Integer pageCount;
    private ExtractedData extractedData;
    private Double ocrConfidenceScore;
}