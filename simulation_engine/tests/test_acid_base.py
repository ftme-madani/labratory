import pytest
from simulation_engine import (
    AcidBaseSimulationEngine,
    LabAction,
    ErrorCategory,
    SimulationState
)

@pytest.fixture
def engine():
    return AcidBaseSimulationEngine()

def test_initial_state(engine):
    """بررسی وضعیت اولیه تمیز و استاندارد موتور"""
    state = engine.state
    assert state.experiment_id == "exp-acid-base"
    assert state.current_step == 1
    assert state.total_steps == 3
    assert state.workbench_tools == []
    assert state.recorded_observations == []
    assert state.is_completed is False

def test_add_and_remove_tools(engine):
    """بررسی افزودن و حذف وسایل از قفسه به میز کار"""
    # افزودن معتبر
    res1 = engine.execute_action(LabAction(action_type="ADD_TOOL", source_id="beaker_lemon"))
    assert res1.success is True
    assert "beaker_lemon" in engine.state.workbench_tools

    # خطای افزودن تکراری
    res_dup = engine.execute_action(LabAction(action_type="ADD_TOOL", source_id="beaker_lemon"))
    assert res_dup.success is False
    assert res_dup.error.code == "ERR_TOOL_ALREADY_ON_WORKBENCH"

    # حذف معتبر
    res_rem = engine.execute_action(LabAction(action_type="REMOVE_TOOL", source_id="beaker_lemon"))
    assert res_rem.success is True
    assert "beaker_lemon" not in engine.state.workbench_tools

    # خطای حذف ابزاری که روی میز نیست
    res_rem_fail = engine.execute_action(LabAction(action_type="REMOVE_TOOL", source_id="beaker_lemon"))
    assert res_rem_fail.success is False
    assert res_rem_fail.error.code == "ERR_TOOL_NOT_ON_WORKBENCH"

def test_malformed_and_crash_resistant(engine):
    """آزمون تضمین عدم وقوع Crash به ازای هر نوع ورودی نامعتبر یا None"""
    # ورودی بدون اکشن‌تایپ
    res1 = engine.execute_action(LabAction(action_type="", source_id=""))
    assert res1.success is False
    assert res1.error.code == "ERR_MALFORMED_ACTION"

    # ابزار یا اکشن کاملاً نامعتبر
    res2 = engine.execute_action(LabAction(action_type="EXPLODE_LAB", source_id="fake_tool"))
    assert res2.success is False
    assert res2.error.code == "ERR_UNSUPPORTED_ACTION"

    # شناساگر نامعتبر (مثلاً فرو بردن خط‌کش یا دماسنج به جای شناساگر)
    engine.add_tool_to_workbench("beaker_lemon")
    engine.add_tool_to_workbench("ruler_tool")
    res3 = engine.execute_action(LabAction(
        action_type="DIP_INDICATOR",
        source_id="ruler_tool",
        target_id="beaker_lemon"
    ))
    assert res3.success is False
    assert res3.error.code == "ERR_WRONG_TOOL_INDICATOR"
    assert res3.error.category == ErrorCategory.WRONG_TOOL

def test_missing_preconditions(engine):
    """آزمون تشخیص عدم استقرار ابزار یا ظرف روی میز پیش از آزمایش"""
    # بدون قرار دادن وسایل روی میز
    res = engine.execute_action(LabAction(
        action_type="DIP_INDICATOR",
        source_id="litmus_blue",
        target_id="beaker_lemon"
    ))
    assert res.success is False
    assert res.error.category == ErrorCategory.MISSING_PRECONDITION
    assert res.error.code == "ERR_PRECONDITION_INDICATOR_NOT_ON_BENCH"

def test_ineffective_indicator_choice(engine):
    """آزمون تشخیص استفاده از شناساگر نامناسب (تورنسل سرخ برای نمونه اسیدی)"""
    engine.add_tool_to_workbench("beaker_lemon")
    engine.add_tool_to_workbench("litmus_red")

    res = engine.execute_action(LabAction(
        action_type="DIP_INDICATOR",
        source_id="litmus_red",
        target_id="beaker_lemon"
    ))
    assert res.success is False
    assert res.error.code == "ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID"
    # باید توضیح علمی بدهد که تورنسل سرخ در اسید بدون تغییر می‌ماند
    assert "تورنسل سرخ" in res.error.description

