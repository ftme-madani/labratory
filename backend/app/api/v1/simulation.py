from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid
import time
from typing import Optional, Dict, Any, List

from ...database import get_db
from ...models.user import User
from ...models.experiment import Experiment
from ...models.attempt import ExperimentAttempt, StepActionLog, HintUsage
from ...schemas.simulation import (
    ActionExecuteRequest,
    ActionExecuteResponse,
    SimulationErrorSchema,
    HintRequest,
    HintResponse,
    StartAttemptResponse,
    FinishAttemptResponse
)
from ..deps import get_current_user
from simulation_engine.schema import LabAction
from simulation_engine.registry import get_simulation_engine
from simulation_engine.hints.engine import IntelligentHintService
from simulation_engine.hints.catalog import HINT_CATALOG

router = APIRouter(prefix="/simulation", tags=["Simulation & Virtual Lab"])

@router.post("/attempts/start", response_model=StartAttemptResponse, status_code=status.HTTP_201_CREATED)
def start_experiment_attempt(
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    آغاز تلاش جدید برای اجرای یک آزمایش مجازی در محیط لابراتوار
    """
    experiment_id = payload.get("experiment_id")
    experiment_slug = payload.get("experiment_slug")

    query = db.query(Experiment)
    if experiment_id:
        experiment = query.filter(Experiment.id == experiment_id).first()
    elif experiment_slug:
        experiment = query.filter(Experiment.slug == experiment_slug).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ارسال شناسه (experiment_id) یا نامک (experiment_slug) آزمایش الزامی است."
        )

    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="آزمایش علمی مورد نظر در سامانه یافت نشد."
        )

    class_code = payload.get("class_code")
    # بررسی آزمایش‌های اختصاصی کلاس
    if experiment.is_class_only and current_user.role not in ["teacher", "admin"]:
        if not class_code or (experiment.class_code and experiment.class_code.lower() != str(class_code).strip().lower()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="این آزمایش مختص دانش‌آموزان کلاس دبیر مربوطه است. لطفاً کد دسترسی معتبر وارد کنید."
            )

    # ایجاد شناسه یکتا برای این نوبت اجرای آزمایش
    unique_suffix = uuid.uuid4().hex[:6]
    attempt_id = f"att-{int(time.time())}-{unique_suffix}"
    total_steps = len(experiment.steps_config) if experiment.steps_config else 3

    new_attempt = ExperimentAttempt(
        id=attempt_id,
        user_id=current_user.id,
        experiment_id=experiment.id,
        class_code=str(class_code).strip() if class_code else experiment.class_code,
        status="IN_PROGRESS",
        score=100.0,
        steps_completed=0,
        total_steps=total_steps,
        final_observations=[],
        final_measurements={}
    )
    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    return StartAttemptResponse(
        attempt_id=new_attempt.id,
        experiment_id=experiment.id,
        experiment_slug=experiment.slug,
        experiment_title=experiment.title,
        total_steps=total_steps,
        current_step=1,
        status=new_attempt.status
    )

@router.post("/attempts/{attempt_id}/action", response_model=ActionExecuteResponse)
def execute_lab_action(
    attempt_id: str,
    action_in: ActionExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ارزیابی قطعی کنش آزمایشگاهی با قوانین موتور علمی مستقل و بدون توهم هوش مصنوعی
    """
    attempt = db.query(ExperimentAttempt).filter(ExperimentAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="تلاش آزمایشگاهی مورد نظر یافت نشد."
        )

    # کنترل امنیت دسترسی به داده‌های دانش‌آموز
    if attempt.user_id != current_user.id and current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="شما مجاز به تغییر وضعیت تلاش سایر کاربران نیستید."
        )

    if attempt.status != "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این نوبت آزمایش قبلاً نهایی شده و امکان ثبت کنش جدید در آن وجود ندارد."
        )

    experiment = attempt.experiment
    engine = get_simulation_engine(experiment.slug)

    # بازسازی قطعی وضعیت موتور شبیه‌سازی از روی لاگ‌های پیشین موفق (Stateless Replay)
    if engine:
        past_logs = (
            db.query(StepActionLog)
            .filter(StepActionLog.attempt_id == attempt.id, StepActionLog.is_valid == True)
            .order_by(StepActionLog.id.asc())
            .all()
        )
        for log in past_logs:
            src = log.item_ids[0] if log.item_ids and len(log.item_ids) > 0 else ""
            tgt = log.item_ids[1] if log.item_ids and len(log.item_ids) > 1 else None
            params = getattr(log, 'parameters', None) or {}
            engine.execute_action(LabAction(action_type=log.action_type, source_id=src, target_id=tgt, parameters=params))

        # اجرای کنش فعلی روی موتور اعتبارسنجی علمی
        current_action = LabAction(
            action_type=action_in.action_type,
            source_id=action_in.source_id,
            target_id=action_in.target_id,
            parameters=action_in.parameters
        )
        result = engine.execute_action(current_action)
    else:
        # برای آزمایش‌های پیش‌نویسی که هنوز موتور اختصاصی در ریجستری ندارند
        from simulation_engine.schema import StepResult
        result = StepResult(
            success=True,
            step_index=attempt.steps_completed + 1,
            is_step_completed=True,
            observations=[f"کنش «{action_in.action_type}» روی «{action_in.source_id}» با موفقیت انجام شد."],
            measurements={},
            state_snapshot={},
            is_terminal=False
        )

    # ثبت لاگ کنش در جدول پایگاه داده
    items_used = [action_in.source_id]
    if action_in.target_id:
        items_used.append(action_in.target_id)

    obs_text = " | ".join(result.observations) if result.observations else ""
    feedback_msg = (
        result.error.recommended_action if result.error else "کنش با موفقیت طبق اصول علمی انجام شد."
    )

    action_log = StepActionLog(
        attempt_id=attempt.id,
        step_index=result.step_index,
        action_type=action_in.action_type,
        item_ids=items_used,
        parameters=action_in.parameters or {},
        is_valid=result.success,
        error_code=result.error.code if result.error else None,
        observation_text=obs_text,
        feedback_text=feedback_msg
    )
    db.add(action_log)

    # به‌روزرسانی پیشرفت و امتیاز
    if result.success:
        if result.is_step_completed and result.step_index > attempt.steps_completed:
            attempt.steps_completed = result.step_index
        # ذخیره مشاهدات علمی جدید
        current_obs = list(attempt.final_observations or [])
        for obs in (result.observations or []):
            if obs not in current_obs:
                current_obs.append(obs)
        attempt.final_observations = current_obs
    else:
        # کسر جزئی امتیاز برای خطای علمی (حداقل نمره صفر)
        attempt.score = max(0.0, attempt.score - 5.0)

    # در صورت اتمام گام نهایی
    if result.is_terminal and result.success:
        attempt.status = "COMPLETED"
        attempt.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(attempt)

    err_schema = None
    if result.error:
        cat_str = result.error.category.value if hasattr(result.error.category, "value") else str(result.error.category)
        err_schema = SimulationErrorSchema(
            code=result.error.code,
            category=cat_str,
            title=result.error.title,
            description=result.error.description,
            scientific_rationale=result.error.scientific_rationale,
            recommended_action=result.error.recommended_action
        )

    return ActionExecuteResponse(
        success=result.success,
        step_index=result.step_index,
        is_step_completed=result.is_step_completed,
        error=err_schema,
        observations=result.observations or [],
        measurements=result.measurements or {},
        state_snapshot=result.state_snapshot or {},
        is_terminal=result.is_terminal
    )

