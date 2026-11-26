import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app.models.user import User
from backend.app.security import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_classroom_data():
    db = SessionLocal()
    # Create a teacher and a student if not already present
    teacher = db.query(User).filter(User.email == "test_teacher_cls@edu.ir").first()
    if not teacher:
        teacher = User(
            username="teacher_cls_test",
            email="test_teacher_cls@edu.ir",
            hashed_password=get_password_hash("Pass123456"),
            full_name="استاد حسینی",
            role="teacher",
            grade="نهم",
            school_name="دبیرستان علامه حلی",
            class_code="CLASS-HELLI-9"
        )
        db.add(teacher)

    student = db.query(User).filter(User.email == "test_student_cls@school.ir").first()
    if not student:
        student = User(
            username="student_cls_test",
            email="test_student_cls@school.ir",
            hashed_password=get_password_hash("Pass123456"),
            full_name="کیانوش رستمی",
            role="student",
            grade="نهم",
            school_name="دبیرستان علامه حلی"
        )
        db.add(student)

    db.commit()
    t_id, s_id = teacher.id, student.id
    db.close()
    return {"teacher_id": t_id, "student_id": s_id}

def test_teacher_creates_classroom_experiment_and_student_enters(setup_classroom_data):
    # 1. Login as teacher
    login_res = client.post("/api/v1/auth/login", json={
        "email": "test_teacher_cls@edu.ir",
        "password": "Pass123456"
    })
    assert login_res.status_code == 200
    teacher_token = login_res.json()["access_token"]
    t_headers = {"Authorization": f"Bearer {teacher_token}"}

    # 2. Login as student
    s_login_res = client.post("/api/v1/auth/login", json={
        "email": "test_student_cls@school.ir",
        "password": "Pass123456"
    })
    assert s_login_res.status_code == 200
    student_token = s_login_res.json()["access_token"]
    s_headers = {"Authorization": f"Bearer {student_token}"}

    # 3. Teacher creates a private classroom experiment with class_code
    import uuid
    uid = uuid.uuid4().hex[:6]
    class_code = f"CLS-HELLI-{uid.upper()}"
    create_payload = {
        "slug": f"exp-cls-test-{uid}",
        "title": "آزمایش اختصاصی زیست‌شناسی کلاس نهم حلی",
        "subject": "زیست",
        "grade": "نهم",
        "difficulty": "متوسط",
        "duration_minutes": 20,
        "summary": "آزمایش بررسی آوندهای چوبی ویژه کلاس",
        "textbook_source": {
            "book": "علوم تجربی نهم",
            "grade": "نهم",
            "chapter": "فصل گیاهان",
            "chapterNumber": 5,
            "page": 55
        },
        "objectives": ["مشاهده آوندها"],
        "safety_notes": ["احتیاط عمومی"],
        "available_tools": [],
        "steps_config": [{"index": 1, "instruction": "مرحله اول"}],
        "thumbnail_type": "leaf",
        "status": "PUBLISHED",
        "class_code": class_code,
        "is_class_only": True
    }
    exp_res = client.post("/api/v1/experiments", json=create_payload, headers=t_headers)
    assert exp_res.status_code == 201
    created_exp = exp_res.json()
    assert created_exp["class_code"] == class_code
    assert created_exp["is_class_only"] is True

    # 4. Student joins via class code endpoint
    join_res = client.post("/api/v1/experiments/join-class", json={"class_code": class_code}, headers=s_headers)
    assert join_res.status_code == 200
    joined_exp = join_res.json()
    assert joined_exp["slug"] == created_exp["slug"]

    # 5. Student starts attempt for this class experiment
    start_res = client.post("/api/v1/simulation/attempts/start", json={
        "experiment_slug": joined_exp["slug"],
        "class_code": class_code
    }, headers=s_headers)
    assert start_res.status_code == 201
    attempt_id = start_res.json()["attempt_id"]

    # 6. Student finishes attempt
    finish_res = client.post(f"/api/v1/simulation/attempts/{attempt_id}/finish", headers=s_headers)
    assert finish_res.status_code == 200

    # 7. Teacher queries attempts filtered by class_code
    attempts_res = client.get(f"/api/v1/teacher/students/attempts?class_code={class_code}", headers=t_headers)
    assert attempts_res.status_code == 200
    attempts_list = attempts_res.json()
    assert len(attempts_list) >= 1
    found_att = next(a for a in attempts_list if a["id"] == attempt_id)
    assert found_att["student_name"] == "کیانوش رستمی"
    assert found_att["student_grade"] == "نهم"
    assert found_att["student_school"] == "دبیرستان علامه حلی"
    assert found_att["class_code"] == class_code

    # 8. Teacher grades and submits feedback
    feedback_text = "آفرین کیانوش جان! فرضیه‌سازی و مراحل آزمایش را به درستی انجام دادی."
    fb_res = client.put(f"/api/v1/teacher/students/attempts/{attempt_id}/feedback", json={
        "teacher_feedback": feedback_text
    }, headers=t_headers)
    assert fb_res.status_code == 200
    assert fb_res.json()["teacher_feedback"] == feedback_text

    # 9. Verify audit endpoint includes student name and teacher feedback
    audit_res = client.get(f"/api/v1/teacher/students/attempts/{attempt_id}", headers=t_headers)
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    assert audit_data["student_name"] == "کیانوش رستمی"
    assert audit_data["teacher_feedback"] == feedback_text
