import pytest
from fastapi.testclient import TestClient

def test_full_simulation_attempt_flow(
    client: TestClient,
    student_auth_headers,
    acid_base_experiment
):
    # 1. آغاز تلاش جدید در آزمایشگاه
    start_res = client.post(
        "/api/v1/simulation/attempts/start",
        json={"experiment_slug": acid_base_experiment.slug},
        headers=student_auth_headers
    )
    assert start_res.status_code == 201
    start_data = start_res.json()
    attempt_id = start_data["attempt_id"]
    assert start_data["experiment_slug"] == acid_base_experiment.slug
    assert start_data["status"] == "IN_PROGRESS"

    # 2. افزودن وسایل مورد نیاز به میز کار
    add_lemon_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "ADD_TOOL", "source_id": "beaker-lemon"},
        headers=student_auth_headers
    )
    assert add_lemon_res.status_code == 200
    assert add_lemon_res.json()["success"] is True

    add_red_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "ADD_TOOL", "source_id": "litmus-red"},
        headers=student_auth_headers
    )
    assert add_red_res.status_code == 200
    assert add_red_res.json()["success"] is True

    # 3. اجرای کنش علمی نادرست و دریافت خطای آموزشی
    # قرار دادن لیتموس سرخ درون اسید (اشتباه علمی کتب درسی: تورنسل سرخ در اسید سرخ می‌ماند)
    wrong_action_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={
            "action_type": "DIP_INDICATOR",
            "source_id": "litmus-red",
            "target_id": "beaker-lemon"
        },
        headers=student_auth_headers
    )
    assert wrong_action_res.status_code == 200
    wrong_data = wrong_action_res.json()
    assert wrong_data["success"] is False
    assert wrong_data["error"] is not None
    assert wrong_data["error"]["code"] == "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"
    assert "شناساگر" in wrong_data["error"]["title"]

    # 4. درخواست راهنمای سه‌سطحی پلکانی
    # سطح ۱: پرسش سقراطی
    hint1_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/hint",
        json={"step_index": 1, "error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"},
        headers=student_auth_headers
    )
    assert hint1_res.status_code == 200
    h1 = hint1_res.json()
    assert h1["level"] == 1
    assert h1["can_escalate"] is True
    assert len(h1["content"]) > 0

    # سطح ۲: سرنخ اصل علمی
    hint2_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/hint",
        json={"step_index": 1, "error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"},
        headers=student_auth_headers
    )
    assert hint2_res.status_code == 200
    h2 = hint2_res.json()
    assert h2["level"] == 2
    assert h2["can_escalate"] is True

    # سطح ۳: راهکار اجرایی مستقیم
    hint3_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/hint",
        json={"step_index": 1, "error_code": "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"},
        headers=student_auth_headers
    )
    assert hint3_res.status_code == 200
    h3 = hint3_res.json()
    assert h3["level"] == 3
    assert h3["can_escalate"] is False

    # 5. تصحیح اقدام طبق راهنما: آوردن تورنسل آبی و قرار دادن آن درون آبلیمو
    client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={"action_type": "ADD_TOOL", "source_id": "litmus-blue"},
        headers=student_auth_headers
    )

    correct_action_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/action",
        json={
            "action_type": "DIP_INDICATOR",
            "source_id": "litmus-blue",
            "target_id": "beaker-lemon"
        },
        headers=student_auth_headers
    )
    assert correct_action_res.status_code == 200
    correct_data = correct_action_res.json()
    assert correct_data["success"] is True
    assert correct_data["is_step_completed"] is True

    # 6. بررسی وضعیت و گزارش کامل تلاش
    state_res = client.get(
        f"/api/v1/simulation/attempts/{attempt_id}/state",
        headers=student_auth_headers
    )
    assert state_res.status_code == 200
    state_data = state_res.json()
    assert len(state_data["action_logs"]) >= 4  # add_lemon + add_red + wrong_dip + add_blue + correct_dip
    assert len(state_data["hint_usages"]) == 3  # 3 levels of hints

    # 7. اتمام آزمایش و ثبت نهایی
    finish_res = client.post(
        f"/api/v1/simulation/attempts/{attempt_id}/finish",
        headers=student_auth_headers
    )
    assert finish_res.status_code == 200
    finish_data = finish_res.json()
    assert finish_data["status"] in ["COMPLETED", "FAILED"]
    assert finish_data["score"] < 100.0  # کسر نمره به دلیل خطا و استفاده از ۳ سطح راهنما
