from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class TextbookRef(BaseModel):
    book: str
    grade: str
    chapter: str
    chapterNumber: int
    page: int
    curriculumCode: Optional[str] = None

class ExperimentBase(BaseModel):
    slug: str
    title: str
    subject: str
    grade: str
    difficulty: str = "متوسط"
    duration_minutes: int = 15
    summary: str
    textbook_source: Dict[str, Any]
    objectives: List[str] = Field(default_factory=list)
    safety_notes: List[str] = Field(default_factory=list)
    available_tools: List[Dict[str, Any]] = Field(default_factory=list)
    steps_config: List[Dict[str, Any]] = Field(default_factory=list)
    thumbnail_type: str = "flask"
    class_code: Optional[str] = None
    is_class_only: bool = False

class ExperimentCreate(ExperimentBase):
    status: str = "DRAFT"

class ExperimentStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(DRAFT|VERIFIED|PUBLISHED)$")

class JoinClassExperimentRequest(BaseModel):
    class_code: str
    student_name: Optional[str] = None

class TeacherFeedbackUpdate(BaseModel):
    teacher_feedback: str

class ExperimentResponse(ExperimentBase):
    id: int
    status: str
    version: int
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
