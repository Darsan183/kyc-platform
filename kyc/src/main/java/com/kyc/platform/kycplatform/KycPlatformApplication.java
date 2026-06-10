package com.kyc.platform.kycplatform;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

@SpringBootApplication
@EnableJpaAuditing
public class KycPlatformApplication {

    public static void main(String[] args) {
        SpringApplication.run(KycPlatformApplication.class, args);
    }

}