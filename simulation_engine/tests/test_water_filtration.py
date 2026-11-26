import pytest
from simulation_engine import (
    WaterFiltrationEngine,
    LabAction,
    ErrorCategory
)

@pytest.fixture
def engine():
    return WaterFiltrationEngine()

def test_filtration_initial_state(engine):
    """بررسی وضعیت اولیه ساخت صافی آب"""
    state = engine.state
    assert state.experiment_id == "water-filtration-column"
    assert state.current_step == 1
    assert state.total_steps == 5

def test_water_before_layers_error(engine):
    """خطای ریختن آب گل‌آلود در ستون خالی بدون لایه‌های فیلتر"""
    engine.add_tool_to_workbench("filter_column_bottle")
    engine.add_tool_to_workbench("dirty_water_flask")

    engine.execute_action(LabAction(action_type="PREPARE_BOTTLE", source_id="filter_column_bottle"))

    res = engine.execute_action(LabAction(action_type="POUR_DIRTY_WATER", source_id="dirty_water_flask"))
    assert res.success is False
    assert res.error.code == "ERR_WATER_BEFORE_LAYERS"

def test_happy_path_water_filtration_and_warning(engine):
    """آزمون کامل تصفیه فیزیکی، بهبود شفافیت و نمایش هشدار عدم نوشیدن"""
    engine.add_tool_to_workbench("filter_column_bottle")
    engine.add_tool_to_workbench("cotton_layer")
    engine.add_tool_to_workbench("fine_sand_layer")
    engine.add_tool_to_workbench("gravel_layer")
    engine.add_tool_to_workbench("dirty_water_flask")
    engine.add_tool_to_workbench("collection_beaker")

    # ۱. آماده‌سازی بطری
    res1 = engine.execute_action(LabAction(action_type="PREPARE_BOTTLE", source_id="filter_column_bottle"))
    assert res1.success is True

    # ۲. چیدن لایه‌ها (پنبه در کف، ماسه در میانه، شن در بالا)
    res2 = engine.execute_action(LabAction(action_type="ADD_LAYER", source_id="cotton_layer"))
    assert res2.success is True
    assert engine.filter_physics.is_order_correct() is True

    # ۳. ریختن آب گل‌آلود
    res3 = engine.execute_action(LabAction(action_type="POUR_DIRTY_WATER", source_id="dirty_water_flask"))
    assert res3.success is True

    # ۴. عبور آب از میان لایه‌ها
    res4 = engine.execute_action(LabAction(action_type="OBSERVE_FILTRATION", source_id="filter_column_bottle"))
    assert res4.success is True
    assert res4.measurements["clarity_improvement_percent"] > 80.0

    # ۵. مقایسه آب ورودی و خروجی و بررسی هشدار بهداشتی
    res5 = engine.execute_action(LabAction(action_type="COMPARE_WATER", source_id="collection_beaker"))
    assert res5.success is True
    assert res5.is_terminal is True
    assert engine.state.is_completed is True
    assert "نباید نوشیده شود" in res5.measurements["safety_warning"]
