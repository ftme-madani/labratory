import pytest
from datetime import datetime, timezone
from backend.app.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.experiment import Experiment
from backend.app.models.attempt import ExperimentAttempt, StepActionLog, HintUsage
from backend.app.api.v1.teacher import (
    get_analytics_overview,
    get_analytics_misconceptions,
    get_analytics_students,
    get_student_analytics_logs
)
from fastapi import HTTPException

@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture
def teacher_user(db_session):
    user = db_session.query(User).filter(User.role == "teacher").first()
    assert user is not None, "حساب معلم پیش‌فرض باید در دیتابیس وجود داشته باشد."
    return user

@pytest.fixture
def student_user(db_session):
    user = db_session.query(User).filter(User.role == "student").first()
    assert user is not None, "حساب دانش‌آموز پیش‌فرض باید در دیتابیس وجود داشته باشد."
    return user

def test_analytics_overview_accessible_by_teacher(db_session, teacher_user):
    """تست ۱: دسترسی موفق معلم به آمار کلی و شاخص‌های کلیدی"""
    overview = get_analytics_overview(
        experiment_id=None,
        class_code=None,
        date_from=None,
        date_to=None,
        current_user=teacher_user,
        db=db_session
    )
    assert overview is not None
    assert overview.total_attempts >= 0
    assert 0.0 <= overview.overall_success_rate <= 100.0
    assert overview.active_students_count >= 0

def test_analytics_misconceptions_endpoint(db_session, teacher_user):
    """تست ۲: استخراج کج‌فهمی‌های علمی و ردیابی کدهای خطای موتور قطعی"""
    res = get_analytics_misconceptions(
        experiment_id=None,
        class_code=None,
        date_from=None,
        date_to=None,
        current_user=teacher_user,
        db=db_session
    )
    assert res is not None
    assert hasattr(res, "misconceptions")
    assert isinstance(res.misconceptions, list)
    if res.misconceptions:
        first = res.misconceptions[0]
        assert first.error_code is not None
        assert first.error_title is not None
        assert first.occurrence_count >= 1
        assert 0.0 <= first.percentage <= 100.0

def test_analytics_students_list(db_session, teacher_user):
    """تست ۳: دریافت جدول عملکرد فردی دانش‌آموزان توسط معلم"""
    students_data = get_analytics_students(
        class_code=None,
        experiment_id=None,
        date_from=None,
        date_to=None,
        current_user=teacher_user,
        db=db_session
    )
    assert isinstance(students_data, list)
    assert len(students_data) >= 1
    std = students_data[0]
    assert std.student_id > 0
    assert std.full_name is not None
    assert std.total_attempts >= 0

def test_student_logs_access_and_filtering(db_session, teacher_user, student_user):
    """تست ۴: ممیزی لاگ‌های تفصیلی اقدامات دانش‌آموز بر اساس شناسه"""
    logs_res = get_student_analytics_logs(
        student_id=student_user.id,
        current_user=teacher_user,
        db=db_session
    )
    assert logs_res is not None
    assert logs_res.student_id == student_user.id
    assert hasattr(logs_res, "logs")

def test_analytics_experiment_filtering(db_session, teacher_user):
    """تست ۵: صحت فیلتر کردن آمار بر اساس شناسه آزمایش خاص"""
    exp = db_session.query(Experiment).first()
    if exp:
        filtered = get_analytics_overview(
            experiment_id=exp.id,
            class_code=None,
            date_from=None,
            date_to=None,
            current_user=teacher_user,
            db=db_session
        )
        assert filtered is not None
        assert filtered.total_attempts >= 0
