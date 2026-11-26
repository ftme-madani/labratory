from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from sqlalchemy import func

from ...database import get_db
from ...models.user import User
from ...models.attempt import ExperimentAttempt, HintUsage, StepActionLog
from ...schemas.analytics import StudentProgressResponse, BadgeSchema
from ..deps import get_current_user

router = APIRouter(prefix="/student", tags=["Student Learning Analytics"])

@router.get("/progress", response_model=StudentProgressResponse)
def get_student_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    محاسبه پیشرفت تحصیلی، نرخ موفقیت و مدال‌های شایستگی دانش‌آموز جاری
    """
    attempts = db.query(ExperimentAttempt).filter(ExperimentAttempt.user_id == current_user.id).all()
    total_attempts = len(attempts)
    
    completed_attempts = [a for a in attempts if a.status == "COMPLETED"]
    completed_exp_ids = set(a.experiment_id for a in completed_attempts)
    completed_experiments_count = len(completed_exp_ids)

    if total_attempts > 0:
        avg_score = round(sum(a.score for a in attempts) / total_attempts, 1)
    else:
        avg_score = 0.0

    # شمارش مجموع راهنماهای استفاده‌شده
    attempt_ids = [a.id for a in attempts]
    hints_count = (
        db.query(HintUsage)
        .filter(HintUsage.attempt_id.in_(attempt_ids))
        .count()
        if attempt_ids else 0
    )

    # سیستم نشان‌ها و مدال‌های پداگوژیک (Badges)
    badges: List[BadgeSchema] = []
    
    if completed_experiments_count >= 1:
        badges.append(BadgeSchema(
            id="badge-first-step",
            title="نخستین کاوشگر",
            description="انجام موفقیت‌آمیز اولین آزمایش علمی در لابراتوار مجازی",
            icon="award",
            earned_at=completed_attempts[0].completed_at.strftime("%Y/%m/%d") if completed_attempts[0].completed_at else "امروز"
        ))

    high_score_attempts = [a for a in completed_attempts if a.score >= 90.0]
    if high_score_attempts:
        badges.append(BadgeSchema(
            id="badge-precision",
            title="پژوهشگر دقیق",
            description="دستیابی به نمره بالاتر از ۹۰ بدون خطای اساسی در فرایند آزمایشگاهی",
            icon="zap",
            earned_at=high_score_attempts[0].completed_at.strftime("%Y/%m/%d") if high_score_attempts[0].completed_at else "امروز"
        ))

    if total_attempts >= 3:
        badges.append(BadgeSchema(
            id="badge-persistent",
            title="دانشمند مصمم",
            description="پشتکار در اجرای بیش از ۳ تلاش برای یادگیری عمیق مفاهیم",
            icon="star",
            earned_at="امروز"
        ))

    # مدال شیمی در صورت تکمیل آزمایش اسید و باز
    for ca in completed_attempts:
        if ca.experiment and "acid" in ca.experiment.slug:
            badges.append(BadgeSchema(
                id="badge-chemist",
                title="شیمی‌دان نوجوان",
                description="تسلط بر شناسایی ویژگی‌های اسیدها و بازها با معرف‌های رنگی",
                icon="flame",
                earned_at=ca.completed_at.strftime("%Y/%m/%d") if ca.completed_at else "امروز"
            ))
            break

    return StudentProgressResponse(
        completed_experiments=completed_experiments_count,
        total_attempts=total_attempts,
        average_score=avg_score,
        hints_requested_total=hints_count,
        badges=badges
    )

@router.get("/attempts")
def list_student_attempts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    فهرست تمام تلاش‌های پیشین دانش‌آموز جاری با جزئیات نمرات و تاریخ
    """
    attempts = (
        db.query(ExperimentAttempt)
        .filter(ExperimentAttempt.user_id == current_user.id)
        .order_by(ExperimentAttempt.started_at.desc())
        .all()
    )

    return [
        {
            "id": a.id,
            "experiment_id": a.experiment_id,
            "experiment_slug": a.experiment.slug if a.experiment else "",
            "experiment_title": a.experiment.title if a.experiment else "",
            "grade": a.experiment.grade if a.experiment else "",
            "subject": a.experiment.subject if a.experiment else "",
            "status": a.status,
            "score": a.score,
            "steps_completed": a.steps_completed,
            "total_steps": a.total_steps,
            "started_at": a.started_at.isoformat(),
            "completed_at": a.completed_at.isoformat() if a.completed_at else None,
            "action_logs_count": len(a.action_logs),
            "hints_count": len(a.hint_usages)
        }
        for a in attempts
    ]

@router.get("/attempts/{attempt_id}")
def get_student_attempt_detail(
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    مشاهده گزارش تفصیلی یک تلاش آزمایشگاهی شامل وقایع و راهنماهای دریافتی
    """
    attempt = db.query(ExperimentAttempt).filter(ExperimentAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="تلاش آزمایشگاهی مورد نظر یافت نشد."
        )

    if attempt.user_id != current_user.id and current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="شما دسترسی مشاهده تلاش سایر دانش‌آموزان را ندارید."
        )

    return {
        "id": attempt.id,
        "experiment_id": attempt.experiment_id,
        "experiment_title": attempt.experiment.title if attempt.experiment else "",
        "experiment_slug": attempt.experiment.slug if attempt.experiment else "",
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
