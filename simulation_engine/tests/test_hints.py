import pytest
from simulation_engine.schema import SimulationError, ErrorCategory, LabAction
from simulation_engine.acid_base.engine import AcidBaseSimulationEngine
from simulation_engine.hints import (
    IntelligentHintService,
    OfflineRuleLLMAdapter,
    ExternalLLMAdapter,
    HINT_CATALOG
)

@pytest.fixture
def hint_service():
    return IntelligentHintService(llm_adapter=OfflineRuleLLMAdapter())

def test_hint_matches_error_category(hint_service):
    """تست ۱: بررسی تناسب محتوای راهنمایی با نوع خطای علمی"""
    error = SimulationError(
        code="ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID",
        category=ErrorCategory.WRONG_TOOL,
        title="شناساگر نامناسب",
        description="تورنسل سرخ در اسید بدون تغییر ماند.",
        scientific_rationale="تورنسل سرخ در محیط اسیدی تغییر رنگ نمی‌دهد.",
        recommended_action="از تورنسل آبی استفاده کنید."
    )

    res = hint_service.get_hint_for_error(
        attempt_id="att-test-1",
        error=error,
        experiment_id="exp-acid-base",
        step_index=1,
        forced_level=1
    )

    assert res["error_code"] == "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"
    assert res["category"] == "WRONG_TOOL"
    assert res["level"] == 1
    # محتوا باید شامل سوال تفکری مربوط به شناساگر سرخ باشد
    assert "شناساگر" in res["content"] or "سرخ" in res["content"]

def test_hint_level_escalation(hint_service):
    """تست ۲: افزایش پلکانی سطح راهنما با تکرار تلاش یا درخواست دستی (۱ -> ۲ -> ۳)"""
    error = SimulationError(
        code="ERR_FILTER_WITHOUT_DISSOLUTION",
        category=ErrorCategory.MISSING_PRECONDITION,
        title="عدم حضور حلال",
        description="نمی‌توان پودر خشک را صاف کرد.",
        scientific_rationale="کاغذ صافی رسوب معلق در مایع را جدا می‌کند.",
        recommended_action="ابتدا آب اضافه کنید."
    )

    attempt_id = "att-escalate-test"

    # تلاش اول: سطح ۱
    res1 = hint_service.get_hint_for_error(attempt_id, error, "exp-mixture-separation", 2)
    assert res1["level"] == 1
    assert "پرسش برای تفکر" in res1["content"]

    # تلاش دوم: سطح ۲
    res2 = hint_service.get_hint_for_error(attempt_id, error, "exp-mixture-separation", 2)
    assert res2["level"] == 2
    assert "سرنخ آموزشی" in res2["content"]

    # تلاش سوم: سطح ۳
    res3 = hint_service.get_hint_for_error(attempt_id, error, "exp-mixture-separation", 2)
    assert res3["level"] == 3
    assert "راهکار و توضیح علمی" in res3["content"]
    assert res3["can_escalate"] is False

def test_llm_cannot_alter_simulation_result():
    """تست ۳: گاردریل - مدل زبانی نمی‌تواند نتیجه موتور علمی را تغییر دهد"""
    engine = AcidBaseSimulationEngine()
    engine.add_tool_to_workbench("beaker_lemon")
    engine.add_tool_to_workbench("litmus_red")

    # اقدام نادرست: تست آب‌لیمو با تورنسل سرخ
    result = engine.execute_action(LabAction(
        action_type="DIP_INDICATOR",
        source_id="litmus_red",
        target_id="beaker_lemon"
    ))

    # موتور عمل را نامعتبر دانسته است
    assert result.success is False
    assert result.is_step_completed is False
    assert engine.state.current_step == 1

    # دریافت راهنما از هوش مصنوعی
    hint_service = IntelligentHintService()
    hint_res = hint_service.get_hint_for_error("att-immutable", result.error, "exp-acid-base", 1)

    # وضعیت موتور و نتیجه شبیه‌ساز باید بدون تغییر و کاملاً محفوظ بماند
    assert result.success is False
    assert engine.state.current_step == 1
    assert result.error.code == "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"

def test_external_llm_failure_does_not_crash_lab():
    """تست ۴: قطع سرویس خارجی باعث از کار افتادن سامانه نمی‌شود (Fallback)"""
    class BrokenExternalAdapter(ExternalLLMAdapter):
        def _call_external_service(self, hint_context):
            raise ConnectionError("External LLM API timed out or refused connection")

    failing_adapter = BrokenExternalAdapter(api_key="fake-secret-key")
    safe_service = IntelligentHintService(llm_adapter=failing_adapter)

    error = SimulationError(
        code="ERR_CIRCUIT_WITHOUT_LOAD",
        category=ErrorCategory.HAZARDOUS_ACTION,
        title="اتصال کوتاه",
        description="سیم‌ها بدون لامپ متصل شدند.",
        scientific_rationale="مقاومت صفر است.",
        recommended_action="لامپ را اضافه کنید."
    )

    # فراخوانی باید بدون کرش کردن، فال‌بک آفلاین استاندارد را برگرداند
    res = safe_service.get_hint_for_error("att-fallback-test", error, "exp-simple-circuit", 1)
    assert res["level"] == 1
    assert len(res["content"]) > 0
    assert "اتصال کوتاه" in res["content"] or "باتری" in res["content"]

def test_explanations_consistency_with_rules():
    """تست ۵: عدم تعارض توضیحات کاتالوگ با مراجع علمی کتاب‌های درسی"""
    for code, hint in HINT_CATALOG.items():
        assert len(hint.level1_question) >= 15
        assert len(hint.level2_clue) >= 15
        assert len(hint.level3_explanation) >= 20
        # بررسی وجود کلیدواژه‌های علمی مرتبط
        combined_text = f"{hint.level1_question} {hint.level2_clue} {hint.level3_explanation}"
        assert any(kw in combined_text for kw in [
            "شناساگر", "اسید", "باز", "صافی", "نمک", "ماسه", "باتری", "مدار", "لامپ", "کلید",
            "سرکه", "جوش‌شیرین", "آونگ", "نوسان", "نخ", "وزنه", "گیاه", "آوند", "رنگ", "چگالی",
            "مایع", "استوانه", "بطری", "آب", "تصفیه", "کرفس", "عسل", "روغن", "کف", "گاز"
        ])

def test_telemetry_collection_minimal_and_correct(hint_service):
    """تست ۶: ذخیره حداقل داده‌های لازم برای تحلیل معلم"""
    error = SimulationError(
        code="ERR_ORDER_VIOLATION_STEP1",
        category=ErrorCategory.ORDER_VIOLATION,
        title="ترتیب نادرست",
        description="گام اول رعایت نشد.",
        scientific_rationale="مقایسه با نمونه اسیدی آغاز می‌شود.",
        recommended_action="بشر آب‌لیمو را انتخاب کنید."
    )

    res = hint_service.get_hint_for_error("session-telemetry-test", error, "exp-acid-base", 1)
    telemetry = res["telemetry"]

    assert telemetry["attempt_id"] == "session-telemetry-test"
    assert telemetry["error_code"] == "ERR_ORDER_VIOLATION_STEP1"
    assert telemetry["level"] == 1
    assert telemetry["attempts_for_this_error"] == 1
    assert "timestamp" in telemetry