@router.post("/attempts/{attempt_id}/hint", response_model=HintResponse)
def request_tiered_hint(
    attempt_id: str,
    hint_in: HintRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ارائه راهنمای هوشمند سه‌سطحی پداگوژیک متناسب با خطای آزمایشگاهی تشخیص‌داده‌شده
    """
    attempt = db.query(ExperimentAttempt).filter(ExperimentAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="تلاش آزمایشگاهی یافت نشد."
        )

    if attempt.user_id != current_user.id and current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی غیرمجاز به راهنماهای سایر کاربران."
        )

    # شمارش دفعات استفاده از راهنما برای این خطا در این تلاش
    prior_usages = (
        db.query(HintUsage)
        .filter(HintUsage.attempt_id == attempt.id, HintUsage.error_code == hint_in.error_code)
        .all()
    )

    if hint_in.forced_level:
        target_level = min(3, max(1, hint_in.forced_level))
    else:
        target_level = min(3, len(prior_usages) + 1)

    catalog_hint = HINT_CATALOG.get(hint_in.error_code)
    from simulation_engine.schema import ErrorCategory, SimulationError
    category = catalog_hint.category if catalog_hint else ErrorCategory.WRONG_TOOL
    sim_err = SimulationError(
        code=hint_in.error_code,
        category=category,
        title=catalog_hint.level1_question if catalog_hint else "خطای آزمایشگاهی",
        description="خطای عملیاتی در آزمایش",
        scientific_rationale="رعایت موازین علمی کتاب درسی",
        recommended_action=""
    )

    hint_service = IntelligentHintService()
    hint_data = hint_service.get_hint_for_error(
        attempt_id=attempt.id,
        error=sim_err,
        experiment_id=attempt.experiment.slug,
        step_index=hint_in.step_index,
        forced_level=target_level
    )

    # ثبت لاگ استفاده از راهنما
    usage = HintUsage(
        attempt_id=attempt.id,
        step_index=hint_in.step_index,
        error_code=hint_data["error_code"],
        hint_level=hint_data["level"],
        hint_content=hint_data["content"]
    )
    db.add(usage)

    # کسر پداگوژیک امتیاز راهنما: سطح ۱: -۱ نمره، سطح ۲: -۲ نمره، سطح ۳: -۴ نمره
    penalties = {1: 1.0, 2: 2.0, 3: 4.0}
    attempt.score = max(0.0, attempt.score - penalties.get(hint_data["level"], 2.0))

    db.commit()

    return HintResponse(
        error_code=hint_data["error_code"],
        category=hint_data["category"],
        level=hint_data["level"],
        can_escalate=hint_data["can_escalate"],
        content=hint_data["content"],
        scientific_rationale=hint_data["scientific_rationale"]
    )

@router.post("/attempts/{attempt_id}/finish", response_model=FinishAttemptResponse)
def finish_experiment_attempt(
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    نهایی‌سازی و ثبت رسمی نمرات و مشاهدات ثبت‌شده در تلاش آزمایشگاه
    """
    attempt = db.query(ExperimentAttempt).filter(ExperimentAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="تلاش آزمایشگاهی یافت نشد."
        )

    if attempt.user_id != current_user.id and current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی غیرمجاز برای اتمام تلاش سایر کاربران."
        )

    if attempt.status != "COMPLETED":
        attempt.status = "COMPLETED" if attempt.steps_completed >= attempt.total_steps else "FAILED"
        attempt.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(attempt)

    return FinishAttemptResponse(
        attempt_id=attempt.id,
        status=attempt.status,
        score=attempt.score,
        total_steps=attempt.total_steps,
        steps_completed=attempt.steps_completed,
        observations_count=len(attempt.final_observations or [])
    )

