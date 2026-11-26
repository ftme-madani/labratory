from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class MixtureState:
    sand_mass_g: float = 10.0
    salt_mass_g: float = 10.0
    water_volume_ml: float = 0.0
    is_salt_dissolved: bool = False
    is_sand_filtered: bool = False
    is_water_evaporated: bool = False
    is_salt_recovered: bool = False
    temperature_celsius: float = 25.0
    has_heat_source: bool = False

    @property
    def has_liquid(self) -> bool:
        return self.water_volume_ml > 0

    @property
    def liquid_phase_description(self) -> str:
        if not self.has_liquid:
            return "مخلوط خشک جامد"
        if not self.is_sand_filtered:
            return "سوسپانسیون ناهمگن آب، نمک و ماسه ته‌نشین‌شده"
        if not self.is_water_evaporated:
            return "محلول همگن و زلال آب‌نمک"
        return "بلورهای متبلور نمک خشک"
