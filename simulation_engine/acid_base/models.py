from dataclasses import dataclass
from typing import Dict, Optional

@dataclass(frozen=True)
class AqueousSolution:
    id: str
    name_fa: str
    chemical_formula: str
    nominal_ph: float
    color_hex: str
    description: str

@dataclass(frozen=True)
class ChemicalIndicator:
    id: str
    name_fa: str
    acidic_color_hex: str
    basic_color_hex: str
    neutral_color_hex: str
    transition_low_ph: float
    transition_high_ph: float
    description: str

# مخرن ثابت و علمی محلول‌های استاندارد کتب درسی (علوم هشتم، ص ۱۶)
KNOWN_SOLUTIONS: Dict[str, AqueousSolution] = {
    "beaker_lemon": AqueousSolution(
        id="beaker_lemon",
        name_fa="محلول آب‌لیمو (اسید سیتریک)",
        chemical_formula="C6H8O7 (aq)",
        nominal_ph=2.5,
        color_hex="#FEF08A",
        description="حاوی یون‌های هیدرونیوم H+ و اسیدی ضعیف"
    ),
    "beaker_soap": AqueousSolution(
        id="beaker_soap",
        name_fa="محلول آب‌صابون (محیط بازی)",
        chemical_formula="R-COO- Na+ (aq)",
        nominal_ph=9.5,
        color_hex="#CCFBF1",
        description="حاوی یون‌های هیدروکسید OH- و خاصیت قلیایی"
    ),
    "beaker_water": AqueousSolution(
        id="beaker_water",
        name_fa="آب‌مقطر خالص (خنثی)",
        chemical_formula="H2O (l)",
        nominal_ph=7.0,
        color_hex="#F0F9FF",
        description="آب خالص با غلظت برابر یون‌های H+ و OH- و pH خنثی"
    ),
    "beaker_vinegar": AqueousSolution(
        id="beaker_vinegar",
        name_fa="سرکه خوراکی (اسید استیک)",
        chemical_formula="CH3COOH (aq)",
        nominal_ph=2.9,
        color_hex="#FEF9C3",
        description="محلول اسید استیک خانگی"
    ),
    "beaker_baking_soda": AqueousSolution(
        id="beaker_baking_soda",
        name_fa="محلول جوش شیرین",
        chemical_formula="NaHCO3 (aq)",
        nominal_ph=8.4,
        color_hex="#F1F5F9",
        description="نمک بازی سدیم هیدروژن‌کربنات"
    )
}

# شناساگرهای استاندارد با منحنی دقیق تغییر رنگ
KNOWN_INDICATORS: Dict[str, ChemicalIndicator] = {
    "litmus_blue": ChemicalIndicator(
        id="litmus_blue",
        name_fa="کاغذ تورنسل آبی",
        acidic_color_hex="#EF4444",   # سرخ در اسید
        basic_color_hex="#3B82F6",    # آبی بدون تغییر در باز
        neutral_color_hex="#3B82F6",  # آبی در خنثی
        transition_low_ph=4.5,
        transition_high_ph=8.3,
        description="شناساگر اسیدها؛ در تماس با محلول pH < 4.5 به رنگ سرخ درمی‌آید."
    ),
    "litmus_red": ChemicalIndicator(
        id="litmus_red",
        name_fa="کاغذ تورنسل سرخ",
        acidic_color_hex="#EF4444",   # سرخ بدون تغییر در اسید
        basic_color_hex="#3B82F6",    # آبی در باز
        neutral_color_hex="#EF4444",  # سرخ در خنثی
        transition_low_ph=4.5,
        transition_high_ph=8.3,
        description="شناساگر بازها؛ در تماس با محلول pH > 8.3 به رنگ آبی درمی‌آید."
    ),
    "phenolphthalein": ChemicalIndicator(
        id="phenolphthalein",
        name_fa="معرف فنل‌فتالئین",
        acidic_color_hex="#F8FAFC",   # بی‌رنگ در اسید
        basic_color_hex="#E11D48",    # ارغوانی / صورتی پررنگ در باز
        neutral_color_hex="#F8FAFC",  # بی‌رنگ در خنثی
        transition_low_ph=8.2,
        transition_high_ph=10.0,
        description="در pH کمتر از ۸.۲ بی‌رنگ و در محیط‌های بازی شدیداً ارغوانی می‌شود."
    )
}
