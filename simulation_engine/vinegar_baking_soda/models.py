from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class VinegarReactionState:
    vinegar_volume_ml: float = 50.0       # حجم سرکه به میلی‌لیتر (اسید استیک ۵٪)
    baking_soda_mass_g: float = 5.0       # جرم جوش‌شیرین به گرم (سدیم هیدروژن‌کربنات)
    is_vinegar_added: bool = False
    is_soda_added: bool = False
    is_reaction_triggered: bool = False
    co2_gas_volume_ml: float = 0.0        # حجم گاز دی‌اکسید کربن تولیدی
    foam_height_percent: float = 0.0      # درصد ارتفاع کف در لیوان
    reaction_duration_seconds: float = 0.0
    temperature_drop_celsius: float = 0.0 # واکنش گرماگیر و افت اندک دما
    limiting_reactant: str = "none"       # ماده محدودکننده

    def calculate_stoichiometry(self) -> Dict[str, Any]:
        """
        محاسبه علمی استوکیومتری واکنش:
        CH3COOH + NaHCO3 -> CH3COONa + H2O + CO2
        جرم مولی جوش‌شیرین NaHCO3 = 84 g/mol
        جرم مولی اسید استیک CH3COOH = 60 g/mol
        سرکه خوراکی دارای چگالی ~1.01 g/ml و غلظت حدود 5% وزنی است (~0.05 g اسید در هر ml سرکه)
        """
        acetic_acid_mass_g = self.vinegar_volume_ml * 0.05
        moles_acid = acetic_acid_mass_g / 60.05
        moles_soda = self.baking_soda_mass_g / 84.01

        if moles_acid < moles_soda:
            moles_co2 = moles_acid
            limiting = "سرکه (اسید استیک)"
        else:
            moles_co2 = moles_soda
            limiting = "جوش‌شیرین (سدیم هیدروژن‌کربنات)"

        # در شرایط اتاق ۱ مول گاز معادل حدود ۲۴,۴۰۰ میلی‌لیتر است
        co2_ml = round(moles_co2 * 24400.0, 1)

        # ارتفاع کف تابعی از سرعت تولید گاز و حجم سرکه است (حداکثر ۱۰۰٪)
        foam = min(100.0, round((co2_ml / 15.0) + (self.vinegar_volume_ml * 0.3), 1))
        
        # واکنش به دلیل گرماگیر بودن پیوندها حدود ۰.۵ تا ۲.۵ درجه سانتی‌گراد خنک می‌شود
        temp_drop = round(min(2.8, (co2_ml / 600.0) * 1.5 + 0.4), 1)

        return {
            "moles_acid": round(moles_acid, 4),
            "moles_soda": round(moles_soda, 4),
            "moles_co2": round(moles_co2, 4),
            "co2_volume_ml": co2_ml,
            "limiting_reactant": limiting,
            "foam_height_percent": foam,
            "temperature_drop_celsius": temp_drop
        }
