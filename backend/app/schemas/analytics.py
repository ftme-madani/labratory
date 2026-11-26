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
