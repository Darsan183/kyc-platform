package com.kyc.platform.kycplatform.onboarding.service;

import com.kyc.platform.kycplatform.onboarding.domain.Customer;
import com.kyc.platform.kycplatform.onboarding.dto.CustomerRegistrationRequest;
import com.kyc.platform.kycplatform.onboarding.repository.CustomerRepository;
import com.kyc.platform.kycplatform.shared.exception.ResourceNotFoundException;
import com.kyc.platform.kycplatform.shared.exception.ValidationException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDate;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CustomerServiceTest {

    @Mock
    private CustomerRepository customerRepository;

    @InjectMocks
    private CustomerServiceImpl customerService;

    private CustomerRegistrationRequest validRequest;

    @BeforeEach
    void setUp() {
        validRequest = CustomerRegistrationRequest.builder()
                .customerReference("CUST-001")
                .firstName("John")
                .lastName("Doe")
                .email("john.doe@example.com")
                .phone("+1234567890")
                .dateOfBirth(LocalDate.of(1990, 1, 1))
                .addressLine1("123 Main St")
                .city("New York")
                .postalCode("10001")
                .country("US")
                .build();
    }

    @Test
    void shouldRegisterCustomerSuccessfully() {
        when(customerRepository.existsByCustomerReference(any())).thenReturn(false);
        when(customerRepository.existsByEmail(any())).thenReturn(false);
        when(customerRepository.save(any())).thenAnswer(inv -> {
            Customer c = inv.getArgument(0);
            c.setId(UUID.randomUUID());
            return c;
        });

        var result = customerService.registerCustomer(validRequest);

        assertNotNull(result);
        assertEquals(validRequest.getCustomerReference(), result.getCustomerReference());
        assertEquals(validRequest.getEmail(), result.getEmail());
        verify(customerRepository).save(any());
    }

    @Test
    void shouldThrowExceptionWhenReferenceExists() {
        when(customerRepository.existsByCustomerReference("CUST-001")).thenReturn(true);

        assertThrows(ValidationException.class, 
                () -> customerService.registerCustomer(validRequest));
        verify(customerRepository, never()).save(any());
    }

    @Test
    void shouldThrowExceptionWhenEmailExists() {
        when(customerRepository.existsByCustomerReference(any())).thenReturn(false);
        when(customerRepository.existsByEmail(any())).thenReturn(true);

        assertThrows(ValidationException.class, 
                () -> customerService.registerCustomer(validRequest));
        verify(customerRepository, never()).save(any());
    }

    @Test
    void shouldGetCustomerById() {
        UUID customerId = UUID.randomUUID();
        Customer customer = Customer.builder()
                .id(customerId)
                .customerReference("CUST-001")
                .build();
        
        when(customerRepository.findById(customerId)).thenReturn(Optional.of(customer));

        var result = customerService.getCustomer(customerId);

        assertNotNull(result);
        assertEquals(customerId, result.getId());
    }

    @Test
    void shouldThrowWhenCustomerNotFound() {
        UUID customerId = UUID.randomUUID();
        when(customerRepository.findById(customerId)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, 
                () -> customerService.getCustomer(customerId));
    }
}