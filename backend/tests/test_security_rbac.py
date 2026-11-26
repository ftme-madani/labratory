import pytest
from fastapi.testclient import TestClient

def test_student_forbidden_from_teacher_analytics(client: TestClient, student_auth_headers):
    response = client.get("/api/v1/teacher/analytics", headers=student_auth_headers)
    assert response.status_code == 403
    assert "دسترسی غیرمجاز" in response.json()["detail"]

def test_teacher_allowed_to_access_analytics(client: TestClient, teacher_auth_headers):
    response = client.get("/api/v1/teacher/analytics", headers=teacher_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_students" in data
    assert "active_experiments_count" in data

def test_prevent_cross_student_tampering(
    client: TestClient,
    student_auth_headers,
    second_student_auth_headers,
    acid_base_experiment
):
    # دانش‌آموز اول یک تلاش جدید می‌سازد
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    # دانش‌آموز دوم تلاش می‌کند روی تلاش دانش‌آموز اول کنش ثبت کند
    tamper_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "ADD_TOOL", "source_id": "beaker-lemon"},
        headers=second_student_auth_headers
    )
    assert tamper_res.status_code == 403
    assert "سایر کاربران" in tamper_res.json()["detail"]

    # دانش‌آموز دوم تلاش می‌کند جزئیات تلاش دانش‌آموز اول را ببیند
    spy_res = client.get(
        f"/api/v1/student/attempts/{attempt_id}",
        headers=second_student_auth_headers
    )
    assert spy_res.status_code == 403

def test_teacher_can_audit_student_attempt(
    client: TestClient,
    student_auth_headers,
    teacher_auth_headers,
    acid_base_experiment
):
    # دانش‌آموز تلاشی ثبت می‌کند
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    # معلم برای بررسی پداگوژیک به عنوان ناظر مجاز است
    teacher_view_res = client.get(
        f"/api/v1/simulation/attempts/{attempt_id}/state",
        headers=teacher_auth_headers
    )
    assert teacher_view_res.status_code == 200

    # ممیزی مستقیم از روتر دبیر
    audit_res = client.get(
        f"/api/v1/teacher/students/attempts/{attempt_id}",
        headers=teacher_auth_headers
    )
    assert audit_res.status_code == 200
    assert audit_res.json()["id"] == attempt_id

    # بررسی دسترسی غیرمجاز دانش‌آموز به مسیر ممیزی دبیر
    forbidden_audit = client.get(
        f"/api/v1/teacher/students/attempts/{attempt_id}",
        headers=student_auth_headers
    )
    assert forbidden_audit.status_code == 403

def test_invalid_bearer_token(client: TestClient):
    fake_headers = {"Authorization": "Bearer this-is-a-completely-invalid-token"}
    response = client.get("/api/v1/auth/me", headers=fake_headers)
    assert response.status_code == 401

def test_missing_auth_header(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
