from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class FrequentErrorStatSchema(BaseModel):
    error_code: str
    error_title: str
    experiment_title: str
    occurrence_count: int
    scientific_concept: str
    recommended_remediation: str

class ClassPerformanceStatSchema(BaseModel):
    experiment_id: int
    experiment_title: str
    total_attempts: int
    completion_rate_percent: float
    average_score_percent: float
    average_hints_used: float

class TeacherAnalyticsResponse(BaseModel):
    total_students: int
    active_experiments_count: int
    average_completion_rate: float
    frequent_errors: List[FrequentErrorStatSchema]
    experiment_stats: List[ClassPerformanceStatSchema]

class BadgeSchema(BaseModel):
    id: str
    title: str
    description: str
    icon: str
    earned_at: str

class StudentProgressResponse(BaseModel):
    completed_experiments: int
    total_attempts: int
    average_score: float
    hints_requested_total: int
    badges: List[BadgeSchema]

# Schemas for Teacher Analytics Endpoints
class AnalyticsOverviewResponse(BaseModel):
    total_attempts: int
    completed_attempts: int
    overall_success_rate: float
    active_students_count: int
    average_score: float
    total_hints_used: int
    total_errors_recorded: int

class MisconceptionItemSchema(BaseModel):
    error_code: str
    error_title: str
    experiment_title: str
    scientific_concept: str
    recommended_remediation: str
    occurrence_count: int
    percentage: float
    affected_students_count: int

class MisconceptionsResponse(BaseModel):
    total_errors: int
    misconceptions: List[MisconceptionItemSchema]

class TeacherStudentAnalyticsItem(BaseModel):
    student_id: int
    full_name: str
    email: str
    grade: Optional[str] = None
    school_name: Optional[str] = None
    class_code: Optional[str] = None
    total_attempts: int
    completed_attempts: int
    success_rate: float
    average_score: float
    errors_count: int
    hints_count: int
    last_activity: Optional[str] = None

class StudentLogItem(BaseModel):
    id: int
    attempt_id: str
    experiment_id: int
    experiment_title: str
    step_index: int
    action_type: str
    item_ids: List[str] = Field(default_factory=list)
    parameters: Optional[Dict[str, Any]] = None
    is_valid: bool
    error_code: Optional[str] = None
    error_title: Optional[str] = None
    observation_text: Optional[str] = None
    feedback_text: str
    created_at: str

class StudentLogsResponse(BaseModel):
    student_id: int
    full_name: str
    total_logs: int
    logs: List[StudentLogItem]
