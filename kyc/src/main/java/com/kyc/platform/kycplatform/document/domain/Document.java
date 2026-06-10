package com.kyc.platform.kycplatform.document.domain;

import com.kyc.platform.kycplatform.domain.BaseEntityWithVersion;
import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;
import com.kyc.platform.kycplatform.document.domain.enums.VerificationStatus;
import com.kyc.platform.kycplatform.onboarding.domain.KycCase;
import jakarta.persistence.*;
import lombok.*;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "documents")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Document extends BaseEntityWithVersion {

    @Column(name = "document_reference", nullable = false, unique = true, length = 50)
    private String documentReference;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "case_id", nullable = false)
    private KycCase kycCase;

    @Enumerated(EnumType.STRING)
    @Column(name = "type", nullable = false, length = 30)
    private DocumentType type;

    @Column(name = "file_name", nullable = false, length = 255)
    private String fileName;

    @Column(name = "original_file_name", nullable = false, length = 255)
    private String originalFileName;

    @Column(name = "file_path", nullable = false, length = 500)
    private String filePath;

    @Column(name = "mime_type", nullable = false, length = 100)
    private String mimeType;

    @Column(name = "file_size", nullable = false)
    private Long fileSize;

    @Column(name = "hash", length = 64)
    private String hash;

    @Column(name = "verification_status", nullable = false, length = 30)
    private VerificationStatus verificationStatus;

    @Column(name = "verified_at")
    private Instant verifiedAt;

    @Column(name = "verification_notes", length = 1000)
    private String verificationNotes;

    @Column(name = "extracted_data", columnDefinition = "jsonb")
    private String extractedData;

    @Column(name = "ocr_confidence_score")
    private Double ocrConfidenceScore;

    @Column(name = "page_count")
    private Integer pageCount;

    public void markVerified(String notes) {
        this.verificationStatus = VerificationStatus.VERIFIED;
        this.verifiedAt = Instant.now();
        this.verificationNotes = notes;
    }

    public void markRejected(String notes) {
        this.verificationStatus = VerificationStatus.REJECTED;
        this.verifiedAt = Instant.now();
        this.verificationNotes = notes;
    }

    public void markPending() {
        this.verificationStatus = VerificationStatus.PENDING;
    }
}