package com.kyc.platform.kycplatform.onboarding.controller;

import com.kyc.platform.kycplatform.onboarding.dto.CustomerDto;
import com.kyc.platform.kycplatform.onboarding.dto.CustomerRegistrationRequest;
import com.kyc.platform.kycplatform.onboarding.service.CustomerService;
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
@RequestMapping("/api/v1/customers")
@RequiredArgsConstructor
@Tag(name = "Customers", description = "Customer management APIs")
public class CustomerController {

    private final CustomerService customerService;

    @PostMapping
    @Operation(summary = "Register new customer", description = "Create a new customer for onboarding")
    public ResponseEntity<ApiResponse<CustomerDto>> registerCustomer(
            @Valid @RequestBody CustomerRegistrationRequest request) {
        CustomerDto response = customerService.registerCustomer(request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get customer by ID", description = "Retrieve customer details")
    public ResponseEntity<ApiResponse<CustomerDto>> getCustomer(
            @PathVariable UUID id) {
        CustomerDto response = customerService.getCustomer(id);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/reference/{ref}")
    @Operation(summary = "Get customer by reference", description = "Retrieve customer by reference")
    public ResponseEntity<ApiResponse<CustomerDto>> getCustomerByReference(
            @PathVariable String ref) {
        CustomerDto response = customerService.getCustomerByReference(ref);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping
    @Operation(summary = "Search customers", description = "Search customers by name")
    public ResponseEntity<ApiResponse<Page<CustomerDto>>> searchCustomers(
            @RequestParam(required = false) String search,
            @PageableDefault(size = 20)
            @ParameterObject Pageable pageable) {
        Page<CustomerDto> response = customerService.searchCustomers(search, pageable);
        return ResponseEntity.ok(ApiResponse.success(response, pageable, response.getTotalElements()));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update customer", description = "Update customer information")
    public ResponseEntity<ApiResponse<CustomerDto>> updateCustomer(
            @PathVariable UUID id,
            @Valid @RequestBody CustomerRegistrationRequest request) {
        CustomerDto response = customerService.updateCustomer(id, request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Deactivate customer", description = "Deactivate customer account")
    public ResponseEntity<ApiResponse<Void>> deactivateCustomer(
            @PathVariable UUID id) {
        customerService.deactivateCustomer(id);
        return ResponseEntity.ok(ApiResponse.success(null));
    }
}