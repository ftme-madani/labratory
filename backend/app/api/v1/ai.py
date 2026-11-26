from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Dict, Any, List
import logging

from ...database import get_db
from ...models.user import User
from ...models.experiment import Experiment
from ...models.attempt import ExperimentAttempt, StepActionLog, HintUsage
from ...schemas.ai import (
    AITutorHintRequest,
    AITutorHintResponse,
    AIQuestionRequest,
    AIQuestionResponse,
    TeacherAIInsightsResponse,
    VoiceTTSRequest
)
from ..deps import get_current_user, require_role
from ...config import settings
from simulation_engine.hints.engine import IntelligentHintService
from simulation_engine.hints.llm_adapter import ExternalLLMAdapter
from simulation_engine.hints.catalog import HINT_CATALOG, EXPERIMENT_TITLES
from simulation_engine.schema import SimulationError, ErrorCategory

router = APIRouter(prefix="/ai", tags=["AI Educational Assistant & Intelligence"])

@router.post("/tutor/hint", response_model=AITutorHintResponse)
def request_ai_tutor_hint(
    payload: AITutorHintRequest,
    attempt_id: str = Query(..., description="شناسه تلاش آزمایش"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت راهنمای آموزشی شخصی‌سازی‌شده و سه‌سطحی از دستیار هوشمند مبتنی بر Gemini.
    در صورت عدم دسترسی به هوش مصنوعی، به‌صورت خودکار و شفاف از قواعد مصوب کتاب درسی استفاده می‌شود.
    """
    attempt = db.query(ExperimentAttempt).filter(ExperimentAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="تلاش آزمایشگاهی مورد نظر یافت نشد."
        )

    # کنترل امنیت دسترسی
    if attempt.user_id != current_user.id and current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="شما مجاز به دسترسی به داده‌های تلاش سایر کاربران نیستید."
        )

    # سابقه دریافت راهنما برای این خطا
    prior_usages = (
        db.query(HintUsage)
        .filter(HintUsage.attempt_id == attempt.id, HintUsage.error_code == payload.error_code)
        .all()
    )

    if payload.forced_level:
        target_level = min(3, max(1, payload.forced_level))
    else:
        target_level = min(3, len(prior_usages) + 1)

    catalog_hint = HINT_CATALOG.get(payload.error_code)
    category = catalog_hint.category if catalog_hint else ErrorCategory.WRONG_TOOL
    title = catalog_hint.level1_question if catalog_hint else "خطای عملیاتی در آزمایش"
    rationale = catalog_hint.level2_clue if catalog_hint else "رعایت موازین و مفاهیم کتاب درسی علوم تجربی"

    sim_error = SimulationError(
        code=payload.error_code,
        category=category,
        title=title,
        description=payload.action_summary or "خطا در انجام آزمایش",
        scientific_rationale=rationale,
        recommended_action=catalog_hint.level3_explanation if catalog_hint else ""
    )

    # سرویس هوشمند با آداپتور Gemini
    hint_service = IntelligentHintService(llm_adapter=ExternalLLMAdapter())
    hint_data = hint_service.get_hint_for_error(
        attempt_id=attempt.id,
        error=sim_error,
        experiment_id=attempt.experiment.slug if attempt.experiment else "exp-general",
        step_index=payload.step_index,
        forced_level=target_level
    )

    # ثبت لاگ استفاده از راهنما در پایگاه داده
    usage = HintUsage(
        attempt_id=attempt.id,
        step_index=payload.step_index,
        error_code=hint_data["error_code"],
        hint_level=hint_data["level"],
        hint_content=hint_data["content"]
    )
    db.add(usage)

    # کسر پداگوژیک امتیاز: سطح ۱: -۱ نمره، سطح ۲: -۲ نمره، سطح ۳: -۴ نمره
    penalties = {1: 1.0, 2: 2.0, 3: 4.0}
    attempt.score = max(0.0, attempt.score - penalties.get(hint_data["level"], 2.0))
    db.commit()

    return AITutorHintResponse(
        attempt_id=attempt.id,
        error_code=hint_data["error_code"],
        category=hint_data["category"],
        level=hint_data["level"],
        can_escalate=hint_data["can_escalate"],
        content=hint_data["content"],
        scientific_rationale=hint_data["scientific_rationale"],
        is_ai_generated=settings.effective_gemini_api_key is not None,
        model_used=settings.AI_MODEL if settings.effective_gemini_api_key else "offline-rule-catalog"
    )

@router.post("/tutor/ask", response_model=AIQuestionResponse)
def ask_ai_tutor_question(
    payload: AIQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    پاسخ هوشمند دستیار آموزشی به پرسش‌های مفهومی و ابهامات علمی دانش‌آموز در طول آزمایش
    """
    attempt = db.query(ExperimentAttempt).filter(ExperimentAttempt.id == payload.attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="تلاش آزمایشگاهی یافت نشد."
        )

    if attempt.user_id != current_user.id and current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی غیرمجاز به اطلاعات تلاش سایر کاربران."
        )

    exp_title = attempt.experiment.title if attempt.experiment else "آزمایشگاه علوم"
    exp_context = {
        "title": exp_title,
        "current_step": payload.step_index or attempt.steps_completed + 1,
        "observations": attempt.final_observations or []
    }

    adapter = ExternalLLMAdapter()
    answer_text = adapter.answer_question(payload.question, exp_context)

    return AIQuestionResponse(
        attempt_id=attempt.id,
        question=payload.question,
        answer=answer_text,
        experiment_title=exp_title,
        is_ai_generated=settings.effective_gemini_api_key is not None
    )

@router.get("/teacher/insights", response_model=TeacherAIInsightsResponse)
def get_teacher_ai_insights(
    class_code: Optional[str] = Query(None, description="فیلتر بر اساس کد کلاس مشخص"),
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    """
    تفسیر هوشمند بدفهمی‌های پرتکرار کلاس و پیشنهاد روش‌های تدریس جبرانی به دبیر
    """
    query = (
        db.query(StepActionLog.error_code, func.count(StepActionLog.id).label("count"))
        .join(ExperimentAttempt, StepActionLog.attempt_id == ExperimentAttempt.id)
        .filter(StepActionLog.is_valid == False, StepActionLog.error_code.isnot(None))
    )

    if class_code and class_code.strip():
        query = query.filter(ExperimentAttempt.class_code == class_code.strip())

    error_logs = (
        query.group_by(StepActionLog.error_code)
        .order_by(func.count(StepActionLog.id).desc())
        .limit(8)
        .all()
    )

    total_errors = sum(count for _, count in error_logs)
    top_misconceptions: List[Dict[str, Any]] = []

    for err_code, count in error_logs:
        catalog_entry = HINT_CATALOG.get(err_code)

        # استخراج داینامیک نام واقعی و رسمی آزمایش
        exp_title = None
        if catalog_entry and catalog_entry.experiment_id:
            exp_title = EXPERIMENT_TITLES.get(catalog_entry.experiment_id)

        if not exp_title:
            # استخراج نام از پایگاه داده تلاش‌ها
            sample_log = (
                db.query(StepActionLog)
                .join(ExperimentAttempt, StepActionLog.attempt_id == ExperimentAttempt.id)
                .join(Experiment, ExperimentAttempt.experiment_id == Experiment.id)
                .filter(StepActionLog.error_code == err_code)
                .first()
            )
            if sample_log and sample_log.attempt and sample_log.attempt.experiment:
                exp_title = sample_log.attempt.experiment.title

        exp_title = exp_title or "علوم تجربی دوره متوسطه"

        title_text = (
            catalog_entry.level1_question[:45] + "..."
            if catalog_entry and len(catalog_entry.level1_question) > 45
            else (catalog_entry.level1_question if catalog_entry else f"خطای علمی {err_code}")
        )

        top_misconceptions.append({
            "error_code": err_code,
            "error_title": title_text,
            "experiment_title": exp_title,
            "occurrence_count": count,
            "scientific_concept": catalog_entry.level2_clue if catalog_entry else "اصول اولیه کتاب درسی",
            "remediation": catalog_entry.level3_explanation if catalog_entry else "مرور دستور کار کتاب"
        })

    adapter = ExternalLLMAdapter()
    remediation_text = adapter.generate_teacher_insights(top_misconceptions)

    return TeacherAIInsightsResponse(
        class_code=class_code,
        total_errors_analyzed=total_errors,
        top_misconceptions=top_misconceptions,
        ai_pedagogical_remediation=remediation_text,
        is_ai_generated=settings.effective_gemini_api_key is not None
    )

@router.post("/voice/tts")
async def generate_voice_speech(
    payload: VoiceTTSRequest,
    current_user: User = Depends(get_current_user)
):
    """
    تبدیل متن پاسخ علمی به صوت طبیعی فارسی با موتور Edge-TTS (صدای دلارا / فرید).
    کاملاً رایگان، بدون نیاز به API Key خارجی و با کیفیت استودیویی جهت ارائه در دفاع.
    """
    clean_text = payload.text.strip()
    if not clean_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="متن ارسالی برای تبدیل به صوت نمی‌تواند خالی باشد."
        )

    try:
        import edge_tts
        voice_name = payload.voice or "fa-IR-DilaraNeural"
        rate = payload.rate or "+0%"
        communicate = edge_tts.Communicate(clean_text, voice_name, rate=rate)

        audio_bytes = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes.extend(chunk["data"])

        if not audio_bytes:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="پاسخ صوتی تولید نشد."
            )

        return Response(content=bytes(audio_bytes), media_type="audio/mpeg")
    except Exception as exc:
        logging.getLogger("ai_voice").error(f"خطا در تولید صوت فارسی: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در تولید صوت: {str(exc)}"
        )
