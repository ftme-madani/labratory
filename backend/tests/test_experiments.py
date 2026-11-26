import pytest
from fastapi.testclient import TestClient

def test_list_experiments_public(client: TestClient, acid_base_experiment):
    response = client.get("/api/v1/experiments")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["slug"] == acid_base_experiment.slug
    assert data[0]["status"] == "PUBLISHED"

def test_list_experiments_filter_subject(client: TestClient, acid_base_experiment):
    response = client.get("/api/v1/experiments?subject=شیمی")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["subject"] == "شیمی"

    # فیلتر موضوعی که وجود ندارد
    response2 = client.get("/api/v1/experiments?subject=زمین‌شناسی")
    assert response2.status_code == 200
    assert len(response2.json()) == 0

def test_get_experiment_detail_by_slug(client: TestClient, acid_base_experiment):
    response = client.get(f"/api/v1/experiments/{acid_base_experiment.slug}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == acid_base_experiment.title
    assert data["textbook_source"]["page"] == 6

def test_get_experiment_detail_not_found(client: TestClient):
    response = client.get("/api/v1/experiments/non-existent-experiment-xyz")
    assert response.status_code == 404

def test_teacher_create_experiment_draft(client: TestClient, teacher_auth_headers):
    payload = {
        "slug": "exp-density-archimedes",
        "title": "چگالی و اصل ارشمیدس در مایعات",
        "subject": "فیزیک",
        "grade": "هفتم",
        "difficulty": "متوسط",
        "duration_minutes": 25,
        "summary": "اندازه‌گیری جرم و حجم اجسام نامنظم با استوانه مدرج",
        "textbook_source": {
            "book": "علوم تجربی هفتم",
            "grade": "هفتم",
            "chapter": "اندازه‌گیری در علوم",
            "chapterNumber": 2,
            "page": 12
        },
        "objectives": ["محاسبه چگالی با رابطه m/v"],
        "safety_notes": ["هنگام کار با استوانه مدرج شیشه‌ای مراقب شکستگی باشید."],
        "available_tools": [],
        "steps_config": [],
        "thumbnail_type": "flask",
        "status": "DRAFT"
    }
    response = client.post("/api/v1/experiments", json=payload, headers=teacher_auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "exp-density-archimedes"
    assert data["status"] == "DRAFT"

def test_student_cannot_create_experiment(client: TestClient, student_auth_headers):
    payload = {
        "slug": "unauthorized-exp",
        "title": "آزمایش غیرمجاز",
        "subject": "شیمی",
        "grade": "هشتم",
        "summary": "تست دسترسی غیرمجاز دانش‌آموز",
        "textbook_source": {"book": "علوم", "grade": "هشتم", "chapter": "۱", "chapterNumber": 1, "page": 1}
    }
    response = client.post("/api/v1/experiments", json=payload, headers=student_auth_headers)
    assert response.status_code == 403

def test_teacher_update_status(client: TestClient, teacher_auth_headers, acid_base_experiment):
    response = client.put(
        f"/api/v1/experiments/{acid_base_experiment.id}/status",
        json={"status": "VERIFIED"},
        headers=teacher_auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "VERIFIED"
