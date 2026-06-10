package com.kyc.platform.kycplatform.onboarding.service;

import com.kyc.platform.kycplatform.onboarding.domain.Customer;
import com.kyc.platform.kycplatform.onboarding.dto.CustomerDto;
import com.kyc.platform.kycplatform.onboarding.dto.CustomerRegistrationRequest;
import com.kyc.platform.kycplatform.onboarding.repository.CustomerRepository;
import com.kyc.platform.kycplatform.shared.exception.ResourceNotFoundException;
import com.kyc.platform.kycplatform.shared.exception.ValidationException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class CustomerServiceImpl implements CustomerService {

    private final CustomerRepository customerRepository;

    @Override
    public CustomerDto registerCustomer(CustomerRegistrationRequest request) {
        validateCustomerUniqueness(request);

        var customer = Customer.builder()
                .customerReference(request.getCustomerReference())
                .firstName(request.getFirstName())
                .middleName(request.getMiddleName())
                .lastName(request.getLastName())
                .email(request.getEmail())
                .phone(request.getPhone())
                .dateOfBirth(request.getDateOfBirth())
                .nationalId(request.getNationalId())
                .passportNumber(request.getPassportNumber())
                .addressLine1(request.getAddressLine1())
                .addressLine2(request.getAddressLine2())
                .city(request.getCity())
                .state(request.getState())
                .postalCode(request.getPostalCode())
                .country(request.getCountry())
                .active(true)
                .build();

        var savedCustomer = customerRepository.save(customer);
        log.info("Customer registered: {}", savedCustomer.getCustomerReference());
        
        return CustomerDto.fromEntity(savedCustomer);
    }

    @Override
    @Transactional(readOnly = true)
    public CustomerDto getCustomer(UUID customerId) {
        var customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResourceNotFoundException("Customer", customerId));
        return CustomerDto.fromEntity(customer);
    }

    @Override
    @Transactional(readOnly = true)
    public CustomerDto getCustomerByReference(String customerReference) {
        var customer = customerRepository.findByCustomerReference(customerReference)
                .orElseThrow(() -> new ResourceNotFoundException("Customer", customerReference));
        return CustomerDto.fromEntity(customer);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<CustomerDto> searchCustomers(String searchTerm, Pageable pageable) {
        if (searchTerm == null || searchTerm.isBlank()) {
            return customerRepository.findAll(pageable)
                    .map(CustomerDto::fromEntity);
        }
        return customerRepository
                .findByFirstNameContainingIgnoreCaseOrLastNameContainingIgnoreCase(
                        searchTerm, searchTerm, pageable)
                .map(CustomerDto::fromEntity);
    }

    @Override
    public CustomerDto updateCustomer(UUID customerId, CustomerRegistrationRequest request) {
        var existingCustomer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResourceNotFoundException("Customer", customerId));

        existingCustomer.setFirstName(request.getFirstName());
        existingCustomer.setMiddleName(request.getMiddleName());
        existingCustomer.setLastName(request.getLastName());
        existingCustomer.setEmail(request.getEmail());
        existingCustomer.setPhone(request.getPhone());
        existingCustomer.setDateOfBirth(request.getDateOfBirth());
        existingCustomer.setNationalId(request.getNationalId());
        existingCustomer.setPassportNumber(request.getPassportNumber());
        existingCustomer.setAddressLine1(request.getAddressLine1());
        existingCustomer.setAddressLine2(request.getAddressLine2());
        existingCustomer.setCity(request.getCity());
        existingCustomer.setState(request.getState());
        existingCustomer.setPostalCode(request.getPostalCode());
        existingCustomer.setCountry(request.getCountry());

        var updatedCustomer = customerRepository.save(existingCustomer);
        log.info("Customer updated: {}", updatedCustomer.getCustomerReference());
        
        return CustomerDto.fromEntity(updatedCustomer);
    }

    @Override
    public void deactivateCustomer(UUID customerId) {
        var customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResourceNotFoundException("Customer", customerId));
        customer.setActive(false);
        customerRepository.save(customer);
        log.info("Customer deactivated: {}", customerId);
    }

    private void validateCustomerUniqueness(CustomerRegistrationRequest request) {
        if (customerRepository.existsByCustomerReference(request.getCustomerReference())) {
            throw new ValidationException(
                    "Customer reference already exists: " + request.getCustomerReference());
        }
        if (customerRepository.existsByEmail(request.getEmail())) {
            throw new ValidationException(
                    "Email already exists: " + request.getEmail());
        }
    }
}