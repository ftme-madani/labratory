import pytest
from simulation_engine import (
    LiquidDensityColumnEngine,
    LabAction,
    ErrorCategory
)

@pytest.fixture
def engine():
    return LiquidDensityColumnEngine()

def test_density_initial_state(engine):
    """بررسی وضعیت اولیه ستون چگالی مایعات"""
    state = engine.state
    assert state.experiment_id == "liquid-density-column"
    assert state.current_step == 1

def test_pour_without_cylinder_error(engine):
    """خطای تلاش برای ریختن عسل قبل از گذاشتن استوانه مدرج"""
    engine.add_tool_to_workbench("flask_honey")

    res = engine.execute_action(LabAction(action_type="POUR_HONEY", source_id="flask_honey"))
    assert res.success is False
    assert res.error.code == "ERR_POUR_WITHOUT_CYLINDER"

def test_happy_path_density_stacking(engine):
    """آزمون تفکیک فازها و شناوری مایعات بر اساس چگالی: عسل در کف، آب در میانه، روغن در بالا"""
    engine.add_tool_to_workbench("measuring_cylinder")
    engine.add_tool_to_workbench("flask_honey")
    engine.add_tool_to_workbench("flask_water")
    engine.add_tool_to_workbench("flask_oil")

    # ۱. استوانه مدرج
    res1 = engine.execute_action(LabAction(action_type="PLACE_CYLINDER", source_id="measuring_cylinder"))
    assert res1.success is True

    # ۲. ریختن ۳۰ میلی‌لیتر عسل
    res2 = engine.execute_action(LabAction(
        action_type="POUR_HONEY",
        source_id="flask_honey",
        parameters={"volume_ml": 30.0}
    ))
    assert res2.success is True

    # ۳. ریختن ۴۰ میلی‌لیتر آب
    res3 = engine.execute_action(LabAction(
        action_type="POUR_WATER",
        source_id="flask_water",
        parameters={"volume_ml": 40.0}
    ))
    assert res3.success is True

    # ۴. ریختن ۳۰ میلی‌لیتر روغن
    res4 = engine.execute_action(LabAction(
        action_type="POUR_OIL",
        source_id="flask_oil",
        parameters={"volume_ml": 30.0}
    ))
    assert res4.success is True

    # ۵. مشاهده تفکیک فازها
    res5 = engine.execute_action(LabAction(action_type="OBSERVE_LAYERS", source_id="measuring_cylinder"))
    assert res5.success is True
    assert res5.is_terminal is True
    assert engine.state.is_completed is True

    stack = res5.measurements["layers_equilibrium_order"]
    assert len(stack) == 3
    # عسل (۱.۴۲) باید لایه ۱ (کف)، آب (۱.۰۰) لایه ۲ (وسط)، روغن (۰.۹۱) لایه ۳ (رویی) باشد
    assert stack[0]["liquid_id"] == "honey"
    assert stack[1]["liquid_id"] == "water"
    assert stack[2]["liquid_id"] == "oil"
