import pytest
from simulation_engine import (
    VinegarBakingSodaEngine,
    LabAction,
    ErrorCategory
)

@pytest.fixture
def engine():
    return VinegarBakingSodaEngine()

def test_vinegar_initial_state(engine):
    """بررسی وضعیت اولیه واکنش سرکه و جوش‌شیرین"""
    state = engine.state
    assert state.experiment_id == "vinegar-baking-soda-reaction"
    assert state.current_step == 1
    assert state.total_steps == 4
    assert engine.reaction_physics.is_reaction_triggered is False

def test_soda_before_vinegar_error(engine):
    """خطای پداگوژیک: تلاش برای افزودن جوش‌شیرین به ظرف خالی بدون سرکه"""
    engine.add_tool_to_workbench("beaker_glass")
    engine.add_tool_to_workbench("jar_baking_soda")

    res = engine.execute_action(LabAction(action_type="ADD_BAKING_SODA", source_id="jar_baking_soda"))
    assert res.success is False
    assert res.error.code == "ERR_SODA_BEFORE_VINEGAR"
    assert res.error.category == ErrorCategory.ORDER_VIOLATION

def test_happy_path_and_stoichiometry(engine):
    """آزمون گام‌به‌گام موفق واکنش، محاسبه گاز CO2 و فوران کف"""
    engine.add_tool_to_workbench("beaker_glass")
    engine.add_tool_to_workbench("bottle_vinegar")
    engine.add_tool_to_workbench("jar_baking_soda")

    # گام ۱: قرار دادن لیوان
    res1 = engine.execute_action(LabAction(action_type="PLACE_BEAKER", source_id="beaker_glass"))
    assert res1.success is True
    assert res1.is_step_completed is True
    assert engine.state.current_step == 2

    # گام ۲: ریختن ۵۰ میلی‌لیتر سرکه
    res2 = engine.execute_action(LabAction(
        action_type="POUR_VINEGAR",
        source_id="bottle_vinegar",
        parameters={"volume_ml": 60.0}
    ))
    assert res2.success is True
    assert res2.is_step_completed is True
    assert engine.reaction_physics.vinegar_volume_ml == 60.0
    assert engine.state.current_step == 3

    # گام ۳: افزودن ۸ گرم جوش‌شیرین
    res3 = engine.execute_action(LabAction(
        action_type="ADD_BAKING_SODA",
        source_id="jar_baking_soda",
        parameters={"mass_g": 8.0}
    ))
    assert res3.success is True
    assert res3.is_step_completed is True
    assert engine.state.current_step == 4

    # گام ۴: مشاهده واکنش و نتایج استوکیومتری
    res4 = engine.execute_action(LabAction(action_type="OBSERVE_REACTION", source_id="beaker_glass"))
    assert res4.success is True
    assert res4.is_step_completed is True
    assert res4.is_terminal is True
    assert engine.state.is_completed is True
    assert res4.measurements["co2_volume_ml"] > 500.0
    assert res4.measurements["foam_height_percent"] > 20.0
    assert "CO2" in res4.measurements["reaction_equation"]
