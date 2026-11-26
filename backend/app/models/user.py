from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), default="student", nullable=False)  # student | teacher | admin
    grade = Column(String(20), nullable=True)                     # هفتم | هشتم | نهم | دهم
    school_name = Column(String(150), nullable=True)
    class_code = Column(String(50), nullable=True, index=True)    # کد کلاس پیش‌فرض معلم یا کد کلاس پیوسته دانش‌آموز
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    attempts = relationship("ExperimentAttempt", back_populates="user", cascade="all, delete-orphan")
    created_experiments = relationship("Experiment", back_populates="creator")
