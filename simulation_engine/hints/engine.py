from typing import Dict, Any, Optional
from datetime import datetime, timezone
from ..schema import ErrorCategory, SimulationError
from .models import TieredHint
from .catalog import HINT_CATALOG, DEFAULT_CATEGORY_HINTS, EXPERIMENT_TITLES
from .llm_adapter import BaseLLMAdapter, OfflineRuleLLMAdapter, ExternalLLMAdapter

class IntelligentHintService:
    """
    سرویس مرکزی راهنمای هوشمند آموزشی سه‌سطحی.
    ارائه راهنمایی متناسب با نوع خطا و پیشرفت تدریجی سطوح بر مبنای تعداد تلاش‌ها.
    """

    def __init__(self, llm_adapter: Optional[BaseLLMAdapter] = None):
        self.llm_adapter = llm_adapter or ExternalLLMAdapter()
        # تاریخچه تلاش‌ها و درخواست‌های هر نشست: attempt_id -> { error_code -> attempt_count }
        self._session_telemetry: Dict[str, Dict[str, int]] = {}
        # تاریخچه سطوح دریافت‌شده: attempt_id -> list of records
        self._hint_history: Dict[str, list] = {}

    def get_hint_for_error(
        self,
        attempt_id: str,
        error: SimulationError,
        experiment_id: str,
        step_index: int,
        forced_level: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        تولید و ثبت راهنمای متناسب با خطای رخ‌داده با افزایش هوشمند سطح راهنمایی
        """
        # ۱. ردگیری تعداد تلاش‌های ناموفق در این سشن برای این خطا
        if attempt_id not in self._session_telemetry:
            self._session_telemetry[attempt_id] = {}

        current_attempts = self._session_telemetry[attempt_id].get(error.code, 0) + 1
        self._session_telemetry[attempt_id][error.code] = current_attempts

        # ۲. محاسبه خودکار سطح راهنمایی (در صورت عدم درخواست دستی کاربر):
        # تلاش اول: سطح ۱ (سقراطی/تفکری)
        # تلاش دوم: سطح ۲ (سرنخ مفهومی)
        # تلاش سوم و بیشتر: سطح ۳ (توضیح کامل علمی و اقدام اصلاحی)
        if forced_level is not None:
            effective_level = max(1, min(3, forced_level))
        else:
            if current_attempts == 1:
                effective_level = 1
            elif current_attempts == 2:
                effective_level = 2
            else:
                effective_level = 3

        # ۳. بازیابی راهنمای معتبر از کاتالوگ یا فال‌بک دسته خطا
        tiered_hint = HINT_CATALOG.get(error.code)
        if not tiered_hint:
            tiered_hint = DEFAULT_CATEGORY_HINTS.get(
                error.category,
                DEFAULT_CATEGORY_HINTS[ErrorCategory.WRONG_TOOL]
            )

        raw_hint_text = tiered_hint.get_content_for_level(effective_level)

        # ۴. پردازش لحن آموزشی از طریق آداپتور (با گاردریل عدم تغییر محتوای علمی)
        category_val = error.category.value if hasattr(error.category, "value") else str(error.category)
        hint_context = {
            "raw_hint": raw_hint_text,
            "level": effective_level,
            "error_code": error.code,
            "category": category_val,
            "textbook_source": "کتاب علوم تجربی دوره متوسطه",
            "scientific_rationale": error.scientific_rationale,
            "experiment_id": experiment_id,
            "experiment_title": EXPERIMENT_TITLES.get(experiment_id, "آزمایشگاه علوم تجربی"),
            "step_index": step_index,
            "action_summary": error.description or error.title
        }

        final_explanation = self.llm_adapter.generate_explanation(hint_context)

        # ۵. ذخیره تل‌متری حداقلی آموزشی
        record = {
            "attempt_id": attempt_id,
            "step_index": step_index,
            "error_code": error.code,
            "category": error.category.value,
            "level": effective_level,
            "attempts_for_this_error": current_attempts,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if attempt_id not in self._hint_history:
            self._hint_history[attempt_id] = []
        self._hint_history[attempt_id].append(record)

        return {
            "error_code": error.code,
            "category": error.category.value,
            "level": effective_level,
            "can_escalate": effective_level < 3,
            "content": final_explanation,
            "scientific_rationale": error.scientific_rationale,
            "telemetry": record
        }

    def get_session_history(self, attempt_id: str) -> list:
        """بازیابی تاریخچه راهنمایی‌های استفاده‌شده در یک تلاش مشخص"""
        return self._hint_history.get(attempt_id, [])
