from typing import Dict, Any, List
from ..base import BaseExperimentEngine
from ..schema import (
    SimulationState,
    LabAction,
    StepResult,
    SimulationError,
    ErrorCategory
)
from .models import PendulumPhysicsState

TOOL_ALIASES = {
    "pendulum_stand": "pendulum_stand",
    "stand": "pendulum_stand",
    "pendulum_string": "pendulum_string",
    "string": "pendulum_string",
    "pendulum_bob": "pendulum_bob",
    "bob": "pendulum_bob",
    "pendulum_stopwatch": "pendulum_stopwatch",
    "stopwatch": "pendulum_stopwatch",
    "timer": "pendulum_stopwatch"
}

class SimplePendulumEngine(BaseExperimentEngine):
    """
    موتور شبیه‌سازی حرکت آونگ ساده، محاسبه دوره تناوب T = 2*pi*sqrt(L/g) و بررسی اثر طول نخ و جرم وزنه.
    منبع: علوم تجربی پایه نهم، فصل ۴ (حرکت چیست؟).
    """

    def __init__(self):
        super().__init__(experiment_id="simple-pendulum-motion", total_steps=4)
        self.pendulum_physics = PendulumPhysicsState()

    def _create_initial_state(self) -> SimulationState:
        self.pendulum_physics = PendulumPhysicsState()
        return SimulationState(
            experiment_id="simple-pendulum-motion",
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
        # خودکارسازی وسایل مرجع در کنش
        for item_id in [action.source_id, action.target_id]:
            if item_id and item_id not in self.state.workbench_tools:
                self.state.workbench_tools.append(item_id)

        # بررسی فرضیه‌سازی و پیش‌بینی‌های نادرست فیزیکی
        params = action.parameters or {}
        predict_effect = str(params.get("predicted_effect", "")).lower()
        prediction = str(params.get("prediction", "")).lower()
        if action.action_type in ["SUBMIT_PREDICTION", "CHECK_HYPOTHESIS"] or predict_effect or prediction:
            if predict_effect in ["mass_increases_period", "heavy_is_faster", "mass_dependent"] or prediction in ["mass_dependent", "جرم_موثر", "سنگین_تندتر"]:
                return StepResult(
                    success=False,
                    step_index=self.state.current_step,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_PENDULUM_MASS_DEPENDENCE",
                        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
                        title="تصور نادرست وابستگی دوره تناوب به جرم وزنه",
                        description="جرم وزنه بر زمان تناوب آونگ ساده اثری ندارد.",
                        scientific_rationale="طبق فرمول T = 2π√(L/g)، دوره تناوب آونگ ساده منحصراً به طول نخ و شتاب گرانش بستگی دارد و در زوایای کوچک از جرم وزنه مستقل است.",
                        recommended_action="استقلال دوره تناوب از جرم وزنه را به عنوان نتیجه فیزیکی ثبت نمایید."
                    ),
                    state_snapshot=self.state.to_dict()
                )

            if predict_effect in ["longer_is_faster", "length_inverse"] or prediction in ["longer_is_faster", "نخ_بلندتر_تندتر"]:
                return StepResult(
                    success=False,
                    step_index=self.state.current_step,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_PENDULUM_LENGTH_INVERSE",
                        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
                        title="اشتباه در رابطه طول نخ با دوره تناوب",
                        description="افزایش طول نخ زمان نوسان را بیشتر (کندتر) می‌کند نه تندتر.",
                        scientific_rationale="رابطه طول نخ و زمان تناوب مستقیم و رادیکالی است (T ∝ √L). با افزایش طول، زمان یک نوسان طولانی‌تر می‌شود.",
                        recommended_action="رابطه مستقیم طول نخ با زمان تناوب را تأیید کنید."
                    ),
                    state_snapshot=self.state.to_dict()
                )

        if action.action_type in ["ATTACH_STRING", "SET_LENGTH", "SELECT_STRING", "SET_PARAMETERS"]:
            params = action.parameters or {}
            if "string_length_m" in params:
                self.pendulum_physics.string_length_m = float(params["string_length_m"])
            elif "length_m" in params:
                self.pendulum_physics.string_length_m = float(params["length_m"])
            if "bob_mass_kg" in params:
                self.pendulum_physics.bob_mass_kg = float(params["bob_mass_kg"])
            elif "mass_g" in params:
                self.pendulum_physics.bob_mass_kg = float(params["mass_g"]) / 1000.0
            if "oscillations_count" in params:
                self.pendulum_physics.oscillations_count = int(params["oscillations_count"])
            elif "oscillations" in params:
                self.pendulum_physics.oscillations_count = int(params["oscillations"])

            self.pendulum_physics.is_string_attached = True
            data = self.pendulum_physics.calculate_motion_data()
            is_step_completed = False
            if self.state.current_step == 1:
                is_step_completed = True
                self.state.current_step = 2

            return StepResult(
                success=True,
                step_index=self.state.current_step,
                is_step_completed=is_step_completed,
                observations=[f"نخ آونگ به طول {self.pendulum_physics.string_length_m} متر و وزنه با جرم {self.pendulum_physics.bob_mass_kg * 1000} گرم تنظیم شد."],
                measurements=data,
                state_snapshot=self.state.to_dict()
            )

        if action.action_type in ["ATTACH_BOB", "CONNECT_BOB", "SELECT_BOB"]:
            return self._handle_attach_bob(action)

        if action.action_type in ["DEFLECT_BOB", "DISPLACE_BOB", "SET_ANGLE"]:
            return self._handle_deflect_bob(action)

        if action.action_type in ["START_OSCILLATION", "START_TIMER", "MEASURE_PERIOD", "RELEASE_AND_MEASURE"]:
            return self._handle_oscillate_and_measure(action)

        return StepResult(
            success=False,
            step_index=self.state.current_step,
            is_step_completed=False,
            error=SimulationError(
                code="ERR_UNSUPPORTED_PENDULUM_ACTION",
                category=ErrorCategory.UNSUPPORTED_COMBINATION,
                title="عملیات نامعتبر در آزمایش آونگ",
                description=f"عملیات «{action.action_type}» برای آونگ ساده تعریف نشده است.",
                scientific_rationale="آزمایش آونگ شامل تنظیم طول نخ، اتصال وزنه، انحراف با زاویه کوچک و ثبت زمان نوسان است.",
                recommended_action="یکی از مراحل آونگ را انجام دهید."
            ),
            state_snapshot=self.state.to_dict()
        )

    def _handle_attach_string(self, action: LabAction) -> StepResult:
        """گام ۱: انتخاب طول نخ و اتصال آن به پایه نگهدارنده"""
        if not self._has_tool("pendulum_stand"):
            return self._make_precondition_error("pendulum_stand", "پایه نگهدارنده و گیره")
        if not self._has_tool("pendulum_string"):
            return self._make_precondition_error("pendulum_string", "نخ آزمایشگاهی")

        if action.parameters and "length_m" in action.parameters:
            self.pendulum_physics.string_length_m = float(action.parameters["length_m"])

        self.pendulum_physics.is_string_attached = True
        length = self.pendulum_physics.string_length_m
        obs = f"نخ آزمایشگاهی به طول {length} متر به گیره پایه نگهدارنده محکم متصل شد."

        is_step_completed = False
        if self.state.current_step == 1:
            is_step_completed = True
            self.state.current_step = 2

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={"string_length_m": length},
            state_snapshot=self.state.to_dict()
        )

    def _handle_attach_bob(self, action: LabAction) -> StepResult:
        """گام ۲: اتصال وزنه به انتهای آزاد نخ"""
        if not self.pendulum_physics.is_string_attached:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_BOB_BEFORE_STRING",
                    category=ErrorCategory.ORDER_VIOLATION,
                    title="ابتدا باید نخ به پایه متصل شود",
                    description="نمی‌توان وزنه را بدون وجود نخ به پایه آویزان کرد.",
                    scientific_rationale="آونگ ساده از یک نخ سبک غیرقابل کشش و یک وزنه معلق تشکیل می‌شود.",
                    recommended_action="ابتدا نخ را به پایه متصل کنید و سپس وزنه را به انتهای آن ببندید."
                ),
                state_snapshot=self.state.to_dict()
            )

        if not self._has_tool("pendulum_bob"):
            return self._make_precondition_error("pendulum_bob", "وزنه فلزی (گلوله آونگ)")

        if action.parameters and "mass_kg" in action.parameters:
            self.pendulum_physics.bob_mass_kg = float(action.parameters["mass_kg"])

        self.pendulum_physics.is_bob_attached = True
        mass = self.pendulum_physics.bob_mass_kg
        obs = f"وزنه فلزی به جرم {mass * 1000:g} گرم به انتهای نخ متصل شد و آونگ در وضعیت تعادل عمودی قرار گرفت."

        is_step_completed = False
        if self.state.current_step <= 2:
            is_step_completed = True
            self.state.current_step = 3

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={"bob_mass_kg": mass, "pendulum_assembled": True},
            state_snapshot=self.state.to_dict()
        )

    def _handle_deflect_bob(self, action: LabAction) -> StepResult:
        """گام ۳: انحراف وزنه از خط تعادل با زاویه کوچک (زیر ۱۵ درجه)"""
        if not self.pendulum_physics.is_bob_attached:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_DEFLECT_WITHOUT_BOB",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="آونگ هنوز وزنه ندارد",
                    description="قبل از انحراف و رهاسازی، باید وزنه به نخ بسته شده باشد.",
                    scientific_rationale="حرکت نوسانی نیازمند جرم لَختی و نیروی بازگرداننده گرانش است.",
                    recommended_action="وزنه را به نخ وصل کنید."
                ),
                state_snapshot=self.state.to_dict()
            )

        angle = 10.0
        if action.parameters and "angle_deg" in action.parameters:
            angle = float(action.parameters["angle_deg"])

        # کنترل علمی محدودیت زاویه کوچک (Small-angle approximation)
        if angle > 15.0:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_LARGE_ANGLE_DEVIATION",
                    category=ErrorCategory.HAZARDOUS_ACTION,
                    title="زاویه انحراف از محدوده تقریب زاویه کوچک خارج است",
                    description=f"زاویه انتخاب‌شده ({angle} درجه) بیش از ۱۵ درجه است.",
                    scientific_rationale="رابطه دوره تناوب T = 2*pi*sqrt(L/g) تنها در زوایای کوچک (sin theta ~= theta) با خطای ناچیز معتبر است. در زوایای بزرگ، حرکت غیرخطی شده و دوره تناوب افزایش می‌یابد.",
                    recommended_action="وزنه را حداکثر تا ۱۰ الی ۱۵ درجه از وضعیت تعادل منحرف سازید."
                ),
                state_snapshot=self.state.to_dict()
            )

        self.pendulum_physics.initial_angle_deg = angle
        obs = f"وزنه با زاویه کوچک {angle} درجه از وضعیت تعادل منحرف و آماده رهاسازی شد (شرط حرکت هماهنگ ساده برقرار است)."

        is_step_completed = False
        if self.state.current_step <= 3:
            is_step_completed = True
            self.state.current_step = 4

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={"initial_angle_deg": angle, "is_small_angle": True},
            state_snapshot=self.state.to_dict()
        )

    def _handle_oscillate_and_measure(self, action: LabAction) -> StepResult:
        """گام ۴: آغاز نوسان، ثبت زمان و اندازه‌گیری دوره تناوب با کرونومتر"""
        if not self._has_tool("stopwatch"):
            self.state.workbench_tools.append("pendulum_stopwatch")

        if not self.pendulum_physics.is_bob_attached:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_OSCILLATION_INCOMPLETE",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="آونگ آماده نوسان نیست",
                    description="اجزای آونگ کامل نبوده و وزنه آماده نوسان نمی‌باشد.",
                    scientific_rationale="قبل از زمان‌گیری باید آونگ کامل و کمی منحرف شده باشد.",
                    recommended_action="مراحل قبل را تکمیل کنید."
                ),
                state_snapshot=self.state.to_dict()
            )

        self.pendulum_physics.is_oscillating = True
        data = self.pendulum_physics.calculate_motion_data()
        self.state.is_completed = True

        obs = (
            f"آونگ رها شد و نوسانات منظم هماهنگ آغاز گردید. زمان‌سنج برای {data['oscillations_count']} نوسان کامل، "
            f"مدت زمان {data['total_time_seconds']} ثانیه را ثبت کرد؛ بنابراین دوره تناوب تجربی T = {data['period_seconds']} ثانیه است. "
            f"با رابطه تئوری T = 2*pi*sqrt(L/g) انطباق کامل دارد و نشان می‌دهد تغییر جرم وزنه اثری بر زمان تناوب ندارد."
        )

        return StepResult(
            success=True,
            step_index=4,
            is_step_completed=True,
            observations=[obs],
            measurements=data,
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
                scientific_rationale="آزمایش نوسان مستلزم استقرار پایه، نخ، وزنه و زمان‌سنج است.",
                recommended_action=f"ابزار «{tool_name}» را از قفسه انتخاب نمایید."
            ),
            state_snapshot=self.state.to_dict()
        )
