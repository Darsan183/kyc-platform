package com.kyc.platform.kycplatform.onboarding.repository;

import com.kyc.platform.kycplatform.infrastructure.BaseRepository;
import com.kyc.platform.kycplatform.onboarding.domain.Customer;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface CustomerRepository extends BaseRepository<Customer> {

    Optional<Customer> findByCustomerReference(String customerReference);

    Optional<Customer> findByEmail(String email);

    Page<Customer> findByFirstNameContainingIgnoreCaseOrLastNameContainingIgnoreCase(
            String firstName, String lastName, Pageable pageable);

    boolean existsByCustomerReference(String customerReference);

    boolean existsByEmail(String email);
}