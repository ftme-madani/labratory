import pytest
from simulation_engine import (
    SimpleCircuitSimulationEngine,
    LabAction,
    ErrorCategory
)

@pytest.fixture
def engine():
    return SimpleCircuitSimulationEngine()

def test_circuit_initial_state(engine):
    """بررسی وضعیت اولیه مدار باز"""
    state = engine.state
    assert state.experiment_id == "exp-simple-circuit"
    assert state.current_step == 1
    assert engine.circuit_physics.current_amperes == 0.0
    assert engine.circuit_physics.is_bulb_lit is False

def test_short_circuit_prevention(engine):
    """آزمون تشخیص و پیشگیری از اتصال کوتاه مستقیم دو قطب باتری بدون لامپ"""
    engine.add_tool_to_workbench("battery_cell")
    engine.add_tool_to_workbench("connecting_wires")
    engine.add_tool_to_workbench("switch_key")

    # تلاش برای سیم‌کشی بدون افزودن لامپ به مدار
    res = engine.execute_action(LabAction(action_type="CONNECT_COMPONENTS", source_id="wires"))
    assert res.success is False
    assert res.error.code == "ERR_CIRCUIT_WITHOUT_LOAD"
    assert "اتصال کوتاه" in res.error.description

def test_switch_before_wiring_error(engine):
    """خطای تغییر کلید قبل از سیم‌کشی مدار"""
    res = engine.execute_action(LabAction(action_type="CLOSE_SWITCH", source_id="switch"))
    assert res.success is False
    assert res.error.code == "ERR_SWITCH_BEFORE_WIRING"

def test_measure_on_open_circuit_error(engine):
    """خطای اندازه‌گیری جریان در حالی که کلید مدار باز است"""
    engine.add_tool_to_workbench("battery_cell")
    engine.add_tool_to_workbench("light_bulb")
    engine.add_tool_to_workbench("switch_key")
    engine.add_tool_to_workbench("connecting_wires")
    engine.add_tool_to_workbench("ammeter")

    # سیم‌کشی
    engine.execute_action(LabAction(action_type="CONNECT_COMPONENTS", source_id="wires"))

    # تلاش برای اندازه‌گیری قبل از بستن کلید
    res = engine.execute_action(LabAction(action_type="MEASURE_CURRENT", source_id="ammeter"))
    assert res.success is False
    assert res.error.code == "ERR_MEASURE_ON_OPEN_CIRCUIT"

def test_happy_path_circuit_and_ohm_law(engine):
    """آزمون گام‌به‌گام بستن مدار، روشن شدن لامپ و اثبات رابطه قانون اهم"""
    # گام ۱: سیم‌کشی
    engine.add_tool_to_workbench("battery_cell")
    engine.add_tool_to_workbench("light_bulb")
    engine.add_tool_to_workbench("switch_key")
    engine.add_tool_to_workbench("connecting_wires")
    res1 = engine.execute_action(LabAction(action_type="CONNECT_COMPONENTS", source_id="wires"))
    assert res1.success is True
    assert res1.is_step_completed is True
    assert engine.state.current_step == 2
    assert engine.circuit_physics.is_loop_connected is True

    # گام ۲: بستن کلید مدار
    res2 = engine.execute_action(LabAction(action_type="CLOSE_SWITCH", source_id="switch_key"))
    assert res2.success is True
    assert res2.is_step_completed is True
    assert engine.circuit_physics.is_bulb_lit is True
    assert engine.circuit_physics.current_amperes > 0.1
    assert engine.state.current_step == 3

    # گام ۳: اندازه‌گیری با آمپرمتر و محاسبه قانون اهم (R = V / I)
    engine.add_tool_to_workbench("ammeter")
    res3 = engine.execute_action(LabAction(action_type="MEASURE_CURRENT", source_id="ammeter"))
    assert res3.success is True
    assert res3.is_step_completed is True
    assert res3.is_terminal is True
    assert engine.state.is_completed is True
    # ولتاژ ۱.۵V تقسیم بر مقاومت کل ~۱۰.۱ اهم -> مقدار مقاومت محاسبه‌شده نزدیک ۱۰ اهم
    assert res3.measurements["calculated_resistance_ohms"] == 10.1
    assert "قانون اهم" in res3.measurements["law_verified"]
