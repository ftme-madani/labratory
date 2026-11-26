import pytest
from simulation_engine import (
    PlantWaterTransportEngine,
    LabAction,
    ErrorCategory
)

@pytest.fixture
def engine():
    return PlantWaterTransportEngine()

def test_plant_initial_state(engine):
    """بررسی وضعیت اولیه آزمایش صعود آب در گیاه"""
    state = engine.state
    assert state.experiment_id == "plant-water-transport-celery"
    assert state.current_step == 1
    assert state.total_steps == 5

def test_celery_in_clear_water_error(engine):
    """خطای قرار دادن کرفس در آب زلال بدون افزودن رنگ خوراکی"""
    engine.add_tool_to_workbench("glass_cup")
    engine.add_tool_to_workbench("water_pitcher")
    engine.add_tool_to_workbench("celery_stalk")

    engine.execute_action(LabAction(action_type="POUR_WATER", source_id="water_pitcher"))

    res = engine.execute_action(LabAction(action_type="INSERT_CELERY", source_id="celery_stalk"))
    assert res.success is False
    assert res.error.code == "ERR_CELERY_IN_CLEAR_WATER"

def test_happy_path_plant_water_transport(engine):
    """آزمون کامل انتقال آب رنگی در آوندهای چوبی کرفس با گذر زمان"""
    engine.add_tool_to_workbench("glass_cup")
    engine.add_tool_to_workbench("water_pitcher")
    engine.add_tool_to_workbench("food_coloring")
    engine.add_tool_to_workbench("celery_stalk")

    # ۱. ریختن آب
    res1 = engine.execute_action(LabAction(action_type="POUR_WATER", source_id="water_pitcher"))
    assert res1.success is True

    # ۲. چکاندن رنگ خوراکی قرمز
    res2 = engine.execute_action(LabAction(
        action_type="ADD_COLOR",
        source_id="food_coloring",
        parameters={"color": "red"}
    ))
    assert res2.success is True

    # ۳. قرار دادن کرفس
    res3 = engine.execute_action(LabAction(action_type="INSERT_CELERY", source_id="celery_stalk"))
    assert res3.success is True

    # ۴. شبیه‌سازی ۱۲ ساعت زمان فشرده
    res4 = engine.execute_action(LabAction(
        action_type="SET_TIME",
        source_id="celery_stalk",
        parameters={"hours": 12.0}
    ))
    assert res4.success is True
    assert res4.measurements["height_ascended_cm"] >= 12.0
    assert res4.measurements["leaf_colored"] is True

    # ۵. مشاهده نهایی و تبیین کشش تعرقی
    res5 = engine.execute_action(LabAction(action_type="EXAMINE_XYLEM", source_id="celery_stalk"))
    assert res5.success is True
    assert res5.is_terminal is True
    assert engine.state.is_completed is True
    assert "آوند چوبی" in res5.observations[0]
