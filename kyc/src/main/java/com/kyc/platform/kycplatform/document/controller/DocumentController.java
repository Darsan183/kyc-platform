package com.kyc.platform.kycplatform.document.controller;

import com.kyc.platform.kycplatform.document.dto.DocumentDto;
import com.kyc.platform.kycplatform.document.domain.enums.DocumentType;
import com.kyc.platform.kycplatform.document.domain.enums.VerificationStatus;
import com.kyc.platform.kycplatform.document.service.DocumentService;
import com.kyc.platform.kycplatform.shared.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.constraints.NotNull;
import lombok.RequiredArgsConstructor;
import org.springdoc.core.annotations.ParameterObject;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/documents")
@RequiredArgsConstructor
@Tag(name = "Documents", description = "Document processing and management APIs")
public class DocumentController {

    private final DocumentService documentService;

    @PostMapping(
        consumes = MediaType.MULTIPART_FORM_DATA_VALUE,
        produces = MediaType.APPLICATION_JSON_VALUE
    )
    @Operation(
        summary = "Upload document",
        description = "Upload a document for KYC case processing"
    )
    public ResponseEntity<ApiResponse<DocumentDto>> uploadDocument(
            @NotNull @RequestParam("caseId") UUID caseId,
            @NotNull @RequestParam("type") DocumentType type,
            @NotNull @RequestParam("file") MultipartFile file) {
        DocumentDto response = documentService.uploadDocument(caseId, type, file);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/{id}")
    @Operation(
        summary = "Get document by ID",
        description = "Retrieve document details"
    )
    public ResponseEntity<ApiResponse<DocumentDto>> getDocument(
            @PathVariable UUID id) {
        DocumentDto response = documentService.getDocument(id);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/reference/{ref}")
    @Operation(
        summary = "Get document by reference",
        description = "Retrieve document by reference number"
    )
    public ResponseEntity<ApiResponse<DocumentDto>> getDocumentByReference(
            @PathVariable String ref) {
        DocumentDto response = documentService.getDocumentByReference(ref);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/case/{caseId}")
    @Operation(
        summary = "Get documents by case",
        description = "List all documents for a KYC case"
    )
    public ResponseEntity<ApiResponse<Page<DocumentDto>>> getDocumentsByCase(
            @PathVariable UUID caseId,
            @PageableDefault(size = 20)
            @ParameterObject Pageable pageable) {
        Page<DocumentDto> response = documentService.getDocumentsByCase(caseId, pageable);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/status/{status}")
    @Operation(
        summary = "Get documents by verification status",
        description = "List documents by verification status"
    )
    public ResponseEntity<ApiResponse<Page<DocumentDto>>> getDocumentsByStatus(
            @PathVariable VerificationStatus status,
            @PageableDefault(size = 20)
            @ParameterObject Pageable pageable) {
        Page<DocumentDto> response = documentService.getDocumentsByStatus(status, pageable);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/{id}/verify")
    @Operation(
        summary = "Verify document",
        description = "Approve or reject a document"
    )
    public ResponseEntity<ApiResponse<DocumentDto>> verifyDocument(
            @PathVariable UUID id,
            @RequestParam boolean approve,
            @RequestParam(required = false) String notes) {
        DocumentDto response = documentService.verifyDocument(id, approve, notes);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PatchMapping("/{id}/status")
    @Operation(
        summary = "Update document status",
        description = "Update document verification status"
    )
    public ResponseEntity<ApiResponse<DocumentDto>> updateStatus(
            @PathVariable UUID id,
            @RequestParam VerificationStatus status) {
        DocumentDto response = documentService.updateStatus(id, status);
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}