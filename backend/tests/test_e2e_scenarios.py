import pytest
from fastapi.testclient import TestClient

def test_scenario_a_acid_base_curriculum_e2e(
    client: TestClient,
    student_auth_headers,
    teacher_auth_headers,
    acid_base_experiment
):
    """
    سناریوی الف: آزمون سرتاسری (E2E) آزمایش شناسایی اسیدها و بازها با معرف‌های رنگی
    مطابق با علوم هشتم، فصل ۱، ص ۶
    شامل: شروع تلاش، خطای شناساگر نامناسب، پلکان ۳ سطحی راهنما، اجرای گام‌ها و اتمام با محاسبه نمره
    """
    # ۱. شروع تلاش توسط دانش‌آموز
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    assert start_res.status_code == 201
    attempt_id = start_res.json()["attempt_id"]

    # ۲. پیش‌نیاز: تلاش برای تست شناساگر قبل از افزودن ابزار به میز کار
    no_tool_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "DIP_INDICATOR", "source_id": "litmus-blue", "target_id": "beaker-lemon"},
        headers=student_auth_headers
    )
    assert no_tool_res.status_code == 200
    assert no_tool_res.json()["success"] is False

    # ۳. افزودن ظروف و ابزارها به میز کار
    for tool_id in ["beaker-lemon", "beaker-soda", "litmus-red", "litmus-blue", "ph-meter"]:
        client.post(
            f"/api/v1/simulation/attempts/{attempt_id}/action",
            json={"action_type": "ADD_TOOL", "source_id": tool_id},
            headers=student_auth_headers
        )

    # ۴. کج‌فهمی رایج علمی: قرار دادن لیتموس قرمز در اسید
    wrong_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "DIP_INDICATOR", "source_id": "litmus-red", "target_id": "beaker-lemon"},
        headers=student_auth_headers
    )
    assert wrong_res.status_code == 200
    wrong_data = wrong_res.json()
    assert wrong_data["success"] is False
    assert wrong_data["error"]["code"] == "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"

    # ۵. دریافت راهنمای آموزشی ۳ سطحی (سقراطی -> سرنخ -> راهکار مستقیم)
    h1 = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/hint",
        json={"step_index": 1, "error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"},
        headers=student_auth_headers
    ).json()
    assert h1["level"] == 1
    assert h1["can_escalate"] is True

    h2 = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/hint",
        json={"step_index": 1, "error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"},
        headers=student_auth_headers
    ).json()
    assert h2["level"] == 2

    h3 = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/hint",
        json={"step_index": 1, "error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"},
        headers=student_auth_headers
    ).json()
    assert h3["level"] == 3
    assert h3["can_escalate"] is False

    # ۶. اجرای صحیح گام ۱: لیتموس آبی در آبلیمو -> تغییر رنگ به قرمز
    step1_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "DIP_INDICATOR", "source_id": "litmus-blue", "target_id": "beaker-lemon"},
        headers=student_auth_headers
    )
    assert step1_res.status_code == 200
    assert step1_res.json()["success"] is True
    assert step1_res.json()["is_step_completed"] is True

    # ۷. اجرای صحیح گام ۲: لیتموس قرمز در جوش شیرین -> تغییر رنگ به آبی
    step2_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "DIP_INDICATOR", "source_id": "litmus-red", "target_id": "beaker-soda"},
        headers=student_auth_headers
    )
    assert step2_res.status_code == 200
    assert step2_res.json()["success"] is True
    assert step2_res.json()["is_step_completed"] is True

    # ۸. اجرای صحیح گام ۳: سنجش دیجیتال pH با پروب
    step3_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "MEASURE_PH", "source_id": "ph-meter", "target_id": "beaker-lemon"},
        headers=student_auth_headers
    )
    assert step3_res.status_code == 200
    assert step3_res.json()["success"] is True
    assert step3_res.json()["is_step_completed"] is True

    # ۹. ثبت نهایی تلاش
    finish_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/finish",
        headers=student_auth_headers
    )
    assert finish_res.status_code == 200
    finish_data = finish_res.json()
    assert finish_data["status"] == "COMPLETED"
    assert finish_data["steps_completed"] == 3
    # نمره به دلیل ۱ خطا و ۳ راهنما باید از ۱۰۰ کسر شده باشد
    assert 50 <= finish_data["score"] < 100

    # ۱۰. پایش معلم: مشاهده لاگ دقیق و ممیزی تلاش دانش‌آموز
    audit_res = client.get(
        f"/api/v1/teacher/students/attempts/{attempt_id}",
        headers=teacher_auth_headers
    )
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    assert audit_data["attempt_id"] == attempt_id
    assert len(audit_data["action_logs"]) >= 5
    assert len(audit_data["hint_usages"]) == 3


