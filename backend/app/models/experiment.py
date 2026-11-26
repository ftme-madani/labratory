from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base

class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    subject = Column(String(50), nullable=False)     # شیمی | فیزیک | زیست
    grade = Column(String(20), nullable=False)       # هفتم | هشتم | نهم | دهم
    difficulty = Column(String(20), default="متوسط") # آسان | متوسط | پیشرفته
    duration_minutes = Column(Integer, default=15)
    status = Column(String(20), default="DRAFT", nullable=False)  # DRAFT | VERIFIED | PUBLISHED
    version = Column(Integer, default=1, nullable=False)
    summary = Column(Text, nullable=False)
    
    # فراداده منبع درسی رسمی (کتاب، فصل، صفحه، کد برنامه درسی)
    textbook_source = Column(JSON, nullable=False)
    # اهداف و نکات ایمنی
    objectives = Column(JSON, default=list)
    safety_notes = Column(JSON, default=list)
    # ابزارهای مجاز اولیه و مشخصات مراحل
    available_tools = Column(JSON, default=list)
    steps_config = Column(JSON, default=list)
    thumbnail_type = Column(String(50), default="flask")

    # اتصال به معلم سازنده و کد اختصاصی کلاس
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    class_code = Column(String(50), index=True, nullable=True)     # کد دسترسی کلاسی
    is_class_only = Column(Boolean, default=False, nullable=False) # آیا فقط برای دانش‌آموزان کلاس است؟

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    creator = relationship("User", back_populates="created_experiments")
    attempts = relationship("ExperimentAttempt", back_populates="experiment", cascade="all, delete-orphan")
