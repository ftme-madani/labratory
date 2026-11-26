import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os
from backend.app.services.gemini_client import GeminiResult
from backend.app.config import settings

def test_scenario_1_red_litmus_on_acid_and_3level_escalation(client: TestClient, acid_base_experiment, student_auth_headers):
    """
    سناریوی ۱: استفاده اشتباه از تورنسل سرخ برای اسید و ارزیابی سه‌سطحی راهنما
    - خطای علمی: تورنسل سرخ در محیط اسیدی سرخ می‌ماند و خاصیت اسیدی را نشان نمی‌دهد.
    - بررسی ارتقای هوشمند سطح راهنما از سطح ۱ به ۲ و سپس ۳ در صورت تکرار اشتباه.
    """
    # آغاز تلاش
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    # افزودن وسایل به میز کار
    client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "ADD_TOOL", "source_id": "beaker_lemon"},
        headers=student_auth_headers
    )
    client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "ADD_TOOL", "source_id": "litmus_red"},
        headers=student_auth_headers
    )

    # اجرای کنش اشتباه (تورنسل سرخ در آب‌لیمو)
    action_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "DIP_INDICATOR", "source_id": "litmus_red", "target_id": "beaker_lemon"},
        headers=student_auth_headers
    )
    assert action_res.status_code == 200
    act_data = action_res.json()
    assert act_data["success"] is False
    assert act_data["error"]["code"] == "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"

    # ۱. درخواست راهنمای اول -> باید سطح ۱ (سقراطی) باشد
    h1_res = client.post(
        f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
        json={"error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID", "step_index": 1},
        headers=student_auth_headers
    )
    assert h1_res.status_code == 200
    h1 = h1_res.json()
    assert h1["level"] == 1
    assert h1["can_escalate"] is True
    assert "شناساگر" in h1["content"] or "رنگ" in h1["content"]

    # ۲. تکرار درخواست برای همین خطا -> باید سطح ۲ (سرنخ مفهومی) باشد
    h2_res = client.post(
        f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
        json={"error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID", "step_index": 1},
        headers=student_auth_headers
    )
    assert h2_res.status_code == 200
    h2 = h2_res.json()
    assert h2["level"] == 2
    assert h2["can_escalate"] is True

    # ۳. تکرار مجدد -> باید سطح ۳ (توضیح کامل علمی و معرفی تورنسل آبی) باشد
    h3_res = client.post(
        f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
        json={"error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID", "step_index": 1},
        headers=student_auth_headers
    )
    assert h3_res.status_code == 200
    h3 = h3_res.json()
    assert h3["level"] == 3
    assert h3["can_escalate"] is False
    assert "تورنسل آبی" in h3["content"] or "آبی" in h3["content"]

def test_scenario_2_blue_litmus_on_base(client: TestClient, acid_base_experiment, student_auth_headers):
    """
    سناریوی ۲: استفاده اشتباه از تورنسل آبی در محیط بازی
    """
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    # تکمیل گام ۱ با موفقیت
    client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "ADD_TOOL", "source_id": "beaker_lemon"}, headers=student_auth_headers)
    client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "ADD_TOOL", "source_id": "litmus_blue"}, headers=student_auth_headers)
    step1_res = client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "DIP_INDICATOR", "source_id": "litmus_blue", "target_id": "beaker_lemon"}, headers=student_auth_headers)
    assert step1_res.json()["is_step_completed"] is True

    # در گام ۲: استفاده از تورنسل آبی در آب‌صابون
    client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "ADD_TOOL", "source_id": "beaker_soap"}, headers=student_auth_headers)
    step2_res = client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "DIP_INDICATOR", "source_id": "litmus_blue", "target_id": "beaker_soap"}, headers=student_auth_headers)
    assert step2_res.json()["success"] is False
    assert step2_res.json()["error"]["code"] == "ERR_INEFFECTIVE_INDICATOR_BLUE_ON_BASE"

    # درخواست راهنما
    hint_res = client.post(
        f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
        json={"error_code": "ERR_INEFFECTIVE_INDICATOR_BLUE_ON_BASE", "step_index": 2},
        headers=student_auth_headers
    )
    assert hint_res.status_code == 200
    assert hint_res.json()["level"] == 1

def test_scenario_3_wrong_order_step1(client: TestClient, acid_base_experiment, student_auth_headers):
    """
    سناریوی ۳: رعایت نکردن ترتیب مراحل و شروع با آب‌صابون به جای آب‌لیمو
    """
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "ADD_TOOL", "source_id": "beaker_soap"}, headers=student_auth_headers)
    client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "ADD_TOOL", "source_id": "litmus_red"}, headers=student_auth_headers)

    res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "DIP_INDICATOR", "source_id": "litmus_red", "target_id": "beaker_soap"},
        headers=student_auth_headers
    )
    assert res.json()["success"] is False
    assert res.json()["error"]["code"] == "ERR_ORDER_VIOLATION_STEP1"

    hint_res = client.post(
        f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
        json={"error_code": "ERR_ORDER_VIOLATION_STEP1", "step_index": 1},
        headers=student_auth_headers
    )
    assert hint_res.status_code == 200
    assert "ترتیب" in hint_res.json()["content"] or "گام" in hint_res.json()["content"] or "دستورالعمل" in hint_res.json()["content"]