def test_order_violation(engine):
    """آزمون تشخیص ترتیب نادرست گام‌ها (تست آب‌صابون در مرحله ۱)"""
    engine.add_tool_to_workbench("beaker_soap")
    engine.add_tool_to_workbench("litmus_red")

    res = engine.execute_action(LabAction(
        action_type="DIP_INDICATOR",
        source_id="litmus_red",
        target_id="beaker_soap"
    ))
    assert res.success is False
    assert res.error.category == ErrorCategory.ORDER_VIOLATION
    assert res.error.code == "ERR_ORDER_VIOLATION_STEP1"

def test_happy_path_full_experiment(engine):
    """آزمون اجرای موفقیت‌آمیز تمام مراحل از گام ۱ تا ۳ و تکمیل آزمایش"""
    # گام ۱: تست آب‌لیمو با تورنسل آبی
    engine.add_tool_to_workbench("beaker_lemon")
    engine.add_tool_to_workbench("litmus_blue")
    step1_res = engine.execute_action(LabAction(
        action_type="DIP_INDICATOR",
        source_id="litmus_blue",
        target_id="beaker_lemon"
    ))
    assert step1_res.success is True
    assert step1_res.is_step_completed is True
    assert step1_res.measurements["resulting_color_hex"] == "#EF4444"  # سرخ
    assert step1_res.measurements["color_changed"] is True
    assert engine.state.current_step == 2

    # گام ۲: تست آب‌صابون با تورنسل سرخ
    engine.add_tool_to_workbench("beaker_soap")
    engine.add_tool_to_workbench("litmus_red")
    step2_res = engine.execute_action(LabAction(
        action_type="DIP_INDICATOR",
        source_id="litmus_red",
        target_id="beaker_soap"
    ))
    assert step2_res.success is True
    assert step2_res.is_step_completed is True
    assert step2_res.measurements["resulting_color_hex"] == "#3B82F6"  # آبی
    assert step2_res.measurements["color_changed"] is True
    assert engine.state.current_step == 3

    # گام ۳: تست آب‌مقطر با تورنسل آبی (نمونه خنثی)
    engine.add_tool_to_workbench("beaker_water")
    step3_res = engine.execute_action(LabAction(
        action_type="DIP_INDICATOR",
        source_id="litmus_blue",
        target_id="beaker_water"
    ))
    assert step3_res.success is True
    assert step3_res.is_step_completed is True
    assert step3_res.is_terminal is True
    assert step3_res.measurements["color_changed"] is False  # بدون تغییر رنگ
    assert engine.state.is_completed is True
    assert len(engine.state.recorded_observations) == 3

def test_determinism_invariant():
    """تضمین قطعیت: اجرای کنش‌های یکسان روی دو نمونه موتور خروجی کاملاً یکسان می‌دهد"""
    eng1 = AcidBaseSimulationEngine()
    eng2 = AcidBaseSimulationEngine()

    for eng in [eng1, eng2]:
        eng.add_tool_to_workbench("beaker_lemon")
        eng.add_tool_to_workbench("litmus_blue")

    res1 = eng1.execute_action(LabAction(
        action_type="DIP_INDICATOR",
        source_id="litmus_blue",
        target_id="beaker_lemon"
    ))
    res2 = eng2.execute_action(LabAction(
        action_type="DIP_INDICATOR",
        source_id="litmus_blue",
        target_id="beaker_lemon"
    ))

    assert res1.to_dict() == res2.to_dict()
    assert res1.measurements["solution_ph"] == res2.measurements["solution_ph"]
    assert res1.measurements["resulting_color_hex"] == res2.measurements["resulting_color_hex"]

def test_reset_clears_state_completely(engine):
    """تضمین پاک‌سازی کامل وضعیت پس از Reset"""
    engine.add_tool_to_workbench("beaker_lemon")
    engine.add_tool_to_workbench("litmus_blue")
    engine.execute_action(LabAction(
        action_type="DIP_INDICATOR",
        source_id="litmus_blue",
        target_id="beaker_lemon"
    ))
    assert engine.state.current_step == 2
    assert len(engine.state.workbench_tools) == 2

    # بازنشانی
    reset_state = engine.reset()
    assert reset_state.current_step == 1
    assert reset_state.workbench_tools == []
    assert reset_state.recorded_observations == []
    assert reset_state.action_history == []
    assert reset_state.is_completed is False

def test_digital_ph_meter_measurement(engine):
    """آزمون اندازه‌گیری دقیق با حسگر دیجیتال pH"""
    res = engine.execute_action(LabAction(
        action_type="MEASURE_PH",
        source_id="ph_meter",
        target_id="beaker_soap"
    ))
    assert res.success is True
    assert res.measurements["ph_value"] == 9.5
    assert res.measurements["classification"] == "بازی"
