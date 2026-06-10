package com.kyc.platform.kycplatform.onboarding.controller;

import com.kyc.platform.kycplatform.onboarding.dto.CaseAssignmentRequest;
import com.kyc.platform.kycplatform.onboarding.dto.KycCaseDto;
import com.kyc.platform.kycplatform.onboarding.dto.KycDecisionRequest;
import com.kyc.platform.kycplatform.onboarding.domain.enums.CaseStatus;
import com.kyc.platform.kycplatform.onboarding.service.KycCaseService;
import com.kyc.platform.kycplatform.shared.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springdoc.core.annotations.ParameterObject;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/cases")
@RequiredArgsConstructor
@Tag(name = "KYC Cases", description = "KYC case management APIs")
public class KycCaseController {

    private final KycCaseService kycCaseService;

    @PostMapping
    @Operation(summary = "Create KYC case", description = "Create a KYC case for a customer")
    public ResponseEntity<ApiResponse<KycCaseDto>> createCase(
            @RequestParam UUID customerId) {
        KycCaseDto response = kycCaseService.createCase(customerId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get case by ID", description = "Retrieve case details")
    public ResponseEntity<ApiResponse<KycCaseDto>> getCase(
            @PathVariable UUID id) {
        KycCaseDto response = kycCaseService.getCase(id);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/reference/{ref}")
    @Operation(summary = "Get case by reference", description = "Retrieve case by reference")
    public ResponseEntity<ApiResponse<KycCaseDto>> getCaseByReference(
            @PathVariable String ref) {
        KycCaseDto response = kycCaseService.getCaseByReference(ref);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/status/{status}")
    @Operation(summary = "Get cases by status", description = "List cases by status")
    public ResponseEntity<ApiResponse<Page<KycCaseDto>>> getCasesByStatus(
            @PathVariable CaseStatus status,
            @PageableDefault(size = 20)
            @ParameterObject Pageable pageable) {
        Page<KycCaseDto> response = kycCaseService.getCasesByStatus(status, pageable);
        return ResponseEntity.ok(ApiResponse.success(response, pageable, response.getTotalElements()));
    }

    @GetMapping("/assigned")
    @Operation(summary = "Get assigned cases", description = "List cases assigned to current user")
    public ResponseEntity<ApiResponse<Page<KycCaseDto>>> getMyAssignedCases(
            @RequestParam UUID userId,
            @PageableDefault(size = 20)
            @ParameterObject Pageable pageable) {
        Page<KycCaseDto> response = kycCaseService.getAssignedCases(userId, pageable);
        return ResponseEntity.ok(ApiResponse.success(response, pageable, response.getTotalElements()));
    }

    @PostMapping("/assign")
    @Operation(summary = "Assign case", description = "Assign case to an analyst")
    public ResponseEntity<ApiResponse<KycCaseDto>> assignCase(
            @Valid @RequestBody CaseAssignmentRequest request) {
        KycCaseDto response = kycCaseService.assignCase(request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PatchMapping("/{id}/status")
    @Operation(summary = "Update case status", description = "Update case status")
    public ResponseEntity<ApiResponse<KycCaseDto>> updateStatus(
            @PathVariable UUID id,
            @RequestParam CaseStatus status) {
        KycCaseDto response = kycCaseService.updateStatus(id, status);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/{id}/decision")
    @Operation(summary = "Make case decision", description = "Approve or reject a case")
    public ResponseEntity<ApiResponse<KycCaseDto>> makeDecision(
            @PathVariable UUID id,
            @Valid @RequestBody KycDecisionRequest request) {
        KycCaseDto response = kycCaseService.makeDecision(id, request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}