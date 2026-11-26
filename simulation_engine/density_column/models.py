from dataclasses import dataclass, field
from typing import Dict, Any, List

# ثوابت چگالی مایعات استاندارد کتاب علوم تجربی بر حسب g/cm3 (یا g/ml)
LIQUID_DENSITIES: Dict[str, Dict[str, Any]] = {
    "honey": {
        "id": "honey",
        "name_fa": "عسل طبیعی",
        "density_g_ml": 1.42,
        "color_hex": "#D97706",
        "viscosity": "بسیار بالا",
        "immiscible_with": ["oil"],
        "miscible_with": ["water_slow"]  # در آب بدون هم زدن شدید سریع حل نمی‌شود
    },
    "water": {
        "id": "water",
        "name_fa": "آب مقطر رنگی",
        "density_g_ml": 1.00,
        "color_hex": "#0284C7",
        "viscosity": "پایین",
        "immiscible_with": ["oil"],
        "miscible_with": ["honey_slow"]
    },
    "oil": {
        "id": "oil",
        "name_fa": "روغن مایع گیاهی",
        "density_g_ml": 0.91,
        "color_hex": "#FBBF24",
        "viscosity": "متوسط",
        "immiscible_with": ["water", "honey"],
        "miscible_with": []
    }
}

@dataclass
class LiquidLayer:
    liquid_id: str
    volume_ml: float
    added_order: int

@dataclass
class DensityColumnState:
    layers: List[LiquidLayer] = field(default_factory=list)
    cylinder_ready: bool = False

    def add_liquid(self, liquid_id: str, volume_ml: float = 30.0) -> None:
        self.layers.append(LiquidLayer(
            liquid_id=liquid_id,
            volume_ml=volume_ml,
            added_order=len(self.layers) + 1
        ))

    def calculate_equilibrium_stack(self) -> List[Dict[str, Any]]:
        """
        محاسبه وضعیت تعادل هیدرواستاتیک:
        به دلیل تفاوت چگالی و عدم امتزاج، مایعات در ستون تعادلی از چگال‌ترین (پایین) به سبک‌ترین (بالا) مرتب می‌شوند:
        ۱. عسل (چگالی ۱.۴۲) -> کف ظرف
        ۲. آب (چگالی ۱.۰۰) -> لایه میانی
        ۳. روغن (چگالی ۰.۹۱) -> لایه رویی
        """
        # بر اساس چگالی مرتب می‌شوند (چگالی بیشتر در پایین)
        unique_liquids: Dict[str, float] = {}
        for l in self.layers:
            unique_liquids[l.liquid_id] = l.volume_ml

        # مرتب‌سازی بر اساس چگالی نزولی (بیشترین چگالی در ابتدا = کف ظرف)
        sorted_keys = sorted(
            unique_liquids.keys(),
            key=lambda k: LIQUID_DENSITIES[k]["density_g_ml"],
            reverse=True
        )

        stack = []
        for rank, k in enumerate(sorted_keys, start=1):
            info = LIQUID_DENSITIES[k]
            vol = unique_liquids[k]
            mass = round(vol * info["density_g_ml"], 1)
            position = "کف ظرف (لایه زیرین)" if rank == 1 else ("سطح ظرف (لایه رویی)" if rank == len(sorted_keys) else "لایه میانی")
            stack.append({
                "liquid_id": k,
                "name_fa": info["name_fa"],
                "density_g_ml": info["density_g_ml"],
                "volume_ml": vol,
                "mass_g": mass,
                "color_hex": info["color_hex"],
                "layer_position": position
            })

        return stack
