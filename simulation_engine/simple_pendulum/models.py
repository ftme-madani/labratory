import math
from dataclasses import dataclass
from typing import Dict, Any, List

GRAVITY_EARTH = 9.80665  # شتاب گرانش زمین بر حسب متر بر مجذور ثانیه

@dataclass
class PendulumPhysicsState:
    string_length_m: float = 0.8         # طول نخ به متر (۰.۲ تا ۱.۵ متر)
    bob_mass_kg: float = 0.1             # جرم وزنه به کیلوگرم (۰.۰۵ تا ۰.۵ کیلوگرم)
    initial_angle_deg: float = 10.0      # زاویه انحراف اولیه (دامنه کوچک: زیر ۱۵ درجه)
    is_string_attached: bool = False
    is_bob_attached: bool = False
    is_oscillating: bool = False
    oscillations_count: int = 10         # تعداد نوسانات شمارش‌شده
    elapsed_time_seconds: float = 0.0

    @property
    def period_seconds(self) -> float:
        """
        محاسبه دوره تناوب آونگ ساده در تقریب زوایای کوچک:
        T = 2 * pi * sqrt(L / g)
        توجه: در تقریب زوایای کوچک (sin theta ~= theta)، دوره تناوب مستقل از جرم وزنه (m) است.
        """
        if self.string_length_m <= 0:
            return 0.0
        return round(2.0 * math.pi * math.sqrt(self.string_length_m / GRAVITY_EARTH), 3)

    @property
    def frequency_hz(self) -> float:
        T = self.period_seconds
        return round(1.0 / T, 3) if T > 0 else 0.0

    def calculate_motion_data(self) -> Dict[str, Any]:
        T = self.period_seconds
        total_time = round(self.oscillations_count * T, 2)
        t_squared = round(T ** 2, 3)
        return {
            "length_m": self.string_length_m,
            "mass_kg": self.bob_mass_kg,
            "period_seconds": T,
            "period_squared": t_squared,
            "frequency_hz": self.frequency_hz,
            "oscillations_count": self.oscillations_count,
            "total_time_seconds": total_time,
            "is_small_angle": self.initial_angle_deg <= 15.0,
            "scientific_takeaway": "دوره تناوب تنها به طول نخ و شتاب گرانش بستگی دارد و جرم وزنه تأثیری در آن ندارد."
        }
