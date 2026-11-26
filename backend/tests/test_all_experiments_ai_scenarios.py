import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch
from backend.app.services.gemini_client import GeminiResult
from backend.app.models.experiment import Experiment

@pytest.fixture()
def all_eight_experiments(db_session: Session) -> dict:
    """اطمینان از وجود تمام ۸ آزمایش رسمی در پایگاه داده تست حافظه‌ای"""
    specs = [
        {
            "slug": "acid-base-indicators",
            "title": "شناسایی اسیدها و بازها با معرف‌های رنگی",
            "subject": "شیمی",
            "grade": "هشتم"
        },
        {
            "slug": "vinegar-baking-soda-reaction",
            "title": "واکنش سرکه و جوش‌شیرین و تولید گاز",
            "subject": "شیمی",
            "grade": "هشتم"
        },
        {
            "slug": "simple-pendulum-motion",
            "title": "بررسی حرکت آونگ ساده و قانون دوره تناوب",
            "subject": "فیزیک",
            "grade": "نهم"
        },
        {
            "slug": "plant-water-transport-celery",
            "title": "انتقال آب در گیاه و هدایت در آوندهای چوبی",
            "subject": "زیست‌شناسی",
            "grade": "هفتم"
        },
        {
            "slug": "liquid-density-column",
            "title": "بررسی چگالی و لایه‌بندی مایعات (ستون چگالی)",
            "subject": "شیمی",
            "grade": "هفتم"
        },
        {
            "slug": "water-filtration-column",
            "title": "ساخت صافی چندلایه آب و تصفیه فیزیکی",
            "subject": "شیمی",
            "grade": "هفتم"
        },
        {
            "slug": "mixture-separation-sand-salt",
            "title": "جداسازی مخلوط ناهمگن ماسه، نمک و آب",
            "subject": "شیمی",
            "grade": "هشتم"
        },
        {
            "slug": "simple-electric-circuit-ohm",
            "title": "بررسی مدار الکتریکی ساده و قانون اهم",
            "subject": "فیزیک",
            "grade": "نهم"
        }
    ]

    result = {}
    for item in specs:
        exp = db_session.query(Experiment).filter(Experiment.slug == item["slug"]).first()
        if not exp:
            exp = Experiment(
                slug=item["slug"],
                title=item["title"],
                subject=item["subject"],
                grade=item["grade"],
                difficulty="متوسط",
                duration_minutes=15,
                status="PUBLISHED",
                version=1,
                summary=f"خلاصه آزمایش {item['title']}",
                textbook_source={"book": "علوم تجربی", "chapter": "فصل ۱", "page": 10},
                steps_config=[{"index": 1}, {"index": 2}, {"index": 3}, {"index": 4}]
            )
            db_session.add(exp)
            db_session.commit()
            db_session.refresh(exp)
        result[item["slug"]] = exp

    return result

def test_vinegar_ai_scenario_gas_misconception_and_hint(client: TestClient, all_eight_experiments, student_auth_headers):
    """
    سناریوی ۱: واکنش سرکه و جوش‌شیرین
    - دانش‌آموز گاز خروجی را اکسیژن پیش‌بینی می‌کند.
    - ارتقای سه‌سطحی راهنمایی هوشمند و بررسی محتوای سقراطی، سرنخ و توضیح علمی.
    """
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": "vinegar-baking-soda-reaction"},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    # ثبت فرضیه اشتباه گاز اکسیژن
    action_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={
            "action_type": "SUBMIT_PREDICTION",
            "source_id": "beaker_glass",
            "parameters": {"predicted_gas": "oxygen"}
        },
        headers=student_auth_headers
    )
    assert action_res.status_code == 200
    act_data = action_res.json()
    assert act_data["success"] is False
    assert act_data["error"]["code"] == "ERR_MISCONCEPTION_GAS_TYPE"

    # سطح ۱ راهنما
    h1 = client.post(
        f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
        json={"error_code": "ERR_MISCONCEPTION_GAS_TYPE", "step_index": 1},
        headers=student_auth_headers
    ).json()
    assert h1["level"] == 1
    assert "گاز" in h1["content"] or "شمع" in h1["content"] or "کربن" in h1["content"]

    # سطح ۲ راهنما
    h2 = client.post(
        f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
        json={"error_code": "ERR_MISCONCEPTION_GAS_TYPE", "step_index": 1},
        headers=student_auth_headers
    ).json()
    assert h2["level"] == 2

    # سطح ۳ راهنما (پاسخ قطعی دی‌اکسید کربن)
    h3 = client.post(
        f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
        json={"error_code": "ERR_MISCONCEPTION_GAS_TYPE", "step_index": 1},
        headers=student_auth_headers
    ).json()
    assert h3["level"] == 3
    assert "دی‌اکسید" in h3["content"] or "CO2" in h3["content"] or "کربن" in h3["content"]