def test_scenario_b_mixture_separation_curriculum_e2e(
    client: TestClient,
    student_auth_headers,
    mixture_experiment
):
    """
    سناریوی ب: آزمون سرتاسری (E2E) آزمایش جداسازی مخلوط ماسه، نمک و آب
    مطابق با علوم هشتم، فصل ۲، ص ۱۶
    قواعد فیزیکی: انحلال‌پذیری تفکیکی، فیلتراسیون فاز جامد، تبخیر و بلورزایی
    """
    # ۱. شروع تلاش
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": mixture_experiment.slug},
        headers=student_auth_headers
    )
    assert start_res.status_code == 201
    attempt_id = start_res.json()["attempt_id"]

    # ۲. استقرار وسایل روی میز
    tools = [
        "beaker_sand_salt",
        "wash_bottle_water",
        "funnel_filter_paper",
        "evaporating_dish",
        "bunsen_burner"
    ]
    for tool_id in tools:
        res = client.post(
            f"/api/v1/simulation/attempts/{attempt_id}/action",
            json={"action_type": "ADD_TOOL", "source_id": tool_id},
            headers=student_auth_headers
        )
        assert res.status_code == 200

    # ۳. خطای نقض توالی: تلاش برای صاف کردن پودر خشک قبل از انحلال
    dry_filter_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "FILTER_MIXTURE", "source_id": "funnel_filter_paper"},
        headers=student_auth_headers
    )
    assert dry_filter_res.status_code == 200
    assert dry_filter_res.json()["success"] is False
    assert dry_filter_res.json()["error"]["code"] == "ERR_FILTER_WITHOUT_DISSOLUTION"

    # ۴. گام ۱: افزودن آب و انحلال نمک طعام
    dissolve_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "ADD_WATER_AND_STIR", "source_id": "wash_bottle_water"},
        headers=student_auth_headers
    )
    assert dissolve_res.status_code == 200
    assert dissolve_res.json()["success"] is True
    assert dissolve_res.json()["is_step_completed"] is True

    # ۵. خطای نقض توالی: تلاش برای حرارت دادن قبل از فیلتراسیون ماسه
    early_heat_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "HEAT", "source_id": "bunsen_burner"},
        headers=student_auth_headers
    )
    assert early_heat_res.status_code == 200
    assert early_heat_res.json()["success"] is False
    assert early_heat_res.json()["error"]["code"] == "ERR_HEAT_BEFORE_FILTER"

    # ۶. گام ۲: فیلتراسیون با قیف و کاغذ صافی
    filter_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "FILTER_MIXTURE", "source_id": "funnel_filter_paper"},
        headers=student_auth_headers
    )
    assert filter_res.status_code == 200
    assert filter_res.json()["success"] is True
    assert filter_res.json()["is_step_completed"] is True

    # ۷. گام ۳: تبخیر آب و بازیابی بلور نمک روی شعله بونزن
    evaporate_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "HEAT", "source_id": "bunsen_burner"},
        headers=student_auth_headers
    )
    assert evaporate_res.status_code == 200
    evap_data = evaporate_res.json()
    assert evap_data["success"] is True
    assert evap_data["is_step_completed"] is True
    assert evap_data["measurements"]["salt_recovered_g"] == 10.0

    # ۸. نهایی‌سازی آزمایش
    finish_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/finish",
        headers=student_auth_headers
    )
    assert finish_res.status_code == 200
    assert finish_res.json()["status"] == "COMPLETED"
    assert finish_res.json()["steps_completed"] == 3


