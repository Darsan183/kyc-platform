package com.kyc.platform.kycplatform.onboarding.service;

import com.kyc.platform.kycplatform.onboarding.dto.CustomerRegistrationRequest;
import com.kyc.platform.kycplatform.onboarding.dto.CustomerDto;
import com.kyc.platform.kycplatform.shared.exception.ResourceNotFoundException;
import com.kyc.platform.kycplatform.shared.exception.ValidationException;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.UUID;

public interface CustomerService {

    CustomerDto registerCustomer(CustomerRegistrationRequest request);

    CustomerDto getCustomer(UUID customerId);

    CustomerDto getCustomerByReference(String customerReference);

    Page<CustomerDto> searchCustomers(String searchTerm, Pageable pageable);

    CustomerDto updateCustomer(UUID customerId, CustomerRegistrationRequest request);

    void deactivateCustomer(UUID customerId);
}