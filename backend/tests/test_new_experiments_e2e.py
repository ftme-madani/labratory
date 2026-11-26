import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.experiment import Experiment

@pytest.fixture()
def seeded_new_experiments(db_session: Session) -> dict:
    """ایجاد ۵ آزمایش جدید در پایگاه داده تست حافظه‌ای"""
    experiments = {}

    exp_defs = [
        {
            "slug": "vinegar-baking-soda-reaction",
            "title": "واکنش شیمیایی سرکه و جوش‌شیرین",
            "subject": "شیمی",
            "grade": "هشتم",
            "difficulty": "آسان",
            "duration_minutes": 15,
            "status": "PUBLISHED",
            "summary": "تولید گاز کربن‌دی‌اکسید و کف",
            "textbook_source": {"book": "علوم هشتم", "chapter": "تغییرهای شیمیایی", "page": 18},
            "objectives": ["تولید گاز", "واکنش گرماگیر"],
            "safety_notes": ["عینک ایمنی"],
            "steps_config": [{"index": 1}, {"index": 2}, {"index": 3}, {"index": 4}]
        },
        {
            "slug": "simple-pendulum-motion",
            "title": "بررسی حرکت آونگ ساده",
            "subject": "فیزیک",
            "grade": "نهم",
            "difficulty": "متوسط",
            "duration_minutes": 20,
            "status": "PUBLISHED",
            "summary": "رابطه دوره تناوب با طول نخ",
            "textbook_source": {"book": "علوم نهم", "chapter": "حرکت چیست", "page": 44},
            "objectives": ["حرکت هماهنگ", "استقلال از جرم"],
            "safety_notes": ["زاویه کوچک"],
            "steps_config": [{"index": 1}, {"index": 2}, {"index": 3}, {"index": 4}]
        },
        {
            "slug": "plant-water-transport-celery",
            "title": "انتقال آب در آوندهای چوبی ساقه کرفس",
            "subject": "زیست‌شناسی",
            "grade": "هفتم",
            "difficulty": "آسان",
            "duration_minutes": 15,
            "status": "PUBLISHED",
            "summary": "صعود آب در آوندهای چوبی با مکش تعرق",
            "textbook_source": {"book": "علوم هفتم", "chapter": "سفر آب درون گیاه", "page": 112},
            "objectives": ["آوند چوبی", "مکش تعرق"],
            "safety_notes": ["مراقبت از تیغ"],
            "steps_config": [{"index": 1}, {"index": 2}, {"index": 3}, {"index": 4}, {"index": 5}]
        },
        {
            "slug": "liquid-density-column",
            "title": "بررسی چگالی و برج مایعات",
            "subject": "شیمی و فیزیک",
            "grade": "هفتم",
            "difficulty": "آسان",
            "duration_minutes": 15,
            "status": "PUBLISHED",
            "summary": "لایه‌بندی عسل، آب و روغن بر اساس چگالی",
            "textbook_source": {"book": "علوم هفتم", "chapter": "اندازه‌گیری در علوم", "page": 14},
            "objectives": ["چگالی مایعات", "امتزاج‌ناپذیری"],
            "safety_notes": ["عدم چشیدن"],
            "steps_config": [{"index": 1}, {"index": 2}, {"index": 3}, {"index": 4}, {"index": 5}]
        },
        {
            "slug": "water-filtration-column",
            "title": "ساخت صافی چندلایه آب",
            "subject": "شیمی",
            "grade": "هشتم",
            "difficulty": "متوسط",
            "duration_minutes": 20,
            "status": "PUBLISHED",
            "summary": "تصفیه مکانیکی آب گل‌آلود با شن و ماسه",
            "textbook_source": {"book": "علوم هشتم", "chapter": "مخلوط و جداسازی", "page": 8},
            "objectives": ["جداسازی فیزیکی", "هشدار عدم شرب"],
            "safety_notes": ["آب غیرقابل شرب است"],
            "steps_config": [{"index": 1}, {"index": 2}, {"index": 3}, {"index": 4}, {"index": 5}]
        }
    ]

    for d in exp_defs:
        e = Experiment(**d)
        db_session.add(e)
        db_session.commit()
        db_session.refresh(e)
        experiments[d["slug"]] = e

    return experiments


