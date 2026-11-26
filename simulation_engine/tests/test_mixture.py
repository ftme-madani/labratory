import pytest
from simulation_engine import (
    MixtureSeparationEngine,
    LabAction,
    ErrorCategory
)

@pytest.fixture
def engine():
    return MixtureSeparationEngine()

def test_mixture_initial_state(engine):
    """بررسی وضعیت اولیه آزمایش جداسازی مخلوط"""
    state = engine.state
    assert state.experiment_id == "exp-mixture-separation"
    assert state.current_step == 1
    assert state.total_steps == 3
    assert engine.mixture_physics.has_liquid is False

def test_filter_without_water_error(engine):
    """خطای تلاش برای صاف کردن پودر خشک بدون حل کردن در آب"""
    engine.add_tool_to_workbench("beaker_sand_salt")
    engine.add_tool_to_workbench("funnel_filter_paper")

    res = engine.execute_action(LabAction(action_type="FILTER_MIXTURE", source_id="funnel"))
    assert res.success is False
    assert res.error.code == "ERR_FILTER_WITHOUT_DISSOLUTION"
    assert res.error.category == ErrorCategory.MISSING_PRECONDITION

def test_heat_before_filter_error(engine):
    """خطای علمی حرارت دادن قبل از فیلتراسیون ماسه"""
    engine.add_tool_to_workbench("beaker_sand_salt")
    engine.add_tool_to_workbench("wash_bottle_water")
    engine.add_tool_to_workbench("evaporating_dish")
    engine.add_tool_to_workbench("bunsen_burner")

    # گام ۱: حل کردن نمک
    engine.execute_action(LabAction(action_type="ADD_WATER_AND_STIR", source_id="wash_bottle_water"))

    # تلاش برای حرارت دادن قبل از صاف کردن
    res = engine.execute_action(LabAction(action_type="HEAT", source_id="bunsen_burner"))
    assert res.success is False
    assert res.error.code == "ERR_HEAT_BEFORE_FILTER"
    assert res.error.category == ErrorCategory.ORDER_VIOLATION

def test_happy_path_mixture_separation(engine):
    """آزمون اجرای کامل و موفقیت‌آمیز جداسازی ماسه، نمک و آب"""
    # گام ۱: افزودن آب و انحلال
    engine.add_tool_to_workbench("beaker_sand_salt")
    engine.add_tool_to_workbench("wash_bottle_water")
    res1 = engine.execute_action(LabAction(action_type="ADD_WATER_AND_STIR", source_id="wash_bottle_water"))
    assert res1.success is True
    assert res1.is_step_completed is True
    assert engine.mixture_physics.is_salt_dissolved is True
    assert engine.state.current_step == 2

    # گام ۲: فیلتراسیون ماسه با قیف و کاغذ صافی
    engine.add_tool_to_workbench("funnel_filter_paper")
    res2 = engine.execute_action(LabAction(action_type="FILTER_MIXTURE", source_id="funnel"))
    assert res2.success is True
    assert res2.is_step_completed is True
    assert engine.mixture_physics.is_sand_filtered is True
    assert engine.state.current_step == 3

    # گام ۳: تبخیر آب و بازیابی بلور نمک روی شعله بونزن
    engine.add_tool_to_workbench("evaporating_dish")
    engine.add_tool_to_workbench("bunsen_burner")
    res3 = engine.execute_action(LabAction(action_type="HEAT", source_id="bunsen_burner"))
    assert res3.success is True
    assert res3.is_step_completed is True
    assert res3.is_terminal is True
    assert engine.mixture_physics.is_salt_recovered is True
    assert engine.state.is_completed is True
    assert res3.measurements["salt_recovered_g"] == 10.0
