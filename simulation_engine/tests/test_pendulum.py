import pytest
import math
from simulation_engine import (
    SimplePendulumEngine,
    LabAction,
    ErrorCategory
)

@pytest.fixture
def engine():
    return SimplePendulumEngine()

def test_pendulum_initial_state(engine):
    """بررسی وضعیت اولیه آونگ ساده"""
    state = engine.state
    assert state.experiment_id == "simple-pendulum-motion"
    assert state.current_step == 1
    assert engine.pendulum_physics.is_oscillating is False

def test_bob_before_string_error(engine):
    """خطای بستن وزنه بدون نخ به پایه"""
    engine.add_tool_to_workbench("pendulum_stand")
    engine.add_tool_to_workbench("pendulum_bob")

    res = engine.execute_action(LabAction(action_type="ATTACH_BOB", source_id="pendulum_bob"))
    assert res.success is False
    assert res.error.code == "ERR_BOB_BEFORE_STRING"
    assert res.error.category == ErrorCategory.ORDER_VIOLATION

def test_large_angle_warning_and_small_angle_physics(engine):
    """کنترل علمی محدودیت زاویه کوچک (زیر ۱۵ درجه)"""
    engine.add_tool_to_workbench("pendulum_stand")
    engine.add_tool_to_workbench("pendulum_string")
    engine.add_tool_to_workbench("pendulum_bob")

    engine.execute_action(LabAction(action_type="ATTACH_STRING", source_id="pendulum_string"))
    engine.execute_action(LabAction(action_type="ATTACH_BOB", source_id="pendulum_bob"))

    # تلاش برای انحراف با زاویه بزرگ ۴۵ درجه
    res_large = engine.execute_action(LabAction(
        action_type="DEFLECT_BOB",
        source_id="pendulum_bob",
        parameters={"angle_deg": 45.0}
    ))
    assert res_large.success is False
    assert res_large.error.code == "ERR_LARGE_ANGLE_DEVIATION"

def test_happy_path_pendulum_period(engine):
    """آزمون نوسان آونگ و اثبات T = 2*pi*sqrt(L/g)"""
    engine.add_tool_to_workbench("pendulum_stand")
    engine.add_tool_to_workbench("pendulum_string")
    engine.add_tool_to_workbench("pendulum_bob")
    engine.add_tool_to_workbench("stopwatch")

    # گام ۱: اتصال نخ با طول L=1.0 متر
    res1 = engine.execute_action(LabAction(
        action_type="ATTACH_STRING",
        source_id="pendulum_string",
        parameters={"length_m": 1.0}
    ))
    assert res1.success is True
    assert res1.is_step_completed is True

    # گام ۲: اتصال وزنه ۲۰۰ گرمی
    res2 = engine.execute_action(LabAction(
        action_type="ATTACH_BOB",
        source_id="pendulum_bob",
        parameters={"mass_kg": 0.2}
    ))
    assert res2.success is True

    # گام ۳: انحراف با زاویه کوچک ۱۰ درجه
    res3 = engine.execute_action(LabAction(
        action_type="DEFLECT_BOB",
        source_id="pendulum_bob",
        parameters={"angle_deg": 10.0}
    ))
    assert res3.success is True

    # گام ۴: رهاسازی و اندازه‌گیری با کرونومتر
    res4 = engine.execute_action(LabAction(action_type="START_OSCILLATION", source_id="stopwatch"))
    assert res4.success is True
    assert res4.is_terminal is True
    assert engine.state.is_completed is True

    # محاسبه تئوری: 2 * pi * sqrt(1.0 / 9.80665) ~= 2.006 s
    t_expected = round(2.0 * math.pi * math.sqrt(1.0 / 9.80665), 3)
    assert abs(res4.measurements["period_seconds"] - t_expected) < 0.01