def test_vinegar_reaction_e2e(client: TestClient, student_auth_headers: dict, seeded_new_experiments: dict):
    """تست چرخه کامل تلاش آزمایشگاه: واکنش سرکه و جوش‌شیرین"""
    # ۱. شروع تلاش
    res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": "vinegar-baking-soda-reaction"},
        headers=student_auth_headers
    )
    assert res.status_code == 201
    data = res.json()
    attempt_id = data["attempt_id"]
    assert data["total_steps"] == 4

    # ۲. گام ۱: انتخاب بشر
    act1 = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "SELECT_BEAKER", "source_id": "beaker_1"},
        headers=student_auth_headers
    )
    assert act1.status_code == 200
    assert act1.json()["success"] is True
    assert act1.json()["is_step_completed"] is True

    # ۳. گام ۲: ریختن سرکه
    act2 = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={
            "action_type": "POUR_VINEGAR",
            "source_id": "vinegar_bottle",
            "target_id": "beaker_1",
            "parameters": {"volume_ml": 60.0}
        },
        headers=student_auth_headers
    )
    assert act2.status_code == 200
    assert act2.json()["success"] is True

    # ۴. گام ۳: افزودن جوش‌شیرین و واکنش
    act3 = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={
            "action_type": "ADD_BAKING_SODA",
            "source_id": "baking_soda_jar",
            "target_id": "beaker_1",
            "parameters": {"mass_g": 6.0}
        },
        headers=student_auth_headers
    )
    assert act3.status_code == 200
    assert act3.json()["success"] is True
    assert act3.json()["measurements"]["gas_emission_started"] is True

    # ۵. گام ۴: مشاهده و پایان
    act4 = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "OBSERVE_REACTION", "source_id": "beaker_1"},
        headers=student_auth_headers
    )
    assert act4.status_code == 200
    assert act4.json()["is_terminal"] is True
    assert "co2_volume_ml" in act4.json()["measurements"]

    # ۶. اتمام و ثبت نمره
    fin = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/finish",
        headers=student_auth_headers
    )
    assert fin.status_code == 200
    assert fin.json()["status"] == "COMPLETED"
    assert fin.json()["score"] >= 90.0


def test_pendulum_motion_e2e(client: TestClient, student_auth_headers: dict, seeded_new_experiments: dict):
    """تست چرخه کامل تلاش: حرکت آونگ ساده و خطای زاویه بزرگ"""
    res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": "simple-pendulum-motion"},
        headers=student_auth_headers
    )
    assert res.status_code == 201
    attempt_id = res.json()["attempt_id"]

    # گام ۱: تنظیم طول و جرم
    act1 = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={
            "action_type": "SET_PARAMETERS",
            "source_id": "pendulum_string",
            "parameters": {"length_m": 1.0, "mass_g": 200.0}
        },
        headers=student_auth_headers
    )
    assert act1.status_code == 200
    assert act1.json()["success"] is True

    # گام ۲: اتصال وزنه
    act2 = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "ATTACH_BOB", "source_id": "pendulum_bob", "target_id": "pendulum_string"},
        headers=student_auth_headers
    )
    assert act2.status_code == 200
    assert act2.json()["success"] is True

    # خطای زاویه بزرگ (انحراف بیش از ۱۵ درجه)
    err_act = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "DISPLACE_BOB", "source_id": "pendulum_bob", "parameters": {"angle_deg": 35.0}},
        headers=student_auth_headers
    )
    assert err_act.status_code == 200
    assert err_act.json()["success"] is False
    assert err_act.json()["error"]["code"] == "ERR_LARGE_ANGLE_DEVIATION"

    # درخواست راهنمای سه‌سطحی برای این خطا
    hint_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/hint",
        json={"step_index": 3, "error_code": "ERR_LARGE_ANGLE_DEVIATION"},
        headers=student_auth_headers
    )
    assert hint_res.status_code == 200
    assert hint_res.json()["level"] == 1
    assert "زاویه" in hint_res.json()["content"]

    # اصلاح انحراف با زاویه کوچک مجاز
    act3 = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "DISPLACE_BOB", "source_id": "pendulum_bob", "parameters": {"angle_deg": 10.0}},
        headers=student_auth_headers
    )
    assert act3.status_code == 200
    assert act3.json()["success"] is True

    # رهاسازی و اندازه‌گیری
    act4 = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "RELEASE_AND_MEASURE", "source_id": "pendulum_bob", "parameters": {"oscillations": 10}},
        headers=student_auth_headers
    )
    assert act4.status_code == 200
    assert act4.json()["is_terminal"] is True


