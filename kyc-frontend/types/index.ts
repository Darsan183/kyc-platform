/** Types for KYC Platform frontend */

export interface User {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  roles: string[];
  enabled: boolean;
}

export interface Customer {
  id: string;
  customerReference: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string;
  country: string;
  active: boolean;
  onboardingCompletedAt?: string;
}

export interface KycCase {
  id: string;
  caseReference: string;
  customerId: string;
  customerName: string;
  status: CaseStatus;
  riskScore?: number;
  decision?: string;
}

export enum CaseStatus {
  PENDING = "PENDING",
  IN_PROGRESS = "IN_PROGRESS",
  DOCUMENTS_PENDING = "DOCUMENTS_PENDING",
  AML_SCREENING = "AML_SCREENING",
  MEDIA_ANALYSIS = "MEDIA_ANALYSIS",
  REVIEW = "REVIEW",
  COMPLETED = "COMPLETED",
  CLOSED = "CLOSED",
  REJECTED = "REJECTED",
  ESCALATED = "ESCALATED"
}

export interface Document {
  id: string;
  documentReference: string;
  caseId: string;
  type: DocumentType;
  fileName: string;
  verificationStatus: VerificationStatus;
  ocrConfidenceScore?: number;
}

export enum DocumentType {
  PASSPORT = "PASSPORT",
  AADHAAR = "AADHAAR",
  PAN = "PAN",
  DRIVING_LICENSE = "DRIVING_LICENSE",
  UTILITY_BILL = "UTILITY_BILL"
}

export enum VerificationStatus {
  PENDING = "PENDING",
  PROCESSING = "PROCESSING",
  VERIFIED = "VERIFIED",
  REJECTED = "REJECTED",
  ERROR = "ERROR"
}

export interface RiskAssessment {
  score: number;
  level: RiskLevel;
  components: RiskComponent[];
  factors: Record<string, number>;
  explanation: string;
}

export enum RiskLevel {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical"
}

export interface RiskComponent {
  name: string;
  score: number;
  weight: number;
}

export interface AuditEvent {
  id: string;
  caseId: string;
  eventType: string;
  timestamp: string;
  actor: string;
}

export interface MonitoringAlert {
  alertId: string;
  customerId: string;
  severity: AlertSeverity;
  status: AlertStatus;
  summary: string;
  detectedAt: string;
}

export enum AlertSeverity {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical"
}

export enum AlertStatus {
  OPEN = "open",
  ACKNOWLEDGED = "acknowledged",
  IN_PROGRESS = "in_progress",
  RESOLVED = "resolved"
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: {
    code: string;
    message: string;
  };
  pagination?: {
    page: number;
    size: number;
    totalElements: number;
    totalPages: number;
  };
}

export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  userId: string;
  username: string;
  email: string;
  roles: string[];
}

export interface LoginRequest {
  username: string;
  password: string;
}