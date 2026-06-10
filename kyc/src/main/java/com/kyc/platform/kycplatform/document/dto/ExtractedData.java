package com.kyc.platform.kycplatform.document.dto;

import lombok.*;

import java.time.LocalDate;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ExtractedData {

    // Common fields
    private String documentNumber;
    private String fullName;
    private LocalDate dateOfBirth;
    private String address;
    
    // Country-specific fields
    private String countryCode;
    private String nationality;
    
    // Aadhaar-specific
    private String aadhaarNumber;
    private String gender;
    
    // PAN-specific
    private String panNumber;
    private String nameOnPan;
    
    // Passport-specific
    private String passportNumber;
    private String issuingCountry;
    private LocalDate expiryDate;
    private String placeOfBirth;
    
    // Driving License
    private String dlNumber;
    private String vehicleClass;
    
    // Utility Bill
    private String providerName;
    private String billDate;
    private String consumerNumber;
}