def test_plant_transport_e2e(client: TestClient, student_auth_headers: dict, seeded_new_experiments: dict):
    """تست چرخه کامل تلاش: انتقال آب در آوند چوبی کرفس"""
    res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": "plant-water-transport-celery"},
        headers=student_auth_headers
    )
    assert res.status_code == 201
    attempt_id = res.json()["attempt_id"]

    # گام ۱: ریختن آب
    client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "POUR_WATER", "source_id": "water_pitcher", "target_id": "transparent_cup", "parameters": {"volume_ml": 150}},
        headers=student_auth_headers
    )
    # گام ۲: افزودن رنگ خوراکی
    client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "ADD_FOOD_COLORING", "source_id": "food_coloring_bottle", "target_id": "transparent_cup", "parameters": {"drops": 6, "color": "blue"}},
        headers=student_auth_headers
    )
    # گام ۳: قرار دادن کرفس
    client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "INSERT_CELERY", "source_id": "celery_stalk", "target_id": "transparent_cup"},
        headers=student_auth_headers
    )
    # گام ۴: گذر زمان
    act4 = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "SIMULATE_TIME", "source_id": "celery_stalk", "parameters": {"hours": 12.0}},
        headers=student_auth_headers
    )
    assert act4.status_code == 200
    assert act4.json()["success"] is True

    # گام ۵: مشاهده مقطع عرضی
    act5 = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "OBSERVE_CROSS_SECTION", "source_id": "celery_stalk"},
        headers=student_auth_headers
    )
    assert act5.status_code == 200
    assert act5.json()["is_terminal"] is True


def test_density_column_e2e(client: TestClient, student_auth_headers: dict, seeded_new_experiments: dict):
    """تست چرخه کامل تلاش: ستون چگالی مایعات"""
    res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": "liquid-density-column"},
        headers=student_auth_headers
    )
    assert res.status_code == 201
    attempt_id = res.json()["attempt_id"]

    # گام ۱: آماده‌سازی استوانه
    client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "PREPARE_CONTAINER", "source_id": "graduated_cylinder"}, headers=student_auth_headers)
    # گام ۲: عسل
    client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "POUR_HONEY", "source_id": "honey_jar", "target_id": "graduated_cylinder", "parameters": {"volume_ml": 50}}, headers=student_auth_headers)
    # گام ۳: آب
    client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "POUR_WATER", "source_id": "water_beaker", "target_id": "graduated_cylinder", "parameters": {"volume_ml": 50}}, headers=student_auth_headers)
    # گام ۴: روغن
    client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "POUR_OIL", "source_id": "oil_bottle", "target_id": "graduated_cylinder", "parameters": {"volume_ml": 50}}, headers=student_auth_headers)
    # گام ۵: مشاهده لایه‌ها
    act5 = client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "OBSERVE_LAYERS", "source_id": "graduated_cylinder"}, headers=student_auth_headers)
    assert act5.status_code == 200
    assert act5.json()["is_terminal"] is True


def test_water_filtration_e2e(client: TestClient, student_auth_headers: dict, seeded_new_experiments: dict):
    """تست چرخه کامل تلاش: صافی چندلایه آب"""
    res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": "water-filtration-column"},
        headers=student_auth_headers
    )
    assert res.status_code == 201
    attempt_id = res.json()["attempt_id"]

    # گام ۱: بطری
    client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "PREPARE_BOTTLE", "source_id": "plastic_bottle"}, headers=student_auth_headers)
    # گام ۲: لایه‌ها
    client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "ARRANGE_FILTER_LAYERS", "source_id": "cotton_layer", "parameters": {"layers": ["cotton", "sand", "gravel"]}}, headers=student_auth_headers)
    # گام ۳: آب گل‌آلود
    client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "POUR_DIRTY_WATER", "source_id": "turbid_water_beaker", "target_id": "plastic_bottle", "parameters": {"volume_ml": 200}}, headers=student_auth_headers)
    # گام ۴: مشاهده فیلتراسیون
    client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "OBSERVE_FILTRATION", "source_id": "plastic_bottle"}, headers=student_auth_headers)
    # گام ۵: ارزیابی و هشدار عدم شرب
    act5 = client.post(f"/api/v1/simulation/attempts/{attempt_id}/action", json={"action_type": "COMPARE_AND_EVALUATE", "source_id": "collection_cup"}, headers=student_auth_headers)
    assert act5.status_code == 200
    assert act5.json()["is_terminal"] is True
