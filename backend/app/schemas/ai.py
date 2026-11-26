from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class AITutorHintRequest(BaseModel):
    error_code: str = Field(..., description="کد خطای آزمایشگاهی تشخیص‌داده‌شده توسط موتور علمی")
    step_index: int = Field(1, ge=1, le=10, description="شماره گام در حال اجرای آزمایش")
    action_summary: Optional[str] = Field(None, description="خلاصه کنش اشتباه انجام‌شده")
    forced_level: Optional[int] = Field(None, ge=1, le=3, description="درخواست مستقیم سطح خاص از راهنما")

class AITutorHintResponse(BaseModel):
    attempt_id: str
    error_code: str
    category: str
    level: int = Field(..., ge=1, le=3, description="سطح راهنمایی (۱: تفکری، ۲: سرنخ، ۳: توضیح علمی)")
    can_escalate: bool = Field(..., description="امکان درخواست راهنمایی عمیق‌تر در صورت تکرار اشتباه")
    content: str = Field(..., description="متن راهنمایی شخصی‌سازی‌شده و آموزشی")
    scientific_rationale: Optional[str] = None
    is_ai_generated: bool = Field(True, description="آیا بازخورد با هوش مصنوعی بازآفرینی شده است")
    model_used: Optional[str] = None

class AIQuestionRequest(BaseModel):
    attempt_id: str = Field(..., description="شناسه تلاش جاری آزمایش")
    question: str = Field(..., min_length=3, max_length=500, description="پرسش علمی دانش‌آموز")
    step_index: Optional[int] = Field(1, ge=1, description="گام فعلی آزمایش")

class AIQuestionResponse(BaseModel):
    attempt_id: str
    question: str
    answer: str
    experiment_title: str
    is_ai_generated: bool = True

class TeacherAIInsightsResponse(BaseModel):
    class_code: Optional[str] = None
    total_errors_analyzed: int
    top_misconceptions: List[Dict[str, Any]]
    ai_pedagogical_remediation: str
    is_ai_generated: bool = True

class VoiceTTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="متن فارسی جهت تبدیل به صوت")
    voice: Optional[str] = Field("fa-IR-DilaraNeural", description="نام صدای فارسی مایکروسافت (Dilara یا Farid)")
    rate: Optional[str] = Field("+0%", description="نرخ سرعت صوت")
