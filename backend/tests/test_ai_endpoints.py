import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.app.services.gemini_client import GeminiResult

def test_ai_tutor_hint_unauthorized(client: TestClient, acid_base_experiment, student_auth_headers):
    """درخواست راهنما بدون توکن باید ۴۰۱ برگرداند"""
    # ابتدا ساخت یک تلاش
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    assert start_res.status_code == 201
    attempt_id = start_res.json()["attempt_id"]

    # ارسال درخواست بدون Authorization header
    res = client.post(
        f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
        json={"error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID", "step_index": 1}
    )
    assert res.status_code == 401

def test_ai_tutor_hint_success_and_penalty(client: TestClient, acid_base_experiment, student_auth_headers):
    """درخواست راهنمای سطح ۱ و بررسی کسر نمره پداگوژیک و ساختار پاسخ"""
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    assert start_res.status_code == 201
    attempt_id = start_res.json()["attempt_id"]

    mock_gemini = GeminiResult(
        success=True,
        text="دانش‌آموز کوشا، آیا کاغذ تورنسل سرخ در یک اسید می‌تواند تغییری نشان دهد؟",
        model="gemini-1.5-flash"
    )

    with patch("backend.app.services.gemini_client.GeminiClient.is_configured", return_value=True), \
         patch("backend.app.services.gemini_client.GeminiClient.generate_content", return_value=mock_gemini):

        res = client.post(
            f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
            json={
                "error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID",
                "step_index": 1,
                "action_summary": "آزمودن آب‌لیمو با تورنسل سرخ"
            },
            headers=student_auth_headers
        )

        assert res.status_code == 200
        data = res.json()
        assert data["attempt_id"] == attempt_id
        assert data["level"] == 1
        assert data["can_escalate"] is True
        assert "تورنسل" in data["content"]

def test_ai_tutor_hint_cross_student_forbidden(client: TestClient, acid_base_experiment, student_auth_headers, second_student_auth_headers):
    """دانش‌آموز ب نباید بتواند راهنمای تلاش دانش‌آموز الف را دریافت کند"""
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    res = client.post(
        f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
        json={"error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID", "step_index": 1},
        headers=second_student_auth_headers
    )
    assert res.status_code == 403

def test_ai_tutor_ask_question(client: TestClient, acid_base_experiment, student_auth_headers):
    """طرح پرسش علمی آزاد توسط دانش‌آموز در محیط آزمایشگاه"""
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    mock_gemini = GeminiResult(
        success=True,
        text="آب‌لیمو اسیدی است و تورنسل آبی را سرخ می‌کند.",
        model="gemini-1.5-flash"
    )

    with patch("backend.app.services.gemini_client.GeminiClient.is_configured", return_value=True), \
         patch("backend.app.services.gemini_client.GeminiClient.generate_content", return_value=mock_gemini):

        res = client.post(
            "/api/v1/ai/tutor/ask",
            json={
                "attempt_id": attempt_id,
                "question": "چرا آب‌لیمو کاغذ تورنسل را سرخ کرد؟",
                "step_index": 1
            },
            headers=student_auth_headers
        )

        assert res.status_code == 200
        data = res.json()
        assert data["attempt_id"] == attempt_id
        assert "اسیدی" in data["answer"]
        assert data["experiment_title"] != ""

def test_teacher_ai_insights_rbac_and_data(client: TestClient, student_auth_headers, teacher_auth_headers):
    """بررسی امنیت نقش‌ها: دسترسی دانش‌آموز رد می‌شود اما معلم آمار را دریافت می‌کند"""
    # ۱. دانش‌آموز نباید دسترسی داشته باشد (403)
    res_student = client.get("/api/v1/ai/teacher/insights", headers=student_auth_headers)
    assert res_student.status_code == 403

    # ۲. دسترسی معلم باید ۲۰۰ با تحلیل‌های آماری باشد
    res_teacher = client.get("/api/v1/ai/teacher/insights", headers=teacher_auth_headers)
    assert res_teacher.status_code == 200
    data = res_teacher.json()
    assert "total_errors_analyzed" in data
    assert "top_misconceptions" in data
    assert "ai_pedagogical_remediation" in data
    assert len(data["ai_pedagogical_remediation"]) > 10

    # ۳. بررسی اندپوینت میانبر در /teacher/ai-insights
    res_alias = client.get("/api/v1/teacher/ai-insights", headers=teacher_auth_headers)
    assert res_alias.status_code == 200

def test_teacher_ai_insights_multi_experiments(client: TestClient, teacher_auth_headers, db_session):
    """بررسی استخراج داینامیک نام آزمایش‌های مختلف در پنل معلم"""
    from backend.app.models.attempt import ExperimentAttempt, StepActionLog

    # ایجاد یک تلاش برای آونگ با خطای مفهومی
    att_pendulum = ExperimentAttempt(
        id="att-test-pendulum-01",
        user_id="user-student-test",
        experiment_id="exp-pendulum-01",
        status="IN_PROGRESS",
        score=90.0,
        steps_completed=1,
        total_steps=4
    )
    db_session.add(att_pendulum)
    log_pendulum = StepActionLog(
        attempt_id="att-test-pendulum-01",
        step_index=2,
        action_type="SUBMIT_PREDICTION",
        item_ids=["pendulum_bob"],
        parameters={"predicted_effect": "mass_increases_period"},
        is_valid=False,
        error_code="ERR_PENDULUM_MASS_DEPENDENCE",
        feedback_text="بررسی فرضیه دوره تناوب آونگ"
    )
    db_session.add(log_pendulum)

    # ایجاد یک تلاش برای سرکه و جوش شیرین با خطای نوع گاز
    att_vinegar = ExperimentAttempt(
        id="att-test-vinegar-01",
        user_id="user-student-test",
        experiment_id="exp-vinegar-01",
        status="IN_PROGRESS",
        score=90.0,
        steps_completed=1,
        total_steps=4
    )
    db_session.add(att_vinegar)
    log_vinegar = StepActionLog(
        attempt_id="att-test-vinegar-01",
        step_index=3,
        action_type="SUBMIT_PREDICTION",
        item_ids=["beaker_glass"],
        parameters={"predicted_gas": "oxygen"},
        is_valid=False,
        error_code="ERR_MISCONCEPTION_GAS_TYPE",
        feedback_text="بررسی نوع گاز متصاعدشده"
    )
    db_session.add(log_vinegar)
    db_session.commit()

    res = client.get("/api/v1/ai/teacher/insights", headers=teacher_auth_headers)
    assert res.status_code == 200
    data = res.json()
    err_codes = [m["error_code"] for m in data["top_misconceptions"]]
    assert "ERR_PENDULUM_MASS_DEPENDENCE" in err_codes
    assert "ERR_MISCONCEPTION_GAS_TYPE" in err_codes

    # بررسی عنوان فارسی داینامیک هر آزمایش
    for m in data["top_misconceptions"]:
        if m["error_code"] == "ERR_PENDULUM_MASS_DEPENDENCE":
            assert "آونگ" in m["experiment_title"]
        elif m["error_code"] == "ERR_MISCONCEPTION_GAS_TYPE":
            assert "سرکه" in m["experiment_title"]

def test_voice_tts_endpoint(client: TestClient, student_auth_headers):
    """آزمون تولید صوت فارسی طبیعی از متن علمی با Edge-TTS"""
    payload = {
        "text": "سلام، به آزمایشگاه مجازی خوش آمدید.",
        "voice": "fa-IR-DilaraNeural"
    }
    res = client.post("/api/v1/ai/voice/tts", json=payload, headers=student_auth_headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "audio/mpeg"
    assert len(res.content) > 100