def test_pendulum_ai_scenario_mass_dependence(client: TestClient, all_eight_experiments, student_auth_headers):
    """
    سناریوی ۲: آونگ ساده
    - پیش‌بینی وابستگی دوره تناوب به جرم وزنه
    - دریافت راهنمای هوشمند و طرح پرسش مفهومی
    """
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": "simple-pendulum-motion"},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    act_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={
            "action_type": "SUBMIT_PREDICTION",
            "source_id": "pendulum_bob",
            "parameters": {"predicted_effect": "mass_increases_period"}
        },
        headers=student_auth_headers
    ).json()
    assert act_res["success"] is False
    assert act_res["error"]["code"] == "ERR_PENDULUM_MASS_DEPENDENCE"

    hint = client.post(
        f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
        json={"error_code": "ERR_PENDULUM_MASS_DEPENDENCE", "step_index": 2},
        headers=student_auth_headers
    ).json()
    assert hint["error_code"] == "ERR_PENDULUM_MASS_DEPENDENCE"
    assert "سقوط آزاد" in hint["content"] or "جرم" in hint["content"] or "فرمول" in hint["content"]

    # طرح پرسش دانش‌آموز از دستیار در مورد جرم وزنه
    ask_res = client.post(
        "/api/v1/ai/tutor/ask",
        json={
            "attempt_id": attempt_id,
            "question": "اگر وزنه آونگ سنگین‌تر شود زمان نوسان تغییر می‌کند؟",
            "step_index": 2
        },
        headers=student_auth_headers
    ).json()
    assert "آونگ" in ask_res["experiment_title"]
    assert len(ask_res["answer"]) > 10

def test_plant_transport_ai_scenario_xylem(client: TestClient, all_eight_experiments, student_auth_headers):
    """
    سناریوی ۳: انتقال آب در گیاه
    - تصور انتقال بدون آوند از پوست ساقه
    - هدایت به بافت آوند چوبی
    """
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": "plant-water-transport-celery"},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    act_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={
            "action_type": "SUBMIT_PREDICTION",
            "source_id": "celery_stalk",
            "parameters": {"predicted_path": "skin"}
        },
        headers=student_auth_headers
    ).json()
    assert act_res["success"] is False
    assert act_res["error"]["code"] == "ERR_MISCONCEPTION_XYLEM_PATH"

    hint3 = client.post(
        f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
        json={"error_code": "ERR_MISCONCEPTION_XYLEM_PATH", "step_index": 4, "forced_level": 3},
        headers=student_auth_headers
    ).json()
    assert hint3["level"] == 3
    assert "آوند" in hint3["content"] or "چوبی" in hint3["content"] or "Xylem" in hint3["content"]

def test_density_column_ai_scenario(client: TestClient, all_eight_experiments, student_auth_headers):
    """
    سناریوی ۴: ستون چگالی مایعات
    - خلط مفهوم حجم با چگالی
    - هدایت به مفهوم خاصیت شدتی ماده
    """
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": "liquid-density-column"},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    act_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={
            "action_type": "SUBMIT_PREDICTION",
            "source_id": "measuring_cylinder",
            "parameters": {"prediction": "volume_determines_layer"}
        },
        headers=student_auth_headers
    ).json()
    assert act_res["success"] is False
    assert act_res["error"]["code"] == "ERR_DENSITY_VOLUME_CONFUSION"

    hint = client.post(
        f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
        json={"error_code": "ERR_DENSITY_VOLUME_CONFUSION", "step_index": 5, "forced_level": 2},
        headers=student_auth_headers
    ).json()
    assert hint["level"] == 2
    assert "چگالی" in hint["content"]

def test_water_filtration_safety_ai_scenario(client: TestClient, all_eight_experiments, student_auth_headers):
    """
    سناریوی ۵: صافی آب
    - خطای بهداشتی شرب آب صافی فیزیکی
    - هشدار ایمنی فوری
    """
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": "water-filtration-column"},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    act_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "DRINK_WATER", "source_id": "collection_beaker", "parameters": {"is_potable": True}},
        headers=student_auth_headers
    ).json()
    assert act_res["success"] is False
    assert act_res["error"]["code"] == "ERR_MISCONCEPTION_POTABLE_WATER"

    hint = client.post(
        f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
        json={"error_code": "ERR_MISCONCEPTION_POTABLE_WATER", "step_index": 5, "forced_level": 3},
        headers=student_auth_headers
    ).json()
    assert hint["level"] == 3
    assert "آشامیدنی" in hint["content"] or "میکروب" in hint["content"] or "شرب" in hint["content"]

