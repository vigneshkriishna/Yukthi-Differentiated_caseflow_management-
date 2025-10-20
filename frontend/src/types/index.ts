// User types
export enum UserRole {
  ADMIN = 'admin',
  JUDGE = 'judge',
  CLERK = 'clerk',
  LAWYER = 'lawyer',
  PUBLIC = 'public',
}

export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  created_at: string
  updated_at?: string
}

// Case types
export enum CaseType {
  CRIMINAL = 'criminal',
  CIVIL = 'civil',
  FAMILY = 'family',
  COMMERCIAL = 'commercial',
  CONSTITUTIONAL = 'constitutional',
}

export enum CaseStatus {
  FILED = 'filed',
  UNDER_REVIEW = 'under_review',
  SCHEDULED = 'scheduled',
  HEARING = 'hearing',
  JUDGMENT_RESERVED = 'judgment_reserved',
  DISPOSED = 'disposed',
  APPEALED = 'appealed',
}

export enum CaseTrack {
  FAST = 'fast',
  REGULAR = 'regular',
  COMPLEX = 'complex',
}

export enum CasePriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
}

export interface Case {
  id: number
  case_number: string
  title: string
  case_type: CaseType
  synopsis: string
  filing_date: string
  status: CaseStatus
  priority: CasePriority
  estimated_duration_minutes: number
  track?: CaseTrack
  track_score?: number
  track_reasons?: string
  is_track_overridden: boolean
  override_reason?: string
  override_by_user_id?: number
  override_at?: string
  assigned_clerk_id?: number
  assigned_bench_id?: number
  suggested_laws?: string
  created_at: string
  updated_at?: string
  assigned_clerk?: User
  assigned_bench?: Bench
  hearings?: Hearing[]
}

// Bench types
export interface Bench {
  id: number
  name: string
  court_number: string
  capacity: number
  is_active: boolean
  created_at: string
  updated_at?: string
}

// Hearing types
export interface Hearing {
  id: number
  case_id: number
  bench_id: number
  judge_id?: number
  scheduled_date: string
  scheduled_time?: string
  duration_minutes: number
  status: string
  notes?: string
  created_at: string
  updated_at?: string
  case?: Case
  bench?: Bench
  judge?: User
}

// Audit types
export enum AuditAction {
  CREATE_USER = 'create_user',
  UPDATE_USER = 'update_user',
  DELETE_USER = 'delete_user',
  CREATE_CASE = 'create_case',
  UPDATE_CASE = 'update_case',
  DELETE_CASE = 'delete_case',
  CLASSIFY_CASE = 'classify_case',
  OVERRIDE_TRACK = 'override_track',
  CREATE_HEARING = 'create_hearing',
  UPDATE_HEARING = 'update_hearing',
  DELETE_HEARING = 'delete_hearing',
  SCHEDULE_HEARING = 'schedule_hearing',
  VIEW_CASE = 'view_case',
  EXPORT_REPORT = 'export_report',
  LOGIN = 'login',
  LOGOUT = 'logout',
}

export interface AuditLog {
  id: number
  user_id: number
  action: AuditAction
  resource_type: string
  resource_id: string
  details: Record<string, any>
  timestamp: string
  user?: User
}

// API Response types
export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface CreateCaseRequest {
  case_number: string
  title: string
  case_type: CaseType
  synopsis: string
  filing_date: string
  priority: CasePriority
  estimated_duration_minutes: number
  assigned_clerk_id?: number
}

export interface UpdateCaseRequest {
  title?: string
  synopsis?: string
  status?: CaseStatus
  priority?: CasePriority
  estimated_duration_minutes?: number
  assigned_clerk_id?: number
  assigned_bench_id?: number
}

export interface CaseClassificationResult {
  case_id: number
  track: CaseTrack
  score: number
  reasons: string[]
  confidence: number
}

export interface CaseOverrideRequest {
  new_track: CaseTrack
  reason: string
}

export interface ScheduleAllocationRequest {
  start_date: string
  num_days: number
}

export interface CreateUserRequest {
  username: string
  email: string
  full_name: string
  role: UserRole
  password: string
}

export interface UpdateUserRequest {
  username?: string
  email?: string
  full_name?: string
  role?: UserRole
  is_active?: boolean
}

// Dashboard types
export interface DashboardMetrics {
  total_cases: number
  active_cases: number
  scheduled_hearings: number
  pending_classification: number
  cases_by_status: Record<CaseStatus, number>
  cases_by_type: Record<CaseType, number>
  cases_by_track: Record<CaseTrack, number>
  recent_activity: AuditLog[]
  upcoming_hearings: Hearing[]
}

// Reports types
export interface ReportMetrics {
  case_statistics: {
    total: number
    by_status: Record<CaseStatus, number>
    by_type: Record<CaseType, number>
    by_priority: Record<CasePriority, number>
  }
  hearing_statistics: {
    total: number
    scheduled: number
    completed: number
    average_duration: number
  }
  performance_metrics: {
    avg_case_resolution_days: number
    scheduling_efficiency: number
    classification_accuracy: number
  }
}

// NLP types
export interface BNSSuggestion {
  section: string
  title: string
  description: string
  relevance_score: number
  reasoning: string
}

export interface NLPAnalysisRequest {
  text: string
  case_type?: CaseType
}

export interface NLPAnalysisResponse {
  suggestions: BNSSuggestion[]
  keywords: string[]
  sentiment: {
    score: number
    label: string
  }
  complexity_score: number
}

// UI types
export interface SelectOption {
  value: string
  label: string
}

export interface TableColumn {
  key: string
  title: string
  sortable?: boolean
  render?: (value: any, record: any) => React.ReactNode
}

export interface PaginationInfo {
  page: number
  per_page: number
  total: number
  total_pages: number
}

export interface ApiResponse<T> {
  data: T
  message?: string
  pagination?: PaginationInfo
}

// Error types
export interface ApiError {
  error: boolean
  status_code: number
  message: string
  error_code?: string
  details?: any
  path?: string
  timestamp?: string
}

// Filter types
export interface CaseFilters {
  status?: CaseStatus
  priority?: CasePriority
  case_type?: CaseType
  track?: CaseTrack
  search?: string
  filing_date_from?: string
  filing_date_to?: string
  assigned_clerk_id?: number
  assigned_bench_id?: number
}

export interface HearingFilters {
  status?: string
  bench_id?: number
  judge_id?: number
  date_from?: string
  date_to?: string
  case_id?: number
}

// Additional request types
export interface CreateHearingRequest {
  case_id: number
  bench_id: number
  judge_id?: number
  scheduled_date: string
  scheduled_time?: string
  duration_minutes: number
  notes?: string
}

export interface UpdateHearingRequest {
  bench_id?: number
  judge_id?: number
  scheduled_date?: string
  scheduled_time?: string
  duration_minutes?: number
  status?: string
  notes?: string
}
