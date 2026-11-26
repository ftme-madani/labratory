from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base

class ExperimentAttempt(Base):
    __tablename__ = "experiment_attempts"

    id = Column(String(50), primary_key=True, index=True)  # e.g., att-1730000000
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    
    status = Column(String(20), default="IN_PROGRESS", nullable=False) # IN_PROGRESS | COMPLETED | FAILED
    score = Column(Float, default=100.0, nullable=False)
    steps_completed = Column(Integer, default=0, nullable=False)
    total_steps = Column(Integer, default=3, nullable=False)
    
    final_observations = Column(JSON, default=list)
    final_measurements = Column(JSON, default=dict)

    class_code = Column(String(50), nullable=True, index=True)      # کد کلاس مرتبط با تلاش
    teacher_feedback = Column(Text, nullable=True)                  # بازخورد ارزیابی معلم

    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="attempts")
    experiment = relationship("Experiment", back_populates="attempts")
    action_logs = relationship("StepActionLog", back_populates="attempt", cascade="all, delete-orphan", order_by="StepActionLog.id")
    hint_usages = relationship("HintUsage", back_populates="attempt", cascade="all, delete-orphan", order_by="HintUsage.id")

class StepActionLog(Base):
    __tablename__ = "step_action_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    attempt_id = Column(String(50), ForeignKey("experiment_attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    step_index = Column(Integer, nullable=False)
    action_type = Column(String(50), nullable=False)
    item_ids = Column(JSON, default=list)
    parameters = Column(JSON, default=dict, nullable=True)
    is_valid = Column(Boolean, default=True, nullable=False)
    error_code = Column(String(100), nullable=True)
    observation_text = Column(Text, nullable=True)
    feedback_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    attempt = relationship("ExperimentAttempt", back_populates="action_logs")

class HintUsage(Base):
    __tablename__ = "hint_usages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    attempt_id = Column(String(50), ForeignKey("experiment_attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    step_index = Column(Integer, nullable=False)
    error_code = Column(String(100), nullable=False)
    hint_level = Column(Integer, nullable=False) # 1, 2, 3
    hint_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    attempt = relationship("ExperimentAttempt", back_populates="hint_usages")
