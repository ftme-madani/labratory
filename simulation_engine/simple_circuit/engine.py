from typing import Dict, Any, List
from ..base import BaseExperimentEngine
from ..schema import (
    SimulationState,
    LabAction,
    StepResult,
    SimulationError,
    ErrorCategory
)
from .models import CircuitPhysicsState

CIRCUIT_TOOL_ALIASES = {
    "battery_pack": "battery_cell",
    "battery_cell": "battery_pack",
    "battery": "battery_cell",
    "switch": "switch_key",
    "switch_key": "switch",
    "connecting_wires": "wires",
    "wires": "connecting_wires",
}

class SimpleCircuitSimulationEngine(BaseExperimentEngine):
    """
    موتور شبیه‌سازی مدار الکتریکی ساده و قانون اهم.
    منبع: علوم تجربی پایه نهم، فصل ۹ (الکتریسیته)، صفحه ۹۸.
    قواعد فیزیکی: قانون اهم (V = I * R)، توان الکتریکی، تشخیص اتصال کوتاه و مدار باز.
    """

    def __init__(self):
        super().__init__(experiment_id="exp-simple-circuit", total_steps=3)
        self.circuit_physics = CircuitPhysicsState()

    def _create_initial_state(self) -> SimulationState:
        self.circuit_physics = CircuitPhysicsState()
        return SimulationState(
            experiment_id="exp-simple-circuit",
            current_step=1,
            total_steps=3,
            workbench_tools=[],
            active_solutions={},
            recorded_observations=[],
            action_history=[],
            is_completed=False
        )

    def _process_scientific_action(self, action: LabAction) -> StepResult:
        params = action.parameters or {}
        prediction = str(params.get("prediction", "")).lower()
        if action.action_type in ["SUBMIT_PREDICTION", "PREDICT_OHM"] or prediction:
            if prediction in ["higher_voltage_less_current", "inverse", "ولتاژ_بیشتر_جریان_کمتر"] or params.get("predict_current") == "decreases_with_voltage":
                return StepResult(
                    success=False,
                    step_index=self.state.current_step,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_VOLTAGE_CURRENT_MISCONCEPTION",
                        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
                        title="تصور نادرست رابطه ولتاژ و جریان",
                        description="طبق قانون اهم با افزایش ولتاژ، شدت جریان مدار افزایش می‌یابد.",
                        scientific_rationale="رابطه قانون اهم I = V / R است. در یک مقاومت ثابت، شدت جریان مستقیماً با ولتاژ دو سر آن متناسب است و با دو برابر شدن ولتاژ، جریان دو برابر می‌شود.",
                        recommended_action="رابطه مستقیم ولتاژ و شدت جریان را ثبت کنید."
                    ),
                    state_snapshot=self.state.to_dict()
                )

        if action.action_type in ["CONNECT", "CONNECT_COMPONENTS", "WIRE_CIRCUIT"]:
            return self._handle_wiring(action)

        if action.action_type in ["SWITCH_TOGGLE", "CLOSE_SWITCH"]:
            return self._handle_switch(action)

        if action.action_type in ["MEASURE_CURRENT", "MEASURE_OHM"]:
            return self._handle_measurement(action)

        return StepResult(
            success=False,
            step_index=self.state.current_step,
            is_step_completed=False,
            error=SimulationError(
                code="ERR_UNSUPPORTED_CIRCUIT_ACTION",
                category=ErrorCategory.UNSUPPORTED_COMBINATION,
                title="عملیات الکتریکی نامعتبر",
                description=f"عملیات «{action.action_type}» در این مدار تعریف نشده است.",
                scientific_rationale="در مدار الکتریکی کنش‌ها شامل سیم‌کشی، تغییر حالت کلید و اندازه‌گیری جریان با آمپرمتر هستند.",
                recommended_action="اجزای مدار را با سیم رابط متصل کنید."
            ),
            state_snapshot=self.state.to_dict()
        )

    def _has_tool(self, tool_id: str) -> bool:
        normalized_tools = {t.replace("-", "_") for t in self.state.workbench_tools}
        target = tool_id.replace("-", "_")
        if target in normalized_tools:
            return True
        alias = CIRCUIT_TOOL_ALIASES.get(target)
        if alias and alias.replace("-", "_") in normalized_tools:
            return True
        return False

    def _handle_wiring(self, action: LabAction) -> StepResult:
        """گام ۱: بستن اجزای مدار در یک حلقه رسانا"""
        if not self._has_tool("battery_cell"):
            return self._make_precondition_error("battery_cell", "باتری ۱.۵ ولت")
        if not self._has_tool("light_bulb"):
            # اگر سعی کند بدون لامپ سیم‌ها را ببندد
            self.circuit_physics.has_bulb = False
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_CIRCUIT_WITHOUT_LOAD",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="مدار فاقد مقاومت مصرف‌کننده است",
                    description="بستن سیم‌های باتری به یکدیگر بدون حضور لامپ باعث خطر اتصال کوتاه می‌شود.",
                    scientific_rationale="طبق قانون اهم (I = V/R)، اگر مقاومت مدار صفر باشد جریان به سمت بی‌نهایت میل کرده و سیم‌ها داغ می‌شوند.",
                    recommended_action="لامپ کوچک ۳ ولتی را از قفسه به مدار اضافه کنید."
                ),
                state_snapshot=self.state.to_dict()
            )

        if not self._has_tool("switch_key"):
            return self._make_precondition_error("switch_key", "کلید قطع و وصل")
        if not self._has_tool("connecting_wires"):
            return self._make_precondition_error("connecting_wires", "سیم‌های رابط")

        self.circuit_physics.has_bulb = True
        self.circuit_physics.is_loop_connected = True
        self.circuit_physics.is_switch_closed = False

        obs = (
            "باتری ۱.۵ ولتی، کلید تیغه‌ای (در حالت باز) و لامپ با سیم‌های رابط در یک حلقه متوالی بسته شدند. "
            "به دلیل باز بودن کلید، جریان الکتریکی صفر است (I=0 A) و لامپ خاموش می‌ماند."
        )

        is_step_completed = False
        if self.state.current_step == 1:
            is_step_completed = True
            self.state.current_step = 2

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={
                "voltage_volts": self.circuit_physics.battery_voltage_volts,
                "circuit_status": "مدار باز (کلید خاموش)",
                "current_amperes": 0.0,
                "bulb_lit": False
            },
            state_snapshot=self.state.to_dict()
        )

    def _handle_switch(self, action: LabAction) -> StepResult:
        """گام ۲: بستن کلید و مشاهده برقراری جریان و روشنایی لامپ"""
        if not self.circuit_physics.is_loop_connected:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_SWITCH_BEFORE_WIRING",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="مدار هنوز سیم‌کشی نشده است",
                    description="پیش از بستن کلید، باید حلقه سیم‌کشی بین باتری و لامپ برقرار باشد.",
                    scientific_rationale="کلید تنها زمانی کارایی دارد که در مسیر یک مدار متوالی قرار گرفته باشد.",
                    recommended_action="ابتدا اجزای مدار را با سیم رابط متصل نمایید."
                ),
                state_snapshot=self.state.to_dict()
            )

        # بستن کلید
        self.circuit_physics.is_switch_closed = True
        current = self.circuit_physics.current_amperes
        power = self.circuit_physics.bulb_power_watts
        is_lit = self.circuit_physics.is_bulb_lit

        obs = (
            f"کلید مدار بسته شد. میدان الکتریکی در سراسر حلقه رسانا برقرار شد و شدت جریان {current} آمپر از مدار گذشت. "
            f"توان مصرفی لامپ به {power} وات رسید و رشته تنگستن داغ شده و نور زرد شفاف ساطع کرد."
        )

        is_step_completed = False
        if self.state.current_step == 2:
            is_step_completed = True
            self.state.current_step = 3

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={
                "switch_status": "بسته [ON]",
                "current_amperes": current,
                "bulb_power_watts": power,
                "bulb_lit": is_lit,
                "bulb_resistance_ohms": self.circuit_physics.bulb_resistance_ohms
            },
            state_snapshot=self.state.to_dict()
        )

    def _handle_measurement(self, action: LabAction) -> StepResult:
        """گام ۳: قرار دادن آمپرمتر در مدار و محاسبه قانون اهم (R = V / I)"""
        if not self._has_tool("ammeter"):
            return self._make_precondition_error("ammeter", "آمپرمتر دیجیتال")

        if not self.circuit_physics.is_switch_closed:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_MEASURE_ON_OPEN_CIRCUIT",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="کلید مدار باز است",
                    description="برای اندازه‌گیری جریان عبوری، باید کلید مدار در وضعیت بسته باشد.",
                    scientific_rationale="در مدار باز جریانی عبور نمی‌کند و آمپرمتر عدد صفر را نشان خواهد داد.",
                    recommended_action="ابتدا کلید مدار را ببندید."
                ),
                state_snapshot=self.state.to_dict()
            )

        self.circuit_physics.has_ammeter = True
        current = self.circuit_physics.current_amperes
        v = self.circuit_physics.battery_voltage_volts
        calculated_r = round(v / current, 1)
        self.state.is_completed = True

        obs = (
            f"آمپرمتر به صورت متوالی در مدار قرار گرفت و شدت جریان دقیق I={current} آمپر را ثبت کرد. "
            f"طبق رابطه قانون اهم R = V / I: مقدار مقاومت لامپ برابر {calculated_r} اهم به دست آمد "
            f"که با مقاومت اسمی لامپ (۱۰ اهم) تطابق دارد."
        )

        return StepResult(
            success=True,
            step_index=3,
            is_step_completed=True,
            observations=[obs],
            measurements={
                "voltage_volts": v,
                "measured_current_amperes": current,
                "calculated_resistance_ohms": calculated_r,
                "law_verified": "قانون اهم V = I * R اثبات شد"
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
                title=f"قطعه «{tool_name}» در مدار قرار ندارد",
                description=f"برای تکمیل مدار، باید قطعه «{tool_name}» را به میز اضافه کنید.",
                scientific_rationale="مدار متوالی نیازمند اتصال تمامی اجزای تشکیل‌دهنده است.",
                recommended_action=f"«{tool_name}» را از قفسه انتخاب نمایید."
            ),
            state_snapshot=self.state.to_dict()
        )