@router.get("/attempts/{attempt_id}/state")
def get_attempt_state(
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت وضعیت جاری، تاریخچه لاگ‌ها و راهنماهای استفاده‌شده در تلاش آزمایشگاهی
    """
    attempt = db.query(ExperimentAttempt).filter(ExperimentAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="تلاش آزمایشگاهی یافت نشد."
        )

    if attempt.user_id != current_user.id and current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی غیرمجاز."
        )

    logs = [
        {
            "id": l.id,
            "step_index": l.step_index,
            "action_type": l.action_type,
            "item_ids": l.item_ids,
            "parameters": getattr(l, "parameters", None) or {},
            "is_valid": l.is_valid,
            "error_code": l.error_code,
            "observation_text": l.observation_text,
            "feedback_text": l.feedback_text,
            "created_at": l.created_at.isoformat()
        }
        for l in attempt.action_logs
    ]

    hints = [
        {
            "id": h.id,
            "step_index": h.step_index,
            "error_code": h.error_code,
            "hint_level": h.hint_level,
            "hint_content": h.hint_content,
            "created_at": h.created_at.isoformat()
        }
        for h in attempt.hint_usages
    ]

    return {
        "attempt_id": attempt.id,
        "experiment_id": attempt.experiment_id,
        "experiment_slug": attempt.experiment.slug,
        "experiment_title": attempt.experiment.title,
        "status": attempt.status,
        "score": attempt.score,
        "steps_completed": attempt.steps_completed,
        "total_steps": attempt.total_steps,
        "final_observations": attempt.final_observations,
        "action_logs": logs,
        "hint_usages": hints,
        "started_at": attempt.started_at.isoformat(),
        "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None
    }
