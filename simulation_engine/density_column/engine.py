from typing import Dict, Any, List
from ..base import BaseExperimentEngine
from ..schema import (
    SimulationState,
    LabAction,
    StepResult,
    SimulationError,
    ErrorCategory
)
from .models import DensityColumnState, LIQUID_DENSITIES

TOOL_ALIASES = {
    "measuring_cylinder": "measuring_cylinder",
    "cylinder": "measuring_cylinder",
    "graduated_cylinder": "measuring_cylinder",
    "flask_honey": "flask_honey",
    "honey_jar": "flask_honey",
    "honey": "flask_honey",
    "flask_water": "flask_water",
    "water_beaker": "flask_water",
    "water": "flask_water",
    "flask_oil": "flask_oil",
    "oil_bottle": "flask_oil",
    "oil": "flask_oil"
}

class LiquidDensityColumnEngine(BaseExperimentEngine):
    """
    موتور شبیه‌سازی ستون چگالی مایعات (عسل، آب و روغن) و بررسی چگالی و امتزاج‌پذیری.
    منبع: علوم تجربی پایه هفتم، فصل ۲ (اندازه‌گیری در علوم و ابزارهای آن، ص ۱۴-۱۸).
    """

    def __init__(self):
        super().__init__(experiment_id="liquid-density-column", total_steps=5)
        self.column_physics = DensityColumnState()

    def _create_initial_state(self) -> SimulationState:
        self.column_physics = DensityColumnState()
        return SimulationState(
            experiment_id="liquid-density-column",
            current_step=1,
            total_steps=5,
            workbench_tools=[],
            active_solutions={},
            recorded_observations=[],
            action_history=[],
            is_completed=False
        )

    def _has_tool(self, tool_id: str) -> bool:
        norm_target = tool_id.replace("-", "_")
        canon_target = TOOL_ALIASES.get(norm_target, norm_target)
        for t in self.state.workbench_tools:
            norm_t = t.replace("-", "_")
            canon_t = TOOL_ALIASES.get(norm_t, norm_t)
            if norm_t == norm_target or canon_t == canon_target:
                return True
        return False

    def _process_scientific_action(self, action: LabAction) -> StepResult:
        # خودکارسازی وسایل مرجع در کنش
        for item_id in [action.source_id, action.target_id]:
            if item_id and item_id not in self.state.workbench_tools:
                self.state.workbench_tools.append(item_id)

        # ۱. بررسی فرضیه‌سازی و خطاهای مفهومی چگالی مایعات دانش‌آموز
        params = action.parameters or {}
        prediction = str(params.get("prediction", "")).lower()
        if action.action_type in ["SUBMIT_PREDICTION", "PREDICT_LAYER"] or prediction:
            if prediction in ["volume_determines_layer", "more_volume_sinks", "حجم_بیشتر_ته‌نشین"]:
                return StepResult(
                    success=False,
                    step_index=self.state.current_step,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_DENSITY_VOLUME_CONFUSION",
                        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
                        title="خلط مفهوم حجم مایع با چگالی",
                        description="افزایش حجم یک مایع باعث ته‌نشینی آن در زیر مایع چگال‌تر نمی‌شود.",
                        scientific_rationale="چگالی یک خاصیت شدتی است (ρ = m/V). جایگاه مایعات در ستون منحصراً به چگالی وابسته است، نه به مقدار یا حجم کل مایع.",
                        recommended_action="قرارگیری لایه‌ها بر حسب چگالی (نه حجم) را تأیید کنید."
                    ),
                    state_snapshot=self.state.to_dict()
                )

            if prediction in ["oil_bottom", "viscosity_sinks", "روغن_کف_می‌رود"] or params.get("predict_oil") == "bottom":
                return StepResult(
                    success=False,
                    step_index=self.state.current_step,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_MISCONCEPTION_VISCOSITY_DENSITY",
                        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
                        title="اشتباه گرفتن گرانروی (غلظت ظاهری) با چگالی",
                        description="روغن با وجود غلیظ‌تر به نظر رسیدن، چگالی کمتری نسبت به آب دارد و شناور می‌ماند.",
                        scientific_rationale="گرانروی اصطکاک داخلی مایع است و نشان‌دهنده جرم واحد حجم نیست. چگالی روغن حدود ۰.۹۱ و کمتر از آب (۱.۰۰) است.",
                        recommended_action="شناوری روغن بر روی آب به دلیل چگالی کمتر را ثبت نمایید."
                    ),
                    state_snapshot=self.state.to_dict()
                )

            if prediction in ["all_liquids_layer", "miscible_liquids_layer", "همه_مایعات_لایه_می‌شوند"] or str(params.get("liquid", "")).lower() in ["alcohol", "الکل"]:
                return StepResult(
                    success=False,
                    step_index=self.state.current_step,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_MISCONCEPTION_MISCIBILITY_IGNORED",
                        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
                        title="غفلت از شرط عدم امتزاج مایعات",
                        description="تفاوت چگالی به تنهایی کافی نیست؛ مایعات باید در یکدیگر حل نشوند.",
                        scientific_rationale="اگر دو مایع با چگالی متفاوت در هم حل شوند (مانند آب و الکل)، ستون لایه‌ای تشکیل نمی‌شود و یک فاز مخلوط حاصل می‌گردد.",
                        recommended_action="شرط امتزاج‌ناپذیری مایعات را برای تشکیل لایه‌های پایدار لحاظ کنید."
                    ),
                    state_snapshot=self.state.to_dict()
                )

        if action.action_type in ["SELECT_CYLINDER", "PLACE_CYLINDER", "PREPARE_CONTAINER"]:
            return self._handle_place_cylinder(action)

        if action.action_type in ["POUR_HONEY", "ADD_HONEY"]:
            return self._handle_pour_liquid(action, "honey", "عسل طبیعی", 2)

        if action.action_type in ["POUR_WATER", "ADD_WATER"]:
            return self._handle_pour_liquid(action, "water", "آب مقطر", 3)

        if action.action_type in ["POUR_OIL", "ADD_OIL"]:
            return self._handle_pour_liquid(action, "oil", "روغن مایع", 4)

        if action.action_type in ["OBSERVE_LAYERS", "ANALYZE_DENSITY"]:
            return self._handle_observe_layers(action)

        if action.action_type == "SET_PARAMETERS":
            params = action.parameters or {}
            # امکان تنظیم حجم مایعات
            if "honey_volume" in params:
                self.column_physics.add_liquid("honey", float(params["honey_volume"]))
            if "water_volume" in params:
                self.column_physics.add_liquid("water", float(params["water_volume"]))
            if "oil_volume" in params:
                self.column_physics.add_liquid("oil", float(params["oil_volume"]))

            stack = self.column_physics.calculate_equilibrium_stack()
            return StepResult(
                success=True,
                step_index=self.state.current_step,
                is_step_completed=False,
                observations=["پارامترهای حجم و چینش مایعات در ستون چگالی محاسبه شد."],
                measurements={"layers_stack": stack},
                state_snapshot=self.state.to_dict()
            )

        return StepResult(
            success=False,
            step_index=self.state.current_step,
            is_step_completed=False,
            error=SimulationError(
                code="ERR_UNSUPPORTED_DENSITY_ACTION",
                category=ErrorCategory.UNSUPPORTED_COMBINATION,
                title="عملیات نامعتبر در ستون چگالی",
                description=f"عملیات «{action.action_type}» برای ستون چگالی تعریف نشده است.",
                scientific_rationale="آزمایش شامل استقرار استوانه، افزودن عسل، آب و روغن به ظرف و مشاهده تفکیک فازهاست.",
                recommended_action="یکی از مراحل مجاز آزمایش را انجام دهید."
            ),
            state_snapshot=self.state.to_dict()
        )

    def _handle_place_cylinder(self, action: LabAction) -> StepResult:
        """گام ۱: استقرار استوانه مدرج شفاف روی میز کار"""
        if "measuring_cylinder" not in self.state.workbench_tools:
            self.state.workbench_tools.append("measuring_cylinder")

        self.column_physics.cylinder_ready = True
        obs = "استوانه مدرج شفاف و تمیز روی سطح آزمایشگاه قرار گرفت."

        is_step_completed = False
        if self.state.current_step == 1:
            is_step_completed = True
            self.state.current_step = 2

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={"cylinder_ready": True},
            state_snapshot=self.state.to_dict()
        )

    def _handle_pour_liquid(self, action: LabAction, liquid_id: str, name_fa: str, target_step: int) -> StepResult:
        """ریختن هر یک از مایعات به داخل ظرف"""
        if not self.column_physics.cylinder_ready:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_POUR_WITHOUT_CYLINDER",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="استوانه مدرج روی میز نیست",
                    description="قبل از ریختن مایعات باید ظرف شفاف روی میز مستقر شده باشد.",
                    scientific_rationale="مایعات باید درون یک محفظه مدرج شفاف ریخته شوند.",
                    recommended_action="ابتدا استوانه مدرج را روی میز کار قرار دهید."
                ),
                state_snapshot=self.state.to_dict()
            )

        flask_key = f"flask_{liquid_id}"
        if not self._has_tool(flask_key):
            return self._make_precondition_error(flask_key, f"ظرف {name_fa}")

        vol = 30.0
        if action.parameters and "volume_ml" in action.parameters:
            vol = float(action.parameters["volume_ml"])

        self.column_physics.add_liquid(liquid_id, vol)
        density = LIQUID_DENSITIES[liquid_id]["density_g_ml"]
        mass = round(vol * density, 1)

        obs = f"مقدار {vol} میلی‌لیتر {name_fa} (با چگالی {density} g/cm³ و جرم {mass} گرم) به استوانه افزوده شد."

        is_step_completed = False
        if self.state.current_step <= target_step:
            is_step_completed = True
            self.state.current_step = target_step + 1

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={"liquid_added": liquid_id, "volume_ml": vol, "density": density, "mass_g": mass},
            state_snapshot=self.state.to_dict()
        )

    def _handle_observe_layers(self, action: LabAction) -> StepResult:
        """گام ۵: مشاهده تشکیل لایه‌های تعادلی بر حسب چگالی و عدم امتزاج"""
        if len(self.column_physics.layers) < 2:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_INSUFFICIENT_LIQUIDS_FOR_LAYERS",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="تعداد مایعات برای تشکیل ستون کافی نیست",
                    description="برای مشاهده لایه‌بندی چگالی حداقل باید دو یا سه مایع به ظرف اضافه شوند.",
                    scientific_rationale="ستون چگالی از تقابل چگالی مایعات گوناگون پدید می‌آید.",
                    recommended_action="عسل، آب و روغن را به استوانه اضافه کنید."
                ),
                state_snapshot=self.state.to_dict()
            )

        stack = self.column_physics.calculate_equilibrium_stack()
        self.state.is_completed = True

        obs = (
            "به دلیل تفاوت چگالی و عدم انحلال‌پذیری (امتزاج‌ناپذیری مایعات با یکدیگر)، ۳ فاز کاملاً تفکیک‌شده پدیدار گشت: "
            "عسل با بیشترین چگالی (۱.۴۲ g/cm³) در کف ظرف ته‌نشین شد، آب با چگالی میانی (۱.۰۰ g/cm³) در وسط قرار گرفت "
            "و روغن با کمترین چگالی (۰.۹۱ g/cm³) روی سطح آب شناور ماند. "
            "(نکته علمی: چگالی کمتر علت شناوری است، اما امتزاج‌ناپذیری شرط اساسی مخلوط نشدن فازهاست)."
        )

        return StepResult(
            success=True,
            step_index=5,
            is_step_completed=True,
            observations=[obs],
            measurements={
                "layers_equilibrium_order": stack,
                "layer_count": len(stack),
                "is_stable": True
            },
            state_snapshot=self.state.to_dict(),
            is_terminal=True
        )

    def _make_precondition_error(self, tool_id: str, tool_name: str) -> StepResult:
        return StepResult(
            success=False,
            step_index=self.state.current_step,
            is_step_completed=False,
            error=SimulationError(
                code=f"ERR_MISSING_{tool_id.upper()}",
                category=ErrorCategory.MISSING_PRECONDITION,
                title=f"وسیله «{tool_name}» روی میز کار نیست",
                description=f"برای اجرای این مرحله، ابتدا باید «{tool_name}» را به میز کار اضافه کنید.",
                scientific_rationale="انجام اندازه‌گیری چگالی نیازمند استقرار ظروف مایعات است.",
                recommended_action=f"ابزار «{tool_name}» را از قفسه انتخاب نمایید."
            ),
            state_snapshot=self.state.to_dict()
        )
