package com.kyc.platform.kycplatform.onboarding.dto;

import com.kyc.platform.kycplatform.onboarding.domain.Customer;
import com.kyc.platform.kycplatform.onboarding.domain.enums.CaseStatus;
import lombok.*;

import java.time.LocalDate;
import java.time.Instant;
import java.util.UUID;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CustomerDto {

    private UUID id;
    private String customerReference;
    private String firstName;
    private String middleName;
    private String lastName;
    private String email;
    private String phone;
    private LocalDate dateOfBirth;
    private int age;
    private String addressLine1;
    private String addressLine2;
    private String city;
    private String state;
    private String postalCode;
    private String country;
    private boolean active;
    private Instant onboardingCompletedAt;
    private Instant createdAt;
    private Instant updatedAt;

    public static CustomerDto fromEntity(Customer customer) {
        return CustomerDto.builder()
                .id(customer.getId())
                .customerReference(customer.getCustomerReference())
                .firstName(customer.getFirstName())
                .middleName(customer.getMiddleName())
                .lastName(customer.getLastName())
                .email(customer.getEmail())
                .phone(customer.getPhone())
                .dateOfBirth(customer.getDateOfBirth())
                .age(customer.getAge())
                .addressLine1(customer.getAddressLine1())
                .addressLine2(customer.getAddressLine2())
                .city(customer.getCity())
                .state(customer.getState())
                .postalCode(customer.getPostalCode())
                .country(customer.getCountry())
                .active(customer.isActive())
                .onboardingCompletedAt(customer.getOnboardingCompletedAt())
                .createdAt(customer.getCreatedAt())
                .updatedAt(customer.getUpdatedAt())
                .build();
    }
}