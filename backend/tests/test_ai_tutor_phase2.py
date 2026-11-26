import pytest
from unittest.mock import patch, MagicMock
from simulation_engine.hints.ai_tutor import PrivacyAnonymizer, PedagogicalPromptBuilder
from simulation_engine.hints.llm_adapter import ExternalLLMAdapter, OfflineRuleLLMAdapter
from simulation_engine.hints.engine import IntelligentHintService
from simulation_engine.schema import SimulationError, ErrorCategory
from backend.app.services.gemini_client import GeminiResult

def test_privacy_anonymizer_strips_all_pii():
    """تست تضمین عدم نشت اطلاعات هویتی و پاک‌سازی کامل PII"""
    raw_payload = {
        "user_id": 42,
        "name": "علیرضا",
        "full_name": "علیرضا محمدی",
        "email": "alireza@school.ir",
        "phone": "09120000000",
        "school": "دبیرستان شهید بهشتی",
        "password": "SecretPassword123",
        "experiment_title": "شناسایی اسیدها و بازها",
        "step_index": 1,
        "error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"
    }

    sanitized = PrivacyAnonymizer.sanitize_context(raw_payload)

    # اطلاعات هویتی نباید در خروجی وجود داشته باشند
    assert "name" not in sanitized
    assert "full_name" not in sanitized
    assert "email" not in sanitized
    assert "phone" not in sanitized
    assert "school" not in sanitized
    assert "password" not in sanitized

    # شناسه کاربر به هش ناشناس و برگشت‌ناپذیر تبدیل شده باشد
    assert "user_id" not in sanitized
    assert "anonymous_student_id" in sanitized
    assert sanitized["anonymous_student_id"].startswith("std-anon-")

    # اطلاعات علمی آزمایش بدون تغییر حفظ شوند
    assert sanitized["experiment_title"] == "شناسایی اسیدها و بازها"
    assert sanitized["error_code"] == "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"

def test_pedagogical_prompt_builder_rules():
    """تست ساختار پرامپت پداگوژیک و تفکیک سطوح آموزشی"""
    prompt_l1 = PedagogicalPromptBuilder.build_hint_prompt({
        "level": 1,
        "raw_hint": "آیا کاغذ سرخ در اسید تغییر رنگ می‌دهد؟",
        "error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID",
        "experiment_title": "شناسایی اسید و باز",
        "step_index": 1,
        "action_summary": "آزمودن آب‌لیمو با تورنسل سرخ",
        "scientific_rationale": "تورنسل سرخ در اسید سرخ می‌ماند."
    })
    assert "سطح ۱: سؤال هدایت‌کننده" in prompt_l1
    assert "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID" in prompt_l1

    prompt_l3 = PedagogicalPromptBuilder.build_hint_prompt({
        "level": 3,
        "raw_hint": "برای اسید باید از تورنسل آبی استفاده کنی.",
        "error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID",
        "experiment_title": "شناسایی اسید و باز",
        "step_index": 1
    })
    assert "سطح ۳: توضیح کامل علمی" in prompt_l3

def test_external_llm_adapter_success_with_gemini():
    """تست پاسخ‌دهی موفق آداپتور هوش مصنوعی هنگام فعال بودن Gemini"""
    mock_result = GeminiResult(
        success=True,
        text="دوست عزیزم، به رنگ اولیه این شناساگر فکر کن؛ به نظرت چه شناساگری در اسید تغییر می‌کند؟",
        model="gemini-1.5-flash",
        latency_ms=120.0
    )

    with patch("backend.app.services.gemini_client.GeminiClient.is_configured", return_value=True), \
         patch("backend.app.services.gemini_client.GeminiClient.generate_content", return_value=mock_result):

        adapter = ExternalLLMAdapter()
        output = adapter.generate_explanation({
            "raw_hint": "کاغذ تورنسل سرخ فقط در مواجهه با بازها تغییر رنگ می‌دهد.",
            "level": 1,
            "error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"
        })

        assert output == mock_result.text
        assert "شناساگر" in output

def test_external_llm_adapter_fallback_on_gemini_failure():
    """تست فعال شدن خودکار فال‌بک آفلاین هنگام عدم پاسخ‌گویی Gemini"""
    with patch("backend.app.services.gemini_client.GeminiClient.is_configured", return_value=True), \
         patch("backend.app.services.gemini_client.GeminiClient.generate_content", return_value=None):

        adapter = ExternalLLMAdapter()
        output = adapter.generate_explanation({
            "raw_hint": "کاغذ تورنسل سرخ فقط در مواجهه با بازها تغییر رنگ می‌دهد.",
            "level": 2,
            "error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"
        })

        # باید بدون معطلی و با پیشوند سرنخ آموزشی کتاب درسی بازگردد
        assert "💡 سرنخ آموزشی: " in output
        assert "کاغذ تورنسل سرخ" in output

def test_intelligent_hint_service_integration():
    """تست یکپارچگی سرویس راهنمایی سه‌سطحی با آداپتور هوشمند"""
    sim_error = SimulationError(
        code="ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID",
        category=ErrorCategory.WRONG_TOOL,
        title="شناساگر نامناسب",
        description="استفاده از تورنسل سرخ برای آب‌لیمو",
        scientific_rationale="کاغذ تورنسل سرخ در محیط اسیدی سرخ می‌ماند.",
        recommended_action="از کاغذ تورنسل آبی استفاده کنید."
    )

    hint_service = IntelligentHintService()

    # درخواست اول: باید سطح ۱ (سقراطی) بدهد
    h1 = hint_service.get_hint_for_error("att-test-123", sim_error, "exp-acid-base", 1)
    assert h1["level"] == 1
    assert h1["error_code"] == "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"
    assert h1["can_escalate"] is True
    assert len(h1["content"]) > 10

    # درخواست دوم برای همین خطا در همان سشن: باید به سطح ۲ ارتقا یابد
    h2 = hint_service.get_hint_for_error("att-test-123", sim_error, "exp-acid-base", 1)
    assert h2["level"] == 2
    assert h2["can_escalate"] is True

    # درخواست سوم: باید به سطح ۳ ارتقا یابد و can_escalate=False شود
    h3 = hint_service.get_hint_for_error("att-test-123", sim_error, "exp-acid-base", 1)
    assert h3["level"] == 3
    assert h3["can_escalate"] is False

def test_student_question_answering_and_teacher_insights():
    """تست پاسخ‌گویی به سؤالات کانسپچوال و تولید بینش‌های آموزشی معلم"""
    mock_qa = GeminiResult(
        success=True,
        text="آب‌لیمو به دلیل وجود اسید سیتریک دارای خصلت اسیدی با pH حدود ۲.۵ است.",
        model="gemini-1.5-flash"
    )

    with patch("backend.app.services.gemini_client.GeminiClient.is_configured", return_value=True), \
         patch("backend.app.services.gemini_client.GeminiClient.generate_content", return_value=mock_qa):

        adapter = ExternalLLMAdapter()
        answer = adapter.answer_question(
            "آیا آب‌لیمو اسید است یا باز؟",
            {"title": "اسیدها و بازها", "current_step": 1}
        )
        assert "اسید سیتریک" in answer

        # تست فال‌بک بینش‌های معلم در صورت نبود آمار
        insights = adapter.generate_teacher_insights([])
        assert "بر اساس داده‌های کلاسی" in insights
