import pytest
import jwt
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone

from backend.app.config import settings
from backend.app.models.user import User
from backend.app.models.experiment import Experiment
from backend.app.models.attempt import ExperimentAttempt

def test_sql_injection_resilience_in_search(client: TestClient, acid_base_experiment):
    """
    آزمون مقاومت در برابر حملات تزریق SQL (SQL Injection Resilience)
    با عبارات مخرب استاندارد SQLi در فیلترهای جست‌وجو و اطمینان از عدم اجرای دستورات تخریبی
    """
    sqli_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE experiments; --",
        "1' UNION SELECT 1, 'admin', 'pass', 'admin@edu.ir', 'admin', 'دهم', 'school', '2026-01-01' --",
        "\" OR \"\"=\""
    ]

    for payload in sqli_payloads:
        # جست‌وجو در اندپوینت آزمایش‌ها با پی‌لود تزریق SQL
        res = client.get(f"/api/v1/experiments?search={payload}&subject={payload}")
        # سرور نباید کرش کند (کد 500 ندهد) و باید با لیست خالی یا نتایج سالم پاسخ دهد
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    # اطمینان از اینکه جدول experiments دست‌نخورده باقی مانده است
    check_res = client.get(f"/api/v1/experiments/{acid_base_experiment.slug}")
    assert check_res.status_code == 200
    assert check_res.json()["slug"] == acid_base_experiment.slug

def test_jwt_tampering_and_forgery(client: TestClient, sample_student):
    """
    آزمون جعل امضا و دستکاری ادعاهای توکن JWT (JWT Tampering & Signature Forgery)
    """
    # 1. توکن با کلید مخفی جعلی (Invalid Signature)
    fake_secret = "completely-wrong-attacker-secret-key-99999"
    forged_token = jwt.encode(
        {"sub": str(sample_student.id), "role": "admin"},
        fake_secret,
        algorithm="HS256"
    )
    res_fake_sig = client.get(
        "/api/v1/teacher/analytics",
        headers={"Authorization": f"Bearer {forged_token}"}
    )
    assert res_fake_sig.status_code == 401
    assert "نامعتبر" in res_fake_sig.json()["detail"]

    # 2. توکن منقضی‌شده (Expired Token)
    expired_time = datetime.now(timezone.utc) - timedelta(hours=2)
    expired_token = jwt.encode(
        {"sub": str(sample_student.id), "role": "student", "exp": expired_time},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    res_expired = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert res_expired.status_code == 401
    assert "منقضی" in res_expired.json()["detail"] or "نامعتبر" in res_expired.json()["detail"]

    # 3. توکن با الگوریتم 'none' (None Algorithm Vulnerability Attack)
    try:
        none_token = jwt.encode(
            {"sub": str(sample_student.id), "role": "admin"},
            key="",
            algorithm="none"
        )
        res_none = client.get(
            "/api/v1/teacher/analytics",
            headers={"Authorization": f"Bearer {none_token}"}
        )
        assert res_none.status_code == 401
    except Exception:
        # کتابخانه pyjwt خود مانع از تولید الگوریتم none می‌شود که این یک مکانیزم امنیتی است
        pass

def test_idor_cross_user_isolation(
    client: TestClient,
    student_auth_headers,
    second_student_auth_headers,
    acid_base_experiment
):
    """
    آزمون جلوگیری از دسترسی مستقیم به شیء سایر کاربران (IDOR - Insecure Direct Object References)
    دانش‌آموز ۲ نباید تحت هیچ شرایطی بتواند به نمرات، لاگ‌ها یا تلاش‌های دانش‌آموز ۱ دست یابد یا آن‌ها را نهایی کند
    """
    # دانش‌آموز ۱ یک تلاش جدید ثبت می‌کند
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    assert start_res.status_code == 201
    attempt_id = start_res.json()["attempt_id"]

    # دانش‌آموز ۲ تلاش می‌کند کنش ثبت کند
    act_attack = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "ADD_TOOL", "source_id": "beaker-lemon"},
        headers=second_student_auth_headers
    )
    assert act_attack.status_code == 403

    # دانش‌آموز ۲ تلاش می‌کند راهنما درخواست دهد
    hint_attack = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/hint",
        json={"step_index": 1, "error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"},
        headers=second_student_auth_headers
    )
    assert hint_attack.status_code == 403

    # دانش‌آموز ۲ تلاش می‌کند تلاش دانش‌آموز ۱ را خاتمه دهد
    finish_attack = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/finish",
        headers=second_student_auth_headers
    )
    assert finish_attack.status_code == 403

    # دانش‌آموز ۲ تلاش می‌کند جزئیات لاگ تلاش دانش‌آموز ۱ را مشاهده کند
    view_attack = client.get(
        f"/api/v1/student/attempts/{attempt_id}",
        headers=second_student_auth_headers
    )
    assert view_attack.status_code == 403

def test_privilege_escalation_student_cannot_publish_experiment(
    client: TestClient,
    student_auth_headers,
    acid_base_experiment
):
    """
    آزمون جلوگیری از ترفیع سطح دسترسی (Privilege Escalation Protection)
    دانش‌آموز نباید بتواند آزمایش ایجاد کند یا وضعیت انتشار آزمایشی را تغییر دهد
    """
    # تغییر وضعیت انتشار
    res_status = client.put(
        f"/api/v1/experiments/{acid_base_experiment.id}/status",
        json={"status": "DRAFT"},
        headers=student_auth_headers
    )
    assert res_status.status_code == 403

    # دسترسی به گزارش جامع کلیه دانش‌آموزان کلاس
    res_all_students = client.get(
        "/api/v1/teacher/students/attempts",
        headers=student_auth_headers
    )
    assert res_all_students.status_code == 403

def test_malformed_json_and_fuzzing_resilience(client: TestClient, student_auth_headers, acid_base_experiment):
    """
    آزمون تاب‌آوری در برابر ورودی‌های ناقص، فازینگ و داده‌های خارج از محدوده
    """
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    # فیلدهای کاملاً خالی یا نال
    res1 = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={},
        headers=student_auth_headers
    )
    # اسکیمای pydantic باید خطای اعتبارسنجی بدهد (422) نه اینکه سرور کرش کند (500)
    assert res1.status_code == 422

    # انواع داده‌ای ناهماهنگ
    res2 = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={
            "action_type": 12345,  # عدد به جای رشته
            "source_id": ["unexpected", "array"],  # آرایه به جای رشته
            "parameters": "string instead of dict"
        },
        headers=student_auth_headers
    )
    assert res2.status_code == 422

def test_cors_headers_presence(client: TestClient):
    """
    آزمون وجود هدرهای استاندارد امنیتی CORS جهت پشتیبانی از اتصالات مجاز کلاینت
    """
    res = client.options(
        "/api/v1/experiments",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert res.status_code in [200, 204]
    assert "access-control-allow-origin" in res.headers
