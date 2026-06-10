-- Customer Onboarding tables migration
-- Version: V3__onboarding_tables.sql

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_reference VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    date_of_birth DATE NOT NULL,
    national_id VARCHAR(50),
    passport_number VARCHAR(50),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    onboarding_completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(100),
    updated_by VARCHAR(100)
);

-- Customer profiles table
CREATE TABLE IF NOT EXISTS customer_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL UNIQUE,
    occupation VARCHAR(100),
    employer_name VARCHAR(255),
    annual_income DECIMAL(19,2),
    source_of_funds VARCHAR(500),
    expected_transaction_volume DECIMAL(19,2),
    pep_status BOOLEAN DEFAULT FALSE,
    pep_details VARCHAR(500),
    risk_rating VARCHAR(20),
    last_verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- KYC cases table
CREATE TABLE IF NOT EXISTS kyc_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_reference VARCHAR(50) NOT NULL UNIQUE,
    customer_id UUID NOT NULL,
    status VARCHAR(30) NOT NULL,
    assigned_to UUID,
    assigned_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    risk_score INTEGER,
    decision VARCHAR(10),
    decision_reason VARCHAR(1000),
    decision_by UUID,
    decision_at TIMESTAMP WITH TIME ZONE,
    version BIGINT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_customers_ref ON customers(customer_reference);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_active ON customers(is_active);
CREATE INDEX idx_customers_name ON customers(last_name, first_name);
CREATE INDEX idx_kyc_cases_ref ON kyc_cases(case_reference);
CREATE INDEX idx_kyc_cases_customer ON kyc_cases(customer_id);
CREATE INDEX idx_kyc_cases_status ON kyc_cases(status);
CREATE INDEX idx_kyc_cases_assigned ON kyc_cases(assigned_to);
CREATE INDEX idx_kyc_cases_started ON kyc_cases(started_at DESC);
CREATE INDEX idx_customer_profiles_customer ON customer_profiles(customer_id);