def test_scenario_c_simple_circuit_curriculum_e2e(
    client: TestClient,
    student_auth_headers,
    circuit_experiment
):
    """
    سناریوی ج: آزمون سرتاسری (E2E) آزمایش مدار الکتریکی ساده و قانون اهم
    مطابق با علوم نهم، فصل ۹، ص ۹۸
    قواعد فیزیکی: قانون اهم (V = I * R)، پیشگیری از اتصال کوتاه، مدار باز/بسته
    """
    # ۱. شروع تلاش
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": circuit_experiment.slug},
        headers=student_auth_headers
    )
    assert start_res.status_code == 201
    attempt_id = start_res.json()["attempt_id"]

    # ۲. پیشگیری از اتصال کوتاه: سیم‌کشی باتری بدون لامپ
    client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "ADD_TOOL", "source_id": "battery_cell"},
        headers=student_auth_headers
    )
    client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "ADD_TOOL", "source_id": "connecting_wires"},
        headers=student_auth_headers
    )
    client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "ADD_TOOL", "source_id": "switch_key"},
        headers=student_auth_headers
    )

    short_circuit_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "CONNECT_COMPONENTS", "source_id": "wires"},
        headers=student_auth_headers
    )
    assert short_circuit_res.status_code == 200
    assert short_circuit_res.json()["success"] is False
    assert short_circuit_res.json()["error"]["code"] == "ERR_CIRCUIT_WITHOUT_LOAD"

    # ۳. افزودن لامپ و سیم‌کشی موفق حلقه مدار
    client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "ADD_TOOL", "source_id": "light_bulb"},
        headers=student_auth_headers
    )

    wire_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "CONNECT_COMPONENTS", "source_id": "wires"},
        headers=student_auth_headers
    )
    assert wire_res.status_code == 200
    assert wire_res.json()["success"] is True
    assert wire_res.json()["is_step_completed"] is True

    # ۴. خطای تلاش برای اندازه‌گیری در مدار باز
    client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "ADD_TOOL", "source_id": "ammeter"},
        headers=student_auth_headers
    )
    open_meas_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "MEASURE_CURRENT", "source_id": "ammeter"},
        headers=student_auth_headers
    )
    assert open_meas_res.status_code == 200
    assert open_meas_res.json()["success"] is False
    assert open_meas_res.json()["error"]["code"] == "ERR_MEASURE_ON_OPEN_CIRCUIT"

    # ۵. گام ۲: بستن کلید مدار و روشن شدن لامپ
    switch_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "CLOSE_SWITCH", "source_id": "switch_key"},
        headers=student_auth_headers
    )
    assert switch_res.status_code == 200
    assert switch_res.json()["success"] is True
    assert switch_res.json()["is_step_completed"] is True
    assert switch_res.json()["measurements"]["bulb_lit"] is True

    # ۶. گام ۳: اندازه‌گیری شدت جریان و محاسبه اثبات قانون اهم
    meas_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "MEASURE_CURRENT", "source_id": "ammeter"},
        headers=student_auth_headers
    )
    assert meas_res.status_code == 200
    meas_data = meas_res.json()
    assert meas_data["success"] is True
    assert meas_data["is_step_completed"] is True
    assert meas_data["measurements"]["calculated_resistance_ohms"] == 10.1

    # ۷. اتمام تلاش
    finish_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/finish",
        headers=student_auth_headers
    )
    assert finish_res.status_code == 200
    assert finish_res.json()["status"] == "COMPLETED"


def test_student_and_teacher_cross_telemetry_flow(
    client: TestClient,
    student_auth_headers,
    teacher_auth_headers,
    acid_base_experiment
):
    """
    آزمون گردش کامل تلمتری بین داشبورد دانش‌آموز و پنل تحلیلی معلم:
    دانش‌آموز آزمایش را تکمیل می‌کند، سوابق در داشبوردش نمایش داده می‌شود،
    و معلم کج‌فهمی‌ها و توزیع نمرات را در پنل تحلیلی رصد می‌کند.
    """
    # ۱. ثبت یک تلاش دانش‌آموز
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    attempt_id = start_res.json()["attempt_id"]

    # اتمام مستقیم برای ارزیابی تلمتری
    client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/finish",
        headers=student_auth_headers
    )

    # ۲. استعلام تاریخچه تلاش‌های دانش‌آموز در داشبورد خود
    student_history_res = client.get(
        "/api/v1/student/attempts",
        headers=student_auth_headers
    )
    assert student_history_res.status_code == 200
    history = student_history_res.json()
    assert isinstance(history, list)
    assert any(att["id"] == attempt_id for att in history)

    # ۳. استعلام پنل کلان تحلیلی معلم
    teacher_analytics_res = client.get(
        "/api/v1/teacher/analytics",
        headers=teacher_auth_headers
    )
    assert teacher_analytics_res.status_code == 200
    analytics = teacher_analytics_res.json()
    assert "total_students" in analytics
    assert "active_experiments_count" in analytics
    assert "average_completion_rate" in analytics
    assert "frequent_errors" in analytics
    assert "experiment_stats" in analytics
