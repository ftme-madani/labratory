from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class PlantTransportState:
    color_chosen: str = "red"            # رنگ خوراکی: قرمز یا آبی
    water_volume_ml: float = 150.0       # حجم آب در لیوان
    drops_food_coloring: int = 5         # تعداد قطرات رنگ خوراکی
    is_water_poured: bool = False
    is_color_added: bool = False
    is_celery_inserted: bool = False
    observation_hours: float = 4.0       # زمان مشاهده فشرده: ۱، ۴، ۱۲، ۲۴ ساعت

    def calculate_transport_progress(self) -> Dict[str, Any]:
        """
        محاسبه علمی میزان انتقال آب در آوندهای چوبی (Xylem):
        در ساقه کرفس، سرعت صعود آب ناشی از کشش تعرقی (Transpiration pull) و مویینگی
        به‌طور متوسط بین ۰.۵ تا ۱.۵ سانتی‌متر بر ساعت در دمای اتاق است.
        """
        stalk_total_height_cm = 20.0
        # سرعت متوسط ۱ سانتی‌متر بر ساعت
        height_ascended_cm = min(stalk_total_height_cm, round(self.observation_hours * 1.0, 1))
        percentage = round((height_ascended_cm / stalk_total_height_cm) * 100.0, 1)

        # مرحله ظهور در رگبرگ‌ها معمولاً از بعد از ۴ ساعت شروع شده و در ۱۲ تا ۲۴ ساعت کامل می‌شود
        leaf_colored = self.observation_hours >= 4.0
        leaf_color_intensity = min(100, int((self.observation_hours / 24.0) * 100))

        color_fa = "سرخ" if self.color_chosen == "red" else ("آبی" if self.color_chosen == "blue" else "سبز")

        return {
            "observation_hours": self.observation_hours,
            "stalk_height_cm": stalk_total_height_cm,
            "height_ascended_cm": height_ascended_cm,
            "ascent_percentage": percentage,
            "xylem_vessels_visible": True,
            "leaf_colored": leaf_colored,
            "leaf_color_intensity_percent": leaf_color_intensity,
            "color_name_fa": color_fa,
            "scientific_mechanism": "انتقال آب از طریق آوندهای چوبی و با نیروی کشش تعرقی (Transpiration Pull) و مویینگی صورت می‌گیرد."
        }
