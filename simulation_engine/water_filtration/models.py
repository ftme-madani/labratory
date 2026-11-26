from dataclasses import dataclass, field
from typing import Dict, Any, List

# لایه‌های استاندارد صافی آب
LAYER_SPECS: Dict[str, Dict[str, Any]] = {
    "cotton": {
        "id": "cotton",
        "name_fa": "پنبه بهداشتی",
        "pore_size": "بسیار ریز (میکرومتری)",
        "captures": "ذرات معلق بسیار ریز و جلوگیری از خروج ماسه",
        "ideal_order": 1  # کف ستون
    },
    "sand": {
        "id": "sand",
        "name_fa": "ماسه بادی ریز",
        "pore_size": "متوسط (۰.۱ تا ۰.۵ میلی‌متر)",
        "captures": "ذرات معلق متوسط و گل و لای",
        "ideal_order": 2  # لایه میانی
    },
    "gravel": {
        "id": "gravel",
        "name_fa": "شن نخودی درشت",
        "pore_size": "درشت (۲ تا ۵ میلی‌متر)",
        "captures": "خرده‌سنگ‌ها، شاخه و ذرات درشت شناور",
        "ideal_order": 3  # لایه بالایی
    }
}

@dataclass
class WaterFilterState:
    layers: List[str] = field(default_factory=list)  # ترتیب قرارگیری لایه‌ها از پایین به بالا
    layer_thicknesses: Dict[str, float] = field(default_factory=lambda: {
        "cotton": 2.0,   # ضخامت به سانتی‌متر
        "sand": 5.0,
        "gravel": 4.0
    })
    is_column_ready: bool = False
    is_dirty_water_added: bool = False
    inlet_turbidity_ntu: float = 250.0  # کدورت اولیه آب گل‌آلود (بسیار کدر)
    outlet_turbidity_ntu: float = 12.0  # کدورت پس از فیلتر مناسب (زلال)

    def is_order_correct(self) -> bool:
        """
        ترتیب استاندارد از پایین به بالا در ستون قیفی:
        ۱. پنبه در خروجی انتهایی
        ۲. ماسه ریز روی پنبه
        ۳. شن درشت در بالا
        """
        return self.layers == ["cotton", "sand", "gravel"]

    def calculate_filtration_efficiency(self) -> Dict[str, Any]:
        """
        محاسبه کارایی فیلتراسیون فیزیکی:
        اگر ترتیب درست باشد، شفافیت بالای ۹۲٪ حاصل می‌شود.
        اگر ترتیب نادرست باشد (مثلاً شن در پایین و پنبه در بالا)، ماسه شسته شده یا فیلتر مسدود می‌شود.
        """
        correct = self.is_order_correct()

        if correct:
            # اثر ضخامت لایه‌ها: ضخامت بیشتر ماسه = شفافیت بالاتر
            sand_th = self.layer_thicknesses.get("sand", 5.0)
            outlet_ntu = max(5.0, round(25.0 - (sand_th * 2.5), 1))
            clarity_percent = round((1.0 - (outlet_ntu / self.inlet_turbidity_ntu)) * 100.0, 1)
            flow_rate_ml_min = max(20.0, round(80.0 - (sand_th * 6.0), 1))
            status_desc = "فیلتراسیون فیزیکی کامل و ذرات معلق به دام افتادند."
        else:
            outlet_ntu = 120.0
            clarity_percent = 52.0
            flow_rate_ml_min = 15.0
            status_desc = "به دلیل عدم رعایت ترتیب صحیح لایه‌ها، بخشی از ذرات گل یا ماسه شسته شده و آب خروجی کدر است."

        return {
            "order_correct": correct,
            "layers_current": self.layers,
            "inlet_turbidity_ntu": self.inlet_turbidity_ntu,
            "outlet_turbidity_ntu": outlet_ntu,
            "clarity_improvement_percent": clarity_percent,
            "flow_rate_ml_min": flow_rate_ml_min,
            "status_description": status_desc,
            "safety_warning": "هشدار بهداشتی: آب خروجی فقط تصفیه فیزیکی شده و فاقد ذرات معلق است، اما ممکن است حاوی میکروب و مواد شیمیایی محلول باشد و هرگز نباید نوشیده شود!"
        }
