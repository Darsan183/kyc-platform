package com.kyc.platform.kycplatform.document.service.impl;

import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;
import com.kyc.platform.kycplatform.document.dto.DocumentMetadata;
import com.kyc.platform.kycplatform.document.service.FileStorageService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.*;

@Service
@Slf4j
public class FileStorageServiceImpl implements FileStorageService {

    private final String storageRoot;
    private final Set<String> supportedMimeTypes;

    public FileStorageServiceImpl(
            @Value("${app.document.storage.root:./documents}") String storageRoot) {
        this.storageRoot = storageRoot;
        this.supportedMimeTypes = Set.of(
                "application/pdf",
                "image/jpeg",
                "image/png",
                "image/tiff",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        );
        initializeStorage();
    }

    private void initializeStorage() {
        try {
            Path rootPath = Paths.get(storageRoot);
            if (!Files.exists(rootPath)) {
                Files.createDirectories(rootPath);
            }
        } catch (IOException e) {
            log.error("Failed to initialize document storage", e);
        }
    }

    @Override
    public String storeFile(MultipartFile file, UUID caseId, DocumentType type) {
        try {
            String filePath = generateFilePath(caseId, type, file.getOriginalFilename());
            Path path = Paths.get(filePath);
            Files.createDirectories(path.getParent());
            
            try (InputStream in = file.getInputStream();
                 FileOutputStream out = new FileOutputStream(path.toFile())) {
                byte[] buffer = new byte[8192];
                int bytesRead;
                while ((bytesRead = in.read(buffer)) != -1) {
                    out.write(buffer, 0, bytesRead);
                }
            }
            
            log.info("Stored document: {}", filePath);
            return filePath;
        } catch (IOException e) {
            log.error("Failed to store document", e);
            throw new RuntimeException("Failed to store document: " + e.getMessage());
        }
    }

    @Override
    public InputStream getFile(String filePath) {
        try {
            return Files.newInputStream(Paths.get(filePath));
        } catch (IOException e) {
            log.error("Failed to retrieve document: {}", filePath, e);
            throw new RuntimeException("Document not found: " + filePath);
        }
    }

    @Override
    public void deleteFile(String filePath) {
        try {
            Files.deleteIfExists(Paths.get(filePath));
        } catch (IOException e) {
            log.error("Failed to delete document: {}", filePath, e);
        }
    }

    @Override
    public String generateFilePath(UUID caseId, DocumentType type, String originalFileName) {
        String extension = getFileExtension(originalFileName);
        String timestamp = String.valueOf(System.currentTimeMillis());
        String uniqueId = UUID.randomUUID().toString().substring(0, 8);
        
        return storageRoot + "/" + caseId + "/" + type.name().toLowerCase() + 
                "/" + timestamp + "_" + uniqueId + extension;
    }

    @Override
    public String computeFileHash(MultipartFile file) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] buffer = new byte[8192];
            int bytesRead;
            
            try (InputStream in = file.getInputStream()) {
                while ((bytesRead = in.read(buffer)) != -1) {
                    md.update(buffer, 0, bytesRead);
                }
            }
            
            byte[] digest = md.digest();
            return new BigInteger(1, digest).toString(16);
        } catch (Exception e) {
            log.error("Failed to compute file hash", e);
            return null;
        }
    }

    @Override
    public boolean isSupportedType(DocumentType type) {
        return Set.of(DocumentType.values()).contains(type);
    }

    @Override
    public boolean isSupportedMimeType(String mimeType) {
        return supportedMimeTypes.contains(mimeType.toLowerCase());
    }

    private String getFileExtension(String fileName) {
        int dotIndex = fileName.lastIndexOf('.');
        return (dotIndex > 0) ? fileName.substring(dotIndex) : "";
    }
}