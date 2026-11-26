import pytest
from simulation_engine.schema import LabAction, ErrorCategory
from simulation_engine.registry import get_simulation_engine
from simulation_engine.hints.catalog import HINT_CATALOG

def test_vinegar_misconceptions():
    engine = get_simulation_engine("vinegar-baking-soda-reaction")
    assert engine is not None

    # ۱. فرضیه‌سازی اشتباه گاز اکسیژن به جای دی‌اکسید کربن
    res1 = engine.execute_action(LabAction(
        action_type="SUBMIT_PREDICTION",
        source_id="beaker_glass",
        parameters={"predicted_gas": "oxygen"}
    ))
    assert res1.success is False
    assert res1.error.code == "ERR_MISCONCEPTION_GAS_TYPE"
    assert res1.error.category == ErrorCategory.SCIENTIFIC_MISCONCEPTION
    assert res1.error.code in HINT_CATALOG

    # ۲. تصور نادرست واکنش بی‌پایان با ریختن مداوم جوش‌شیرین
    res2 = engine.execute_action(LabAction(
        action_type="SUBMIT_PREDICTION",
        source_id="beaker_glass",
        parameters={"predict_infinite_reaction": True}
    ))
    assert res2.success is False
    assert res2.error.code == "ERR_LIMITING_REACTANT_OVEREATING"
    assert res2.error.category == ErrorCategory.SCIENTIFIC_MISCONCEPTION

    # ۳. اشتباه گرفتن جوشش شیمیایی با جوشیدن فیزیکی
    res3 = engine.execute_action(LabAction(
        action_type="SUBMIT_PREDICTION",
        source_id="beaker_glass",
        parameters={"is_boiling": True}
    ))
    assert res3.success is False
    assert res3.error.code == "ERR_MISCONCEPTION_BOILING_VS_REACTION"

def test_pendulum_misconceptions():
    engine = get_simulation_engine("simple-pendulum-motion")
    assert engine is not None

    # ۱. تصور وابستگی دوره تناوب به جرم وزنه
    res1 = engine.execute_action(LabAction(
        action_type="SUBMIT_PREDICTION",
        source_id="pendulum_bob",
        parameters={"predicted_effect": "mass_increases_period"}
    ))
    assert res1.success is False
    assert res1.error.code == "ERR_PENDULUM_MASS_DEPENDENCE"
    assert res1.error.category == ErrorCategory.SCIENTIFIC_MISCONCEPTION
    assert res1.error.code in HINT_CATALOG

    # ۲. تصور معکوس در مورد رابطه طول نخ و زمان نوسان
    res2 = engine.execute_action(LabAction(
        action_type="SUBMIT_PREDICTION",
        source_id="pendulum_string",
        parameters={"predicted_effect": "longer_is_faster"}
    ))
    assert res2.success is False
    assert res2.error.code == "ERR_PENDULUM_LENGTH_INVERSE"

def test_plant_transport_misconceptions():
    engine = get_simulation_engine("plant-water-transport-celery")
    assert engine is not None

    # ۱. تصور انتقال آب از پوست یا بافت گوشتی بدون آوند
    res1 = engine.execute_action(LabAction(
        action_type="SUBMIT_PREDICTION",
        source_id="celery_stalk",
        parameters={"predicted_path": "skin"}
    ))
    assert res1.success is False
    assert res1.error.code == "ERR_MISCONCEPTION_XYLEM_PATH"
    assert res1.error.code in HINT_CATALOG

    # ۲. نادیده گرفتن نقش مکش تعرقی برگ‌ها
    res2 = engine.execute_action(LabAction(
        action_type="SUBMIT_PREDICTION",
        source_id="celery_stalk",
        parameters={"leaves_needed": False}
    ))
    assert res2.success is False
    assert res2.error.code == "ERR_MISCONCEPTION_NO_LEAVES_NEEDED"