def test_acid_base_and_circuit_misconceptions_ai_scenarios(client: TestClient, all_eight_experiments, student_auth_headers):
    """
    سناریوی ۶: اسید و باز و مدار الکتریکی
    """
    # الف) اسید و باز: تفسیر فنل‌فتالئین
    res_acid = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": "acid-base-indicators"},
        headers=student_auth_headers
    )
    att_acid = res_acid.json()["attempt_id"]
    act_acid = client.post(
        f"/api/v1/simulation/attempts/{att_acid}/action",
        json={"action_type": "SUBMIT_PREDICTION", "source_id": "phenolphthalein", "parameters": {"prediction": "acid_is_pink"}},
        headers=student_auth_headers
    ).json()
    assert act_acid["error"]["code"] == "ERR_PHENOLPHTHALEIN_ACID_MISINTERPRETATION"

    # ب) مدار الکتریکی: تصور رابطه معکوس ولتاژ و جریان
    res_circ = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": "simple-electric-circuit-ohm"},
        headers=student_auth_headers
    )
    att_circ = res_circ.json()["attempt_id"]
    act_circ = client.post(
        f"/api/v1/simulation/attempts/{att_circ}/action",
        json={"action_type": "SUBMIT_PREDICTION", "source_id": "battery_pack", "parameters": {"prediction": "higher_voltage_less_current"}},
        headers=student_auth_headers
    ).json()
    assert act_circ["error"]["code"] == "ERR_VOLTAGE_CURRENT_MISCONCEPTION"

def test_all_experiments_offline_fallback_resilience(client: TestClient, all_eight_experiments, student_auth_headers):
    """
    سناریوی ۷: بررسی مصونیت سیستم در صورت عدم دسترسی به API یا نبود کلید Gemini
    - باید برای تمام ۸ آزمایش راهنمای باکیفیت بر پایه کاتالوگ مصوب کتاب درسی ارائه دهد بدون پرتاب خطا.
    """
    test_errors = [
        ("vinegar-baking-soda-reaction", "ERR_MISCONCEPTION_GAS_TYPE"),
        ("simple-pendulum-motion", "ERR_PENDULUM_MASS_DEPENDENCE"),
        ("plant-water-transport-celery", "ERR_MISCONCEPTION_XYLEM_PATH"),
        ("liquid-density-column", "ERR_DENSITY_VOLUME_CONFUSION"),
        ("water-filtration-column", "ERR_MISCONCEPTION_POTABLE_WATER"),
        ("acid-base-indicators", "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"),
        ("mixture-separation-sand-salt", "ERR_FILTER_WITHOUT_DISSOLUTION"),
        ("simple-electric-circuit-ohm", "ERR_CIRCUIT_WITHOUT_LOAD")
    ]

    with patch("backend.app.config.settings.GEMINI_API_KEY", None):
        for slug, err_code in test_errors:
            start_res = client.post(
                "/api/v1/simulation/attempts/start",
                json={"experiment_slug": slug},
                headers=student_auth_headers
            )
            assert start_res.status_code == 201
            attempt_id = start_res.json()["attempt_id"]

            hint_res = client.post(
                f"/api/v1/ai/tutor/hint?attempt_id={attempt_id}",
                json={"error_code": err_code, "step_index": 1, "forced_level": 3},
                headers=student_auth_headers
            )
            assert hint_res.status_code == 200
            data = hint_res.json()
            assert data["error_code"] == err_code
            assert data["level"] == 3
            assert len(data["content"]) > 10
            assert data["is_ai_generated"] is False
            assert data["model_used"] == "offline-rule-catalog"

def test_teacher_dashboard_multi_experiment_insights_report(client: TestClient, all_eight_experiments, teacher_auth_headers):
    """
    سناریوی ۸: بررسی پنل معلم و استخراج گزارش کلاسی برای سرفصل‌های مختلف آزمایشگاه
    """
    res = client.get("/api/v1/ai/teacher/insights", headers=teacher_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "top_misconceptions" in data
    assert "ai_pedagogical_remediation" in data
    assert len(data["ai_pedagogical_remediation"]) > 10