def test_scenario_4_missing_precondition(client: TestClient, acid_base_experiment, student_auth_headers):
    """
    سناریوی ۴: اقدام به آزمایش بدون انتقال شناساگر به روی میز کار
    """
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "ADD_TOOL", "source_id": "beaker_lemon"}, headers=student_auth_headers)
    # شناساگر روی میز نیست
    res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "DIP_INDICATOR", "source_id": "litmus_blue", "target_id": "beaker_lemon"},
        headers=student_auth_headers
    )
    assert res.json()["success"] is False
    assert res.json()["error"]["code"] == "ERR_PRECONDITION_INDICATOR_NOT_ON_BENCH"

def test_scenario_5_perfect_step_by_step_completion(client: TestClient, acid_base_experiment, student_auth_headers):
    """
    سناریوی ۵: اجرای کامل، علمی و بی‌نقص هر ۳ گام آزمایش اسید و باز
    """
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    # چیدمان کامل میز کار
    tools = ["beaker_lemon", "beaker_soap", "beaker_water", "litmus_blue", "litmus_red"]
    for t in tools:
        client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "ADD_TOOL", "source_id": t}, headers=student_auth_headers)

    # گام ۱: تورنسل آبی در آب‌لیمو -> سرخ
    step1 = client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "DIP_INDICATOR", "source_id": "litmus_blue", "target_id": "beaker_lemon"}, headers=student_auth_headers)
    assert step1.json()["success"] is True
    assert step1.json()["is_step_completed"] is True
    assert step1.json()["measurements"]["solution_ph"] == 2.5
    assert step1.json()["measurements"]["color_name_fa"] == "سرخ"

    # گام ۲: تورنسل سرخ در آب‌صابون -> آبی
    step2 = client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "DIP_INDICATOR", "source_id": "litmus_red", "target_id": "beaker_soap"}, headers=student_auth_headers)
    assert step2.json()["success"] is True
    assert step2.json()["is_step_completed"] is True
    assert step2.json()["measurements"]["solution_ph"] == 9.5
    assert step2.json()["measurements"]["color_name_fa"] == "آبی"

    # گام ۳: تورنسل در آب‌مقطر خنثی
    step3 = client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "DIP_INDICATOR", "source_id": "litmus_blue", "target_id": "beaker_water"}, headers=student_auth_headers)
    assert step3.json()["success"] is True
    assert step3.json()["is_terminal"] is True

    # نهایی‌سازی نشست
    finish_res = client.post(f"/api/v1/simulation/attempts/{attempt_id}/finish", headers=student_auth_headers)
    assert finish_res.status_code == 200
    assert finish_res.json()["status"] == "COMPLETED"
    assert finish_res.json()["score"] == 100.0

def test_scenario_6_api_offline_fallback_zero_downtime(client: TestClient, acid_base_experiment, student_auth_headers):
    """
    سناریوی ۶: آزمایش تاب‌آوری و قطع سرویس هوش مصنوعی (قطع اینترنت، عدم کلید، تایم‌اوت)
    - برنامه تحت هیچ شرایطی نباید ۵۰۰ بدهد و باید از قوانین کتاب درسی پاسخ دهد.
    """
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    # شبیه‌سازی قطع کامل ارتباط با هوش مصنوعی گوگل
    with patch("backend.app.services.gemini_client.GeminiClient.generate_content", return_value=None):
        res = client.post(
            f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
            json={"error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID", "step_index": 1},
            headers=student_auth_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["level"] == 1
        assert "🤔 پرسش برای تفکر: " in data["content"]

def test_scenario_7_api_key_security_leak_audit(client: TestClient, student_auth_headers, teacher_auth_headers):
    """
    سناریوی ۷: بازرسی امنیتی؛ هیچ اندپوینتی نباید کلید GEMINI_API_KEY را به کلاینت نشت دهد
    """
    real_or_configured_key = settings.GEMINI_API_KEY
    if not real_or_configured_key:
        return

    # ۱. بررسی اندپوینت هلث
    health = client.get("/api/health").json()
    assert real_or_configured_key not in str(health)

    # ۲. بررسی پروفایل کاربر
    me = client.get("/api/v1/auth/me", headers=student_auth_headers).json()
    assert real_or_configured_key not in str(me)

    # ۳. بررسی تنظیمات گیت‌ایگنور
    root_gitignore_path = "d:/www/library/.gitignore"
    if os.path.exists(root_gitignore_path):
        with open(root_gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert ".env" in content
            assert "*.db" in content