def test_density_column_misconceptions():
    engine = get_simulation_engine("liquid-density-column")
    assert engine is not None

    # ۱. خلط مفهوم حجم بیشتر با چگالی بیشتر
    res1 = engine.execute_action(LabAction(
        action_type="SUBMIT_PREDICTION",
        source_id="measuring_cylinder",
        parameters={"prediction": "volume_determines_layer"}
    ))
    assert res1.success is False
    assert res1.error.code == "ERR_DENSITY_VOLUME_CONFUSION"
    assert res1.error.code in HINT_CATALOG

    # ۲. تصور ته‌نشینی روغن به دلیل گرانروی و غلظت ظاهری
    res2 = engine.execute_action(LabAction(
        action_type="SUBMIT_PREDICTION",
        source_id="measuring_cylinder",
        parameters={"prediction": "oil_bottom"}
    ))
    assert res2.success is False
    assert res2.error.code == "ERR_MISCONCEPTION_VISCOSITY_DENSITY"

    # ۳. غفلت از امتزاج‌ناپذیری مایعات
    res3 = engine.execute_action(LabAction(
        action_type="SUBMIT_PREDICTION",
        source_id="measuring_cylinder",
        parameters={"prediction": "all_liquids_layer"}
    ))
    assert res3.success is False
    assert res3.error.code == "ERR_MISCONCEPTION_MISCIBILITY_IGNORED"

def test_water_filtration_misconceptions():
    engine = get_simulation_engine("water-filtration-column")
    assert engine is not None

    # ۱. ادعای آشامیدنی بودن آب خروجی صافی فیزیکی
    res1 = engine.execute_action(LabAction(
        action_type="DRINK_WATER",
        source_id="collection_beaker",
        parameters={"is_potable": True}
    ))
    assert res1.success is False
    assert res1.error.code == "ERR_MISCONCEPTION_POTABLE_WATER"
    assert res1.error.category == ErrorCategory.HAZARDOUS_ACTION
    assert res1.error.code in HINT_CATALOG

    # ۲. ادعای حذف نمک حل‌شده با صافی
    res2 = engine.execute_action(LabAction(
        action_type="SUBMIT_PREDICTION",
        source_id="filter_column_bottle",
        parameters={"prediction": "removes_salt"}
    ))
    assert res2.success is False
    assert res2.error.code == "ERR_FILTER_SOLUBLE_SUBSTANCES"

    # ۳. چینش معکوس لایه‌ها
    engine.execute_action(LabAction(action_type="PREPARE_BOTTLE", source_id="filter_column_bottle"))
    res3 = engine.execute_action(LabAction(
        action_type="ADD_LAYER",
        source_id="filter_column_bottle",
        parameters={"layers": ["cotton", "gravel", "sand"]}
    ))
    assert res3.success is False
    assert res3.error.code == "ERR_INVERTED_FILTER_LAYERS"
    assert res3.error.category == ErrorCategory.ORDER_VIOLATION

def test_acid_base_misconceptions():
    engine = get_simulation_engine("acid-base-indicators")
    assert engine is not None

    # ۱. پیش‌بینی ارغوانی شدن فنل‌فتالئین در اسید
    res1 = engine.execute_action(LabAction(
        action_type="SUBMIT_PREDICTION",
        source_id="phenolphthalein",
        parameters={"prediction": "acid_is_pink"}
    ))
    assert res1.success is False
    assert res1.error.code == "ERR_PHENOLPHTHALEIN_ACID_MISINTERPRETATION"
    assert res1.error.code in HINT_CATALOG

    # ۲. پیش‌بینی غیرخنثی بودن آب خالص
    res2 = engine.execute_action(LabAction(
        action_type="SUBMIT_PREDICTION",
        source_id="beaker_water",
        parameters={"prediction": "water_is_acid"}
    ))
    assert res2.success is False
    assert res2.error.code == "ERR_WATER_PH_MISCONCEPTION"

def test_circuit_misconceptions():
    engine = get_simulation_engine("simple-electric-circuit-ohm")
    assert engine is not None

    # پیش‌بینی معکوس رابطه ولتاژ و شدت جریان
    res = engine.execute_action(LabAction(
        action_type="SUBMIT_PREDICTION",
        source_id="battery_pack",
        parameters={"prediction": "higher_voltage_less_current"}
    ))
    assert res.success is False
    assert res.error.code == "ERR_VOLTAGE_CURRENT_MISCONCEPTION"
    assert res.error.code in HINT_CATALOG

def test_mixture_misconceptions():
    engine = get_simulation_engine("mixture-separation-sand-salt")
    assert engine is not None

    # شعله مستقیم به نمک خشک پس از تبخیر
    res = engine.execute_action(LabAction(
        action_type="SUBMIT_PREDICTION",
        source_id="evaporating_dish",
        parameters={"prediction": "boil_dry"}
    ))
    assert res.success is False
    assert res.error.code == "ERR_BOIL_DRY_EXPLOSION"
    assert res.error.category == ErrorCategory.HAZARDOUS_ACTION
    assert res.error.code in HINT_CATALOG
