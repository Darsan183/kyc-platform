package com.kyc.platform.kycplatform.onboarding;

import com.kyc.platform.kycplatform.onboarding.dto.CustomerRegistrationRequest;
import com.kyc.platform.kycplatform.onboarding.repository.CustomerRepository;
import com.kyc.platform.kycplatform.onboarding.service.CustomerService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@Transactional
class CustomerOnboardingIntegrationTest {

    @Autowired(required = false)
    private CustomerService customerService;

    @Autowired(required = false)
    private CustomerRepository customerRepository;

    @Test
    void contextLoads() {
        // Basic context test
        assertNotNull(customerService);
    }
}