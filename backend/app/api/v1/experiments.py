from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ...database import get_db
from ...models.user import User
from ...models.experiment import Experiment
from ...schemas.experiment import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentStatusUpdate,
    JoinClassExperimentRequest
)
from ..deps import get_optional_current_user, require_role

router = APIRouter(prefix="/experiments", tags=["Experiments"])

@router.get("", response_model=List[ExperimentResponse])
def list_experiments(
    subject: Optional[str] = Query(None, description="فیلتر بر اساس رشته (شیمی، فیزیک، زیست)"),
    grade: Optional[str] = Query(None, description="فیلتر بر اساس پایه تحصیلی"),
    difficulty: Optional[str] = Query(None, description="فیلتر بر اساس درجه سختی"),
    status_filter: Optional[str] = Query(None, alias="status", description="وضعیت انتشار"),
    class_code: Optional[str] = Query(None, description="فیلتر بر اساس کد اختصاصی کلاس"),
    only_mine: Optional[bool] = Query(False, description="فقط آزمایش‌های من (ویژه دبیر)"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    فهرست آزمایش‌های درسی با امکان جست‌وجو و فیلتر چندگانه.
    دانش‌آموزان و مهمانان تنها آزمایش‌های منتشرشده (PUBLISHED) را مشاهده می‌کنند.
    """
    query = db.query(Experiment)

    # کنترل سطح دسترسی مشاهده پیش‌نویس‌ها
    is_educator = current_user is not None and current_user.role in ["teacher", "admin"]
    if not is_educator:
        query = query.filter(Experiment.status == "PUBLISHED")
        # اگر آزمایش اختصاصی کلاس باشد، فقط در صورتی نمایش داده شود که کد کلاس ارسالی تطابق داشته باشد
        if class_code:
            query = query.filter(
                (Experiment.is_class_only == False) | (Experiment.class_code == class_code.strip())
            )
        else:
            query = query.filter(Experiment.is_class_only == False)
    else:
        if status_filter:
            query = query.filter(Experiment.status == status_filter)
        if only_mine and current_user:
            query = query.filter(Experiment.created_by_id == current_user.id)

    if class_code:
        query = query.filter(Experiment.class_code == class_code.strip())
    if subject:
        query = query.filter(Experiment.subject == subject)
    if grade:
        query = query.filter(Experiment.grade == grade)
    if difficulty:
        query = query.filter(Experiment.difficulty == difficulty)

    experiments = query.order_by(Experiment.id.asc()).all()
    return [ExperimentResponse.model_validate(e) for e in experiments]

@router.post("/join-class", response_model=ExperimentResponse)
def join_class_experiment(
    req: JoinClassExperimentRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    ورود دانش‌آموز به آزمایش کلاسی با استفاده از کد دسترسی اختصاصی دبیر
    """
    code = req.class_code.strip()
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="کد اختصاصی کلاس یا آزمایش را وارد نمایید."
        )

    # جست‌وجو بر اساس class_code یا slug
    experiment = (
        db.query(Experiment)
        .filter(
            (Experiment.class_code.ilike(code)) | (Experiment.slug.ilike(code))
        )
        .first()
    )

    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="آزمایشی با این کد دسترسی کلاسی یافت نشد. لطفاً کد را با دبیر خود مجدداً بررسی کنید."
        )

    return ExperimentResponse.model_validate(experiment)

@router.get("/{id_or_slug}", response_model=ExperimentResponse)
def get_experiment_detail(
    id_or_slug: str,
    class_code: Optional[str] = Query(None, description="کد دسترسی کلاسی"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت جزئیات کامل یک آزمایش با شناسه عددی یا نامک (Slug) یکتا.
    """
    if id_or_slug.isdigit():
        experiment = db.query(Experiment).filter(Experiment.id == int(id_or_slug)).first()
    else:
        experiment = db.query(Experiment).filter(Experiment.slug == id_or_slug).first()

    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="آزمایش علمی مورد نظر در سامانه یافت نشد."
        )

    # بررسی دسترسی در صورت عدم انتشار
    is_educator = current_user is not None and current_user.role in ["teacher", "admin"]
    if experiment.status != "PUBLISHED" and not is_educator:
        # اگر کاربر با کد دسترسی کلاس وارد شده است
        if experiment.class_code and class_code and experiment.class_code.lower() == class_code.strip().lower():
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="این آزمایش هنوز در مرحله بازبینی علمی بوده و منتشر نشده است."
            )

    return ExperimentResponse.model_validate(experiment)

@router.post("", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
def create_experiment(
    exp_in: ExperimentCreate,
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    """
    ایجاد آزمایش جدید در سامانه با وضعیت پیش‌نویس (ویژه معلمان و مدیران).
    """
    existing_slug = db.query(Experiment).filter(Experiment.slug == exp_in.slug).first()
    if existing_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="نامک (slug) این آزمایش از قبل در سامانه تعریف شده است."
        )

    new_exp = Experiment(
        slug=exp_in.slug,
        title=exp_in.title,
        subject=exp_in.subject,
        grade=exp_in.grade,
        difficulty=exp_in.difficulty,
        duration_minutes=exp_in.duration_minutes,
        status=exp_in.status,
        version=1,
        summary=exp_in.summary,
        textbook_source=exp_in.textbook_source,
        objectives=exp_in.objectives,
        safety_notes=exp_in.safety_notes,
        available_tools=exp_in.available_tools,
        steps_config=exp_in.steps_config,
        thumbnail_type=exp_in.thumbnail_type,
        created_by_id=current_user.id,
        class_code=exp_in.class_code.strip() if exp_in.class_code else None,
        is_class_only=exp_in.is_class_only
    )
    db.add(new_exp)
    db.commit()
    db.refresh(new_exp)
    return ExperimentResponse.model_validate(new_exp)

@router.put("/{experiment_id}/status", response_model=ExperimentResponse)
def update_experiment_status(
    experiment_id: int,
    status_in: ExperimentStatusUpdate,
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    """
    تغییر وضعیت چرخه حیات آزمایش (DRAFT -> VERIFIED -> PUBLISHED) توسط کادر آموزشی.
    """
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="آزمایش مورد نظر یافت نشد."
        )

    exp.status = status_in.status
    db.commit()
    db.refresh(exp)
    return ExperimentResponse.model_validate(exp)
