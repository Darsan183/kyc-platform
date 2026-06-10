package com.kyc.platform.kycplatform.document.service;

import com.kyc.platform.kycplatform.document.dto.DocumentMetadata;
import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.util.UUID;

public interface FileStorageService {

    String storeFile(MultipartFile file, UUID caseId, DocumentType type);

    InputStream getFile(String filePath);

    void deleteFile(String filePath);

    String generateFilePath(UUID caseId, DocumentType type, String originalFileName);

    String computeFileHash(MultipartFile file);

    boolean isSupportedType(DocumentType type);

    boolean isSupportedMimeType(String mimeType);
}