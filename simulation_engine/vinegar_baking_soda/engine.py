from typing import Dict, Any, List
from ..base import BaseExperimentEngine
from ..schema import (
    SimulationState,
    LabAction,
    StepResult,
    SimulationError,
    ErrorCategory
)
from .models import VinegarReactionState

TOOL_ALIASES = {
    "beaker_glass": "beaker_glass",
    "beaker": "beaker_glass",
    "beaker_1": "beaker_glass",
    "glass_cup": "beaker_glass",
    "bottle_vinegar": "bottle_vinegar",
    "vinegar_bottle": "bottle_vinegar",
    "vinegar": "bottle_vinegar",
    "jar_baking_soda": "jar_baking_soda",
    "baking_soda_jar": "jar_baking_soda",
    "baking_soda": "jar_baking_soda",
    "spatula": "spatula"
}

class VinegarBakingSodaEngine(BaseExperimentEngine):
    """
    موتور شبیه‌سازی واکنش شیمیایی سرکه و جوش‌شیرین و تولید گاز دی‌اکسید کربن.
    منبع: علوم تجربی پایه هشتم، فصل ۲ (تغییرهای شیمیایی در خدمت زندگی)، صفحات ۱۰-۱۴.
    معادله واکنش: CH3COOH + NaHCO3 -> CH3COONa + H2O + CO2 (g)
    """

    def __init__(self):
        super().__init__(experiment_id="vinegar-baking-soda-reaction", total_steps=4)
        self.reaction_physics = VinegarReactionState()

    def _create_initial_state(self) -> SimulationState:
        self.reaction_physics = VinegarReactionState()
        return SimulationState(
            experiment_id="vinegar-baking-soda-reaction",
            current_step=1,
            total_steps=4,
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
        # خودکارسازی حضور وسایلی که مستقیماً در کنش مشخص شده‌اند
        for item_id in [action.source_id, action.target_id]:
            if item_id and item_id not in self.state.workbench_tools:
                self.state.workbench_tools.append(item_id)

        # ۱. بررسی پیش‌بینی‌ها و خطاهای مفهومی دانش‌آموز
        params = action.parameters or {}
        predicted_gas = str(params.get("predicted_gas", "")).lower()
        if action.action_type in ["SUBMIT_PREDICTION", "PREDICT_GAS"] or predicted_gas:
            if predicted_gas in ["oxygen", "o2", "hydrogen", "h2", "اکسیژن", "هیدروژن"]:
                return StepResult(
                    success=False,
                    step_index=self.state.current_step,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_MISCONCEPTION_GAS_TYPE",
                        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
                        title="تشخیص اشتباه نوع گاز متصاعدشده",
                        description=f"گاز حاصل از واکنش «{predicted_gas}» نیست.",
                        scientific_rationale="واکنش اسید استیک و بی‌کربنات سدیم گاز دی‌اکسید کربن (CO2) آزاد می‌کند که چگال‌تر از هوا بوده و شعله را خاموش می‌کند.",
                        recommended_action="گاز خروجی را به عنوان کربن دی‌اکسید (CO2) ثبت کنید."
                    ),
                    state_snapshot=self.state.to_dict()
                )

        if params.get("predict_infinite_reaction") or params.get("infinite_soda") or params.get("more_soda_more_gas"):
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_LIMITING_REACTANT_OVEREATING",
                    category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
                    title="غفلت از مفهوم واکنش‌دهنده محدودکننده",
                    description="افزودن بی‌رویه جوش‌شیرین بدون وجود اسید سرکه گازی تولید نمی‌کند.",
                    scientific_rationale="با اتمام سرکه (ماده محدودکننده)، واکنش متوقف شده و جوش‌شیرین دست‌نخورده باقی می‌ماند.",
                    recommended_action="برای ادامه واکنش باید اسید سرکه به ظرف اضافه شود."
                ),
                state_snapshot=self.state.to_dict()
            )

        if params.get("is_boiling") or params.get("predicted_phenomenon") in ["boiling", "جوشیدن", "تبخیر"]:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_MISCONCEPTION_BOILING_VS_REACTION",
                    category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
                    title="اشتباه گرفتن جوشش شیمیایی با جوشیدن فیزیکی",
                    description="حباب‌های حاصل ناشی از تبخیر حرارتی مایع نیستند.",
                    scientific_rationale="خروج سریع مولکول‌های CO2 پدیده جوشش شیمیایی است، در حالی که دمای محلول در اثر واکنش اندکی افت می‌کند.",
                    recommended_action="پدیده را به عنوان تولید شیمیایی گاز ثبت نمایید."
                ),
                state_snapshot=self.state.to_dict()
            )

        if action.action_type in ["SELECT_BEAKER", "PLACE_BEAKER"]:
            return self._handle_place_beaker(action)

        if action.action_type in ["POUR_VINEGAR", "ADD_VINEGAR"]:
            return self._handle_pour_vinegar(action)

        if action.action_type in ["ADD_BAKING_SODA", "ADD_SODA", "MIX_SODA"]:
            return self._handle_add_baking_soda(action)

        if action.action_type in ["OBSERVE_REACTION", "TRIGGER_REACTION", "MIX"]:
            return self._handle_observe_reaction(action)

        if action.action_type == "SET_PARAMETERS":
            params = action.parameters or {}
            if "vinegar_volume_ml" in params:
                self.reaction_physics.vinegar_volume_ml = float(params["vinegar_volume_ml"])
            if "baking_soda_mass_g" in params:
                self.reaction_physics.baking_soda_mass_g = float(params["baking_soda_mass_g"])
            
            calc = self.reaction_physics.calculate_stoichiometry()
            return StepResult(
                success=True,
                step_index=self.state.current_step,
                is_step_completed=False,
                observations=[f"پارامترهای واکنش تنظیم شد: سرکه {self.reaction_physics.vinegar_volume_ml}ml و جوش‌شیرین {self.reaction_physics.baking_soda_mass_g}g."],
                measurements=calc,
                state_snapshot=self.state.to_dict()
            )

        return StepResult(
            success=False,
            step_index=self.state.current_step,
            is_step_completed=False,
            error=SimulationError(
                code="ERR_UNSUPPORTED_VINEGAR_ACTION",
                category=ErrorCategory.UNSUPPORTED_COMBINATION,
                title="عملیات واکنش نامعتبر است",
                description=f"عملیات «{action.action_type}» در این آزمایش تعریف نشده است.",
                scientific_rationale="مراحل آزمایش شامل استقرار لیوان، ریختن سرکه، افزودن جوش‌شیرین و مشاهده پدیده جوشش است.",
                recommended_action="یکی از مراحل مجاز آزمایش را انجام دهید."
            ),
            state_snapshot=self.state.to_dict()
        )

    def _handle_place_beaker(self, action: LabAction) -> StepResult:
        """گام ۱: استقرار لیوان آزمایشگاهی روی میز کار"""
        if "beaker_glass" not in self.state.workbench_tools:
            self.state.workbench_tools.append("beaker_glass")

        obs = "لیوان آزمایشگاهی شفاف روی میز کار مستقر شد و آماده دریافت مواد است."
        is_step_completed = False
        if self.state.current_step == 1:
            is_step_completed = True
            self.state.current_step = 2

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={"container_ready": True},
            state_snapshot=self.state.to_dict()
        )

    def _handle_pour_vinegar(self, action: LabAction) -> StepResult:
        """گام ۲: ریختن سرکه داخل لیوان"""
        if not self._has_tool("beaker_glass"):
            return self._make_precondition_error("beaker_glass", "لیوان آزمایشگاهی (بشر)")
        if not self._has_tool("bottle_vinegar"):
            return self._make_precondition_error("bottle_vinegar", "بطری سرکه")

        # خواندن پارامتر حجم در صورت ارسال
        if action.parameters and "volume_ml" in action.parameters:
            self.reaction_physics.vinegar_volume_ml = float(action.parameters["volume_ml"])

        self.reaction_physics.is_vinegar_added = True
        vol = self.reaction_physics.vinegar_volume_ml
        obs = f"مقدار {vol} میلی‌لیتر سرکه حاوی اسید استیک به لیوان آزمایشگاهی اضافه شد."

        is_step_completed = False
        if self.state.current_step <= 2:
            is_step_completed = True
            self.state.current_step = 3

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={"vinegar_volume_ml": vol, "pH_estimated": 2.8},
            state_snapshot=self.state.to_dict()
        )

    def _handle_add_baking_soda(self, action: LabAction) -> StepResult:
        """گام ۳: افزودن جوش‌شیرین به سرکه داخل لیوان"""
        if not self.reaction_physics.is_vinegar_added:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_SODA_BEFORE_VINEGAR",
                    category=ErrorCategory.ORDER_VIOLATION,
                    title="ابتدا باید سرکه درون ظرف باشد",
                    description="افزودن پودر جوش‌شیرین به ظرف خالی واکنشی ایجاد نمی‌کند.",
                    scientific_rationale="واکنش اسید و باز نیازمند فاز مایع و حضور یون‌های هیدرونیوم اسید استیک است.",
                    recommended_action="ابتدا سرکه را داخل لیوان بریزید و سپس جوش‌شیرین را بیفزایید."
                ),
                state_snapshot=self.state.to_dict()
            )

        if not self._has_tool("jar_baking_soda"):
            return self._make_precondition_error("jar_baking_soda", "ظرف جوش‌شیرین")

        if action.parameters and "mass_g" in action.parameters:
            self.reaction_physics.baking_soda_mass_g = float(action.parameters["mass_g"])

        self.reaction_physics.is_soda_added = True
        mass = self.reaction_physics.baking_soda_mass_g
        obs = f"مقدار {mass} گرم جوش‌شیرین (سدیم هیدروژن‌کربنات) به سرکه اضافه شد. فوراً تشکیل حباب‌ها و جوشش گاز آغاز گردید."

        is_step_completed = False
        if self.state.current_step <= 3:
            is_step_completed = True
            self.state.current_step = 4

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={"baking_soda_mass_g": mass, "gas_emission_started": True},
            state_snapshot=self.state.to_dict()
        )

    def _handle_observe_reaction(self, action: LabAction) -> StepResult:
        """گام ۴: مشاهده و ثبت تحلیل نهایی واکنش شیمیایی و استوکیومتری"""
        if not self.reaction_physics.is_vinegar_added or not self.reaction_physics.is_soda_added:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_REACTION_PRECONDITIONS_INCOMPLETE",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="مواد واکنش هنوز ترکیب نشده‌اند",
                    description="برای مشاهده واکنش باید هر دو ماده سرکه و جوش‌شیرین در لیوان مخلوط شده باشند.",
                    scientific_rationale="واکنش تولید گاز نیازمند اختلاط مستقیم اسید استیک و بی‌کربنات است.",
                    recommended_action="سرکه و جوش‌شیرین را به ظرف اضافه کنید."
                ),
                state_snapshot=self.state.to_dict()
            )

        calc = self.reaction_physics.calculate_stoichiometry()
        self.reaction_physics.is_reaction_triggered = True
        self.reaction_physics.co2_gas_volume_ml = calc["co2_volume_ml"]
        self.reaction_physics.foam_height_percent = calc["foam_height_percent"]
        self.state.is_completed = True

        obs = (
            f"واکنش سریع اسید و باز رخ داد: {calc['co2_volume_ml']} میلی‌لیتر گاز کربن دی‌اکسید (CO2) آزاد شد "
            f"و کف سفیدرنگی تا {calc['foam_height_percent']}٪ ظرف بالا آمد. "
            f"ماده محدودکننده در این مقادیر «{calc['limiting_reactant']}» بود و دمای محلول {calc['temperature_drop_celsius']}°C کاهش یافت."
        )

        return StepResult(
            success=True,
            step_index=4,
            is_step_completed=True,
            observations=[obs],
            measurements={
                "reaction_equation": "CH3COOH + NaHCO3 -> CH3COONa + H2O + CO2",
                "gas_produced": "کربن دی‌اکسید (CO2)",
                "co2_volume_ml": calc["co2_volume_ml"],
                "foam_height_percent": calc["foam_height_percent"],
                "limiting_reactant": calc["limiting_reactant"],
                "temperature_drop_c": calc["temperature_drop_celsius"]
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
                scientific_rationale="انجام واکنش مستلزم حضور ابزار یا ماده در محیط آزمایشگاه است.",
                recommended_action=f"ابزار «{tool_name}» را از قفسه انتخاب نمایید."
            ),
            state_snapshot=self.state.to_dict()
        )
