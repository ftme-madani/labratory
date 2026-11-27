from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, date
import csv
import io

from ...database import get_db
from ...models.user import User
from ...models.experiment import Experiment
from ...models.attempt import ExperimentAttempt, StepActionLog, HintUsage
from ...schemas.analytics import (
    TeacherAnalyticsResponse,
    FrequentErrorStatSchema,
    ClassPerformanceStatSchema,
    AnalyticsOverviewResponse,
    MisconceptionsResponse,
    MisconceptionItemSchema,
    TeacherStudentAnalyticsItem,
    StudentLogsResponse,
    StudentLogItem
)
from ...schemas.experiment import TeacherFeedbackUpdate
from ..deps import require_role
from simulation_engine.hints.catalog import HINT_CATALOG, EXPERIMENT_TITLES

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

@router.get("/analytics/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(
    experiment_id: Optional[int] = Query(None, description="فیلتر بر اساس شناسه آزمایش"),
    class_code: Optional[str] = Query(None, description="فیلتر بر اساس کد اختصاصی کلاس"),
    date_from: Optional[datetime] = Query(None, description="تاریخ شروع"),
    date_to: Optional[datetime] = Query(None, description="تاریخ پایان"),
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    """
    دریافت خلاصه شاخص‌های کلیدی عملکرد کلاس (تعداد تلاش‌ها، نرخ موفقیت، میانگین نمره و دانش‌آموزان فعال)
    """
    query = db.query(ExperimentAttempt)
    if experiment_id:
        query = query.filter(ExperimentAttempt.experiment_id == experiment_id)
    if class_code:
        query = query.filter(ExperimentAttempt.class_code == class_code.strip())
    if date_from:
        query = query.filter(ExperimentAttempt.started_at >= date_from)
    if date_to:
        query = query.filter(ExperimentAttempt.started_at <= date_to)

    attempts = query.all()
    total_attempts = len(attempts)
    completed_attempts = sum(1 for a in attempts if a.status == "COMPLETED")
    overall_success_rate = round((completed_attempts / total_attempts * 100), 1) if total_attempts > 0 else 0.0
    active_students_count = len(set(a.user_id for a in attempts))
    average_score = round(sum(a.score for a in attempts) / total_attempts, 1) if total_attempts > 0 else 0.0

    attempt_ids = [a.id for a in attempts]
    total_hints = db.query(HintUsage).filter(HintUsage.attempt_id.in_(attempt_ids)).count() if attempt_ids else 0
    total_errors = db.query(StepActionLog).filter(StepActionLog.attempt_id.in_(attempt_ids), StepActionLog.is_valid == False).count() if attempt_ids else 0

    return AnalyticsOverviewResponse(
        total_attempts=total_attempts,
        completed_attempts=completed_attempts,
        overall_success_rate=overall_success_rate,
        active_students_count=active_students_count,
        average_score=average_score,
        total_hints_used=total_hints,
        total_errors_recorded=total_errors
    )

@router.get("/analytics/misconceptions", response_model=MisconceptionsResponse)
def get_analytics_misconceptions(
    experiment_id: Optional[int] = Query(None, description="فیلتر بر اساس شناسه آزمایش"),
    class_code: Optional[str] = Query(None, description="فیلتر بر اساس کد اختصاصی کلاس"),
    date_from: Optional[datetime] = Query(None, description="تاریخ شروع"),
    date_to: Optional[datetime] = Query(None, description="تاریخ پایان"),
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    """
    تحلیل آماری و ردیابی کج‌فهمی‌های علمی دانش‌آموزان بر مبنای خطاهای ثبت‌شده موتور شبیه‌سازی
    """
    query = (
        db.query(StepActionLog)
        .join(ExperimentAttempt, StepActionLog.attempt_id == ExperimentAttempt.id)
        .filter(StepActionLog.is_valid == False, StepActionLog.error_code.isnot(None))
    )

    if experiment_id:
        query = query.filter(ExperimentAttempt.experiment_id == experiment_id)
    if class_code:
        query = query.filter(ExperimentAttempt.class_code == class_code.strip())
    if date_from:
        query = query.filter(StepActionLog.created_at >= date_from)
    if date_to:
        query = query.filter(StepActionLog.created_at <= date_to)

    error_logs = query.all()
    total_errors = len(error_logs)

    counts: Dict[str, int] = {}
    students_per_error: Dict[str, set] = {}
    exp_per_error: Dict[str, set] = {}

    for log in error_logs:
        code = log.error_code
        counts[code] = counts.get(code, 0) + 1
        if code not in students_per_error:
            students_per_error[code] = set()
            exp_per_error[code] = set()
        if log.attempt:
            students_per_error[code].add(log.attempt.user_id)
            if log.attempt.experiment:
                exp_per_error[code].add(log.attempt.experiment.title)

    misconceptions: List[MisconceptionItemSchema] = []
    for code, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        cat = HINT_CATALOG.get(code)
        pct = round((count / total_errors * 100), 1) if total_errors > 0 else 0.0
        exp_title = "، ".join(exp_per_error[code]) if exp_per_error.get(code) else (cat.get("experiment_title") if cat else "آزمایشگاه علوم")

        if cat:
            err_title = getattr(cat, "level1_question", None) or f"کج‌فهمی علمی {code}"
            exp_fallback = EXPERIMENT_TITLES.get(getattr(cat, "experiment_id", ""), "آزمایشگاه علوم")
            misconceptions.append(MisconceptionItemSchema(
                error_code=code,
                error_title=err_title,
                experiment_title="، ".join(exp_per_error[code]) if exp_per_error.get(code) else exp_fallback,
                scientific_concept=getattr(cat, "category", "مفاهیم کتاب درسی").value if hasattr(getattr(cat, "category", None), "value") else str(getattr(cat, "category", "مفاهیم درسی")),
                recommended_remediation=getattr(cat, "level3_explanation", "مرور دستورالعمل کتاب درسی"),
                occurrence_count=count,
                percentage=pct,
                affected_students_count=len(students_per_error.get(code, set()))
            ))
        else:
            misconceptions.append(MisconceptionItemSchema(
                error_code=code,
                error_title=f"خطای علمی {code}",
                experiment_title=exp_title,
                scientific_concept="رعایت ترتیب علمی و پیش‌نیازها",
                recommended_remediation="بررسی اهداف آزمایش و مرور مجدد پیش‌نیازهای درسی",
                occurrence_count=count,
                percentage=pct,
                affected_students_count=len(students_per_error.get(code, set()))
            ))

    return MisconceptionsResponse(
        total_errors=total_errors,
        misconceptions=misconceptions
    )

@router.get("/analytics/students", response_model=List[TeacherStudentAnalyticsItem])
def get_analytics_students(
    class_code: Optional[str] = Query(None, description="فیلتر بر اساس کد کلاس"),
    experiment_id: Optional[int] = Query(None, description="فیلتر بر اساس شناسه آزمایش"),
    date_from: Optional[datetime] = Query(None, description="تاریخ شروع"),
    date_to: Optional[datetime] = Query(None, description="تاریخ پایان"),
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    """
    فهرست تحلیلی عملکرد دانش‌آموزان به همراه درصد موفقیت، میانگین نمرات و وضعیت فعالیت
    """
    students_query = db.query(User).filter(User.role == "student")
    if class_code:
        students_query = students_query.filter(User.class_code == class_code.strip())
    students = students_query.all()

    result: List[TeacherStudentAnalyticsItem] = []
    for s in students:
        att_query = db.query(ExperimentAttempt).filter(ExperimentAttempt.user_id == s.id)
        if experiment_id:
            att_query = att_query.filter(ExperimentAttempt.experiment_id == experiment_id)
        if class_code:
            att_query = att_query.filter(ExperimentAttempt.class_code == class_code.strip())
        if date_from:
            att_query = att_query.filter(ExperimentAttempt.started_at >= date_from)
        if date_to:
            att_query = att_query.filter(ExperimentAttempt.started_at <= date_to)

        attempts = att_query.all()
        total_att = len(attempts)
        comp_att = sum(1 for a in attempts if a.status == "COMPLETED")
        success_rate = round((comp_att / total_att * 100), 1) if total_att > 0 else 0.0
        avg_score = round(sum(a.score for a in attempts) / total_att, 1) if total_att > 0 else 0.0

        att_ids = [a.id for a in attempts]
        err_count = db.query(StepActionLog).filter(StepActionLog.attempt_id.in_(att_ids), StepActionLog.is_valid == False).count() if att_ids else 0
        hint_count = db.query(HintUsage).filter(HintUsage.attempt_id.in_(att_ids)).count() if att_ids else 0

        last_act = None
        if attempts:
            latest = max(attempts, key=lambda a: a.started_at)
            last_act = latest.started_at.isoformat()

        result.append(TeacherStudentAnalyticsItem(
            student_id=s.id,
            full_name=s.full_name,
            email=s.email,
            grade=s.grade,
            school_name=s.school_name,
            class_code=s.class_code,
            total_attempts=total_att,
            completed_attempts=comp_att,
            success_rate=success_rate,
            average_score=avg_score,
            errors_count=err_count,
            hints_count=hint_count,
            last_activity=last_act
        ))

    result.sort(key=lambda x: (x.total_attempts, x.average_score), reverse=True)
    return result

@router.get("/analytics/student/{student_id}/logs", response_model=StudentLogsResponse)
def get_student_analytics_logs(
    student_id: int,
    experiment_id: Optional[int] = Query(None, description="فیلتر بر اساس شناسه آزمایش"),
    date_from: Optional[datetime] = Query(None, description="تاریخ شروع"),
    date_to: Optional[datetime] = Query(None, description="تاریخ پایان"),
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    """
    استعلام لاگ تفصیلی اقدامات و پاسخ‌های یک دانش‌آموز جهت عارضه‌یابی و بررسی کج‌فهمی‌ها
    """
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="دانش‌آموز مورد نظر یافت نشد."
        )

    query = (
        db.query(StepActionLog)
        .join(ExperimentAttempt, StepActionLog.attempt_id == ExperimentAttempt.id)
        .filter(ExperimentAttempt.user_id == student_id)
    )

    if isinstance(experiment_id, int):
        query = query.filter(ExperimentAttempt.experiment_id == experiment_id)
    if isinstance(date_from, (datetime, date)):
        query = query.filter(StepActionLog.created_at >= date_from)
    if isinstance(date_to, (datetime, date)):
        query = query.filter(StepActionLog.created_at <= date_to)

    logs = query.order_by(StepActionLog.created_at.desc()).all()

    log_items: List[StudentLogItem] = []
    for log in logs:
        cat = HINT_CATALOG.get(log.error_code) if log.error_code else None
        err_title = getattr(cat, "level1_question", None) if cat else (f"خطای {log.error_code}" if log.error_code else None)
        log_items.append(StudentLogItem(
            id=log.id,
            attempt_id=log.attempt_id,
            experiment_id=log.attempt.experiment_id if log.attempt else 0,
            experiment_title=log.attempt.experiment.title if log.attempt and log.attempt.experiment else "آزمایشگاه علوم",
            step_index=log.step_index,
            action_type=log.action_type,
            item_ids=log.item_ids or [],
            parameters=log.parameters or {},
            is_valid=log.is_valid,
            error_code=log.error_code,
            error_title=err_title,
            observation_text=log.observation_text,
            feedback_text=log.feedback_text,
            created_at=log.created_at.isoformat()
        ))

    return StudentLogsResponse(
        student_id=student.id,
        full_name=student.full_name,
        total_logs=len(log_items),
        logs=log_items
    )

@router.get("/reports/class/csv")
def export_class_report_csv(
    class_code: Optional[str] = Query(None, description="کد کلاس"),
    experiment_id: Optional[int] = Query(None, description="شناسه آزمایش"),
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    """
    تولید و دانلود گزارش کارنامه کلاس با فرمت استاندارد CSV فارسی (UTF-8-SIG برای سازگاری با اکسل)
    """
    query = db.query(ExperimentAttempt).join(Experiment, ExperimentAttempt.experiment_id == Experiment.id)
    if class_code:
        query = query.filter(ExperimentAttempt.class_code == class_code.strip())
    if experiment_id:
        query = query.filter(ExperimentAttempt.experiment_id == experiment_id)

    attempts = query.order_by(ExperimentAttempt.started_at.desc()).all()

    output = io.StringIO()
    # Write BOM for Excel UTF-8 recognition
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow([
        "شناسه تلاش",
        "نام دانش‌آموز",
        "ایمیل",
        "پایه",
        "عنوان آزمایش",
        "کد کلاس",
        "وضعیت",
        "نمره نهایی",
        "مراحل طی شده",
        "تعداد راهنماهای استفاده شده",
        "تعداد خطاها",
        "تاریخ شروع",
        "تاریخ پایان",
        "بازخورد معلم"
    ])

    for a in attempts:
        writer.writerow([
            a.id,
            a.user.full_name if a.user else "ناشناس",
            a.user.email if a.user else "",
            a.user.grade or "",
            a.experiment.title if a.experiment else "",
            a.class_code or "",
            "موفق" if a.status == "COMPLETED" else "در جریان",
            a.score,
            f"{a.steps_completed} از {a.total_steps}",
            len(a.hint_usages),
            sum(1 for log in a.action_logs if not log.is_valid),
            a.started_at.strftime("%Y-%m-%d %H:%M:%S") if a.started_at else "",
            a.completed_at.strftime("%Y-%m-%d %H:%M:%S") if a.completed_at else "",
            a.teacher_feedback or ""
        ])

    csv_data = output.getvalue().encode('utf-8-sig')
    filename = f"class_report_{class_code or 'all'}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/reports/student/{student_id}/csv")
def export_student_report_csv(
    student_id: int,
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    """
    تولید و دانلود گزارش عملکرد فردی دانش‌آموز با فرمت استاندارد CSV فارسی
    """
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="دانش‌آموز یافت نشد."
        )

    attempts = db.query(ExperimentAttempt).filter(ExperimentAttempt.user_id == student_id).order_by(ExperimentAttempt.started_at.desc()).all()

    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow([
        "شناسه تلاش",
        "عنوان آزمایش",
        "وضعیت",
        "نمره",
        "گام‌های تکمیل‌شده",
        "تعداد راهنماها",
        "تعداد خطاها",
        "تاریخ شروع",
        "تاریخ اتمام",
        "بازخورد معلم"
    ])

    for a in attempts:
        writer.writerow([
            a.id,
            a.experiment.title if a.experiment else "",
            "موفق" if a.status == "COMPLETED" else "در جریان",
            a.score,
            f"{a.steps_completed} از {a.total_steps}",
            len(a.hint_usages),
            sum(1 for log in a.action_logs if not log.is_valid),
            a.started_at.strftime("%Y-%m-%d %H:%M:%S") if a.started_at else "",
            a.completed_at.strftime("%Y-%m-%d %H:%M:%S") if a.completed_at else "",
            a.teacher_feedback or ""
        ])

    csv_data = output.getvalue().encode('utf-8-sig')
    filename = f"student_{student_id}_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
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

