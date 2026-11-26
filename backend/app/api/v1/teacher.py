from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any

from ...database import get_db
from ...models.user import User
from ...models.experiment import Experiment
from ...models.attempt import ExperimentAttempt, StepActionLog, HintUsage
from ...schemas.analytics import (
    TeacherAnalyticsResponse,
    FrequentErrorStatSchema,
    ClassPerformanceStatSchema
)
from ...schemas.experiment import TeacherFeedbackUpdate
from ..deps import require_role
from simulation_engine.hints.catalog import HINT_CATALOG

router = APIRouter(prefix="/teacher", tags=["Teacher & Pedagogical Analytics"])

@router.get("/analytics", response_model=TeacherAnalyticsResponse)
def get_teacher_macro_analytics(
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    """
    تحلیل‌های کلان پداگوژیک، آمارهای عملکرد کلاس و شایع‌ترین بدفهمی‌های علمی دانش‌آموزان
    """
    total_students = db.query(User).filter(User.role == "student").count()
    active_experiments = db.query(Experiment).filter(Experiment.status == "PUBLISHED").all()
    active_experiments_count = len(active_experiments)

    all_attempts = db.query(ExperimentAttempt).all()
    total_attempts_count = len(all_attempts)

    if total_attempts_count > 0:
        completed_count = sum(1 for a in all_attempts if a.status == "COMPLETED")
        avg_completion = round((completed_count / total_attempts_count) * 100, 1)
    else:
        avg_completion = 0.0

    # تحلیل شایع‌ترین خطاهای علمی دانش‌آموزان (Frequent Misconceptions)
    error_logs = (
        db.query(StepActionLog.error_code, func.count(StepActionLog.id).label("count"))
        .filter(StepActionLog.is_valid == False, StepActionLog.error_code.isnot(None))
        .group_by(StepActionLog.error_code)
        .order_by(func.count(StepActionLog.id).desc())
        .limit(6)
        .all()
    )

    frequent_errors: List[FrequentErrorStatSchema] = []
    for err_code, count in error_logs:
        catalog_entry = HINT_CATALOG.get(err_code)
        if catalog_entry:
            frequent_errors.append(FrequentErrorStatSchema(
                error_code=err_code,
                error_title=catalog_entry["error_title"],
                experiment_title=catalog_entry.get("experiment_title", "علوم تجربی"),
                occurrence_count=count,
                scientific_concept=catalog_entry["scientific_concept"],
                recommended_remediation=catalog_entry["remediation"]
            ))
        else:
            frequent_errors.append(FrequentErrorStatSchema(
                error_code=err_code,
                error_title=f"خطای علمی {err_code}",
                experiment_title="آزمایشگاه علوم",
                occurrence_count=count,
                scientific_concept="رعایت پیش‌نیازها و ترتیب علمی مراحل",
                recommended_remediation="بررسی دستور کار کتاب درسی پیش از اجرای آزمایش"
            ))

    # آمار به تفکیک هر آزمایش
    exp_stats: List[ClassPerformanceStatSchema] = []
    for exp in active_experiments:
        exp_attempts = [a for a in all_attempts if a.experiment_id == exp.id]
        n_attempts = len(exp_attempts)
        if n_attempts > 0:
            comp_cnt = sum(1 for a in exp_attempts if a.status == "COMPLETED")
            comp_rate = round((comp_cnt / n_attempts) * 100, 1)
            avg_sc = round(sum(a.score for a in exp_attempts) / n_attempts, 1)
            
            exp_attempt_ids = [a.id for a in exp_attempts]
            n_hints = (
                db.query(HintUsage)
                .filter(HintUsage.attempt_id.in_(exp_attempt_ids))
                .count()
            )
            avg_hints = round(n_hints / n_attempts, 1)
        else:
            comp_rate = 0.0
            avg_sc = 0.0
            avg_hints = 0.0

        exp_stats.append(ClassPerformanceStatSchema(
            experiment_id=exp.id,
            experiment_title=exp.title,
            total_attempts=n_attempts,
            completion_rate_percent=comp_rate,
            average_score_percent=avg_sc,
            average_hints_used=avg_hints
        ))

    return TeacherAnalyticsResponse(
        total_students=total_students,
        active_experiments_count=active_experiments_count,
        average_completion_rate=avg_completion,
        frequent_errors=frequent_errors,
        experiment_stats=exp_stats
    )

@router.get("/students/attempts")
def list_all_student_attempts(
    experiment_id: Optional[int] = Query(None, description="فیلتر بر اساس شناسه آزمایش"),
    status_filter: Optional[str] = Query(None, alias="status", description="وضعیت تلاش"),
    student_id: Optional[int] = Query(None, description="فیلتر بر اساس شناسه دانش‌آموز"),
    class_code: Optional[str] = Query(None, description="فیلتر بر اساس کد اختصاصی کلاس"),
    only_my_students: Optional[bool] = Query(False, description="فقط دانش‌آموزان آزمایش‌های من"),
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    """
    مشاهده گزارش کلیه تلاش‌های دانش‌آموزان به همراه جزئیات کامل نمرات، مشخصات فردی و خطاها
    """
    query = db.query(ExperimentAttempt).join(Experiment, ExperimentAttempt.experiment_id == Experiment.id)
    if experiment_id:
        query = query.filter(ExperimentAttempt.experiment_id == experiment_id)
    if status_filter:
        query = query.filter(ExperimentAttempt.status == status_filter)
    if student_id:
        query = query.filter(ExperimentAttempt.user_id == student_id)
    if class_code:
        c_code = class_code.strip()
        query = query.filter(
            (ExperimentAttempt.class_code == c_code) | (Experiment.class_code == c_code)
        )
    if only_my_students:
        query = query.filter(Experiment.created_by_id == current_user.id)

    attempts = query.order_by(ExperimentAttempt.started_at.desc()).all()

    return [
        {
            "id": a.id,
            "student_id": a.user_id,
            "student_name": a.user.full_name if a.user else "ناشناس",
            "student_grade": a.user.grade if a.user else None,
            "student_school": a.user.school_name if a.user else None,
            "experiment_id": a.experiment_id,
            "experiment_title": a.experiment.title if a.experiment else "",
            "class_code": a.class_code or (a.experiment.class_code if a.experiment else None),
            "teacher_feedback": a.teacher_feedback,
            "status": a.status,
            "score": a.score,
            "steps_completed": a.steps_completed,
            "total_steps": a.total_steps,
            "hints_count": len(a.hint_usages),
            "errors_count": sum(1 for log in a.action_logs if not log.is_valid),
            "started_at": a.started_at.isoformat(),
            "completed_at": a.completed_at.isoformat() if a.completed_at else None
        }
        for a in attempts
    ]

@router.get("/students/attempts/{attempt_id}")
def get_student_attempt_audit(
    attempt_id: str,
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    """
    مشاهده گزارش ممیزی تفصیلی لاگ‌های یک تلاش دانش‌آموز جهت عارضه‌یابی آموزشی توسط دبیر
    """
    attempt = db.query(ExperimentAttempt).filter(ExperimentAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="تلاش آزمایشگاهی مورد نظر یافت نشد."
        )

    return {
        "id": attempt.id,
        "attempt_id": attempt.id,
        "student_id": attempt.user_id,
        "student_name": attempt.user.full_name if attempt.user else "ناشناس",
        "student_grade": attempt.user.grade if attempt.user else None,
        "student_school": attempt.user.school_name if attempt.user else None,
        "experiment_id": attempt.experiment_id,
        "experiment_title": attempt.experiment.title if attempt.experiment else "",
        "class_code": attempt.class_code or (attempt.experiment.class_code if attempt.experiment else None),
        "teacher_feedback": attempt.teacher_feedback,
        "status": attempt.status,
        "score": attempt.score,
        "steps_completed": attempt.steps_completed,
        "total_steps": attempt.total_steps,
        "final_observations": attempt.final_observations,
        "started_at": attempt.started_at.isoformat(),
        "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
        "action_logs": [
            {
                "id": log.id,
                "step_index": log.step_index,
                "action_type": log.action_type,
                "item_ids": log.item_ids,
                "is_valid": log.is_valid,
                "error_code": log.error_code,
                "observation_text": log.observation_text,
                "feedback_text": log.feedback_text,
                "created_at": log.created_at.isoformat()
            }
            for log in attempt.action_logs
        ],
        "hint_usages": [
            {
                "id": hint.id,
                "step_index": hint.step_index,
                "error_code": hint.error_code,
                "hint_level": hint.hint_level,
                "hint_content": hint.hint_content,
                "created_at": hint.created_at.isoformat()
            }
            for hint in attempt.hint_usages
        ]
    }

@router.put("/students/attempts/{attempt_id}/feedback")
def update_student_attempt_feedback(
    attempt_id: str,
    feedback_in: TeacherFeedbackUpdate,
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    """
    ثبت یا ویرایش بازخورد آموزشی و نمره ارزیابی معلم برای تلاش آزمایشگاهی یک دانش‌آموز
    """
    attempt = db.query(ExperimentAttempt).filter(ExperimentAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="تلاش آزمایشگاهی مورد نظر یافت نشد."
        )

    attempt.teacher_feedback = feedback_in.teacher_feedback.strip()
    db.commit()
    db.refresh(attempt)

    return {
        "status": "success",
        "message": "بازخورد ارزیابی با موفقیت در پرونده آزمایشگاهی دانش‌آموز ثبت گردید.",
        "attempt_id": attempt.id,
        "teacher_feedback": attempt.teacher_feedback
    }

@router.get("/ai-insights")
def get_teacher_ai_insights_endpoint(
    class_code: Optional[str] = Query(None, description="فیلتر بر اساس کد کلاس مشخص"),
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    """
    دریافت تحلیل‌های هوشمند بدفهمی‌های کلاسی و توصیه‌های پداگوژیک تدریس برای دبیر
    """
    from .ai import get_teacher_ai_insights
    return get_teacher_ai_insights(class_code=class_code, current_user=current_user, db=db)

