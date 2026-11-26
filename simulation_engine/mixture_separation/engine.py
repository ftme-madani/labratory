from typing import Dict, Any, List
from ..base import BaseExperimentEngine
from ..schema import (
    SimulationState,
    LabAction,
    StepResult,
    SimulationError,
    ErrorCategory
)
from .models import MixtureState

TOOL_ALIASES = {
    "mixture_beaker": "beaker_sand_salt",
    "beaker_sand_salt": "mixture_beaker",
    "water_bottle": "wash_bottle_water",
    "wash_bottle_water": "water_bottle",
    "filter_funnel": "funnel_filter_paper",
    "funnel_filter_paper": "filter_funnel",
    "funnel": "funnel_filter_paper",
}

class MixtureSeparationEngine(BaseExperimentEngine):
    """
    موتور شبیه‌سازی جداسازی مخلوط ماسه، نمک و آب.
    منبع: علوم تجربی پایه هشتم، فصل ۱ (مخلوط و جداسازی مواد)، صفحه ۶.
    قواعد فیزیکی: انحلال‌پذیری تفکیکی، فیلتراسیون فاز جامد، تبخیر و بلورزایی.
    """

    def __init__(self):
        super().__init__(experiment_id="exp-mixture-separation", total_steps=3)
        self.mixture_physics = MixtureState()

    def _create_initial_state(self) -> SimulationState:
        self.mixture_physics = MixtureState()
        return SimulationState(
            experiment_id="exp-mixture-separation",
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
        if action.action_type in ["SUBMIT_PREDICTION", "PREDICT_SEPARATION"] or prediction:
            if prediction in ["boil_dry", "heat_dry_salt", "شعله_مستقیم_به_نمک_خشک"] or params.get("heat_after_dry") is True:
                return StepResult(
                    success=False,
                    step_index=self.state.current_step,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_BOIL_DRY_EXPLOSION",
                        category=ErrorCategory.HAZARDOUS_ACTION,
                        title="خطر پرتاب دانه‌های داغ نمک و شکستن کپسول",
                        description="حرارت مستقیم با شعله تند پس از تبخیر تمام آب باعث ته‌پریدگی نمک می‌شود.",
                        scientific_rationale="به محض مشاهده اولین بلورهای نمک و کم شدن آب باید حرارت را ملایم یا قطع کرد تا از ترکیدن کپسول و پرتاب ذرات داغ جلوگیری شود.",
                        recommended_action="به محض مشاهده اولین بلورهای نمک شعله را خاموش نمایید."
                    ),
                    state_snapshot=self.state.to_dict()
                )

        if action.action_type in ["DISSOLVE", "ADD_WATER_AND_STIR"]:
            return self._handle_dissolution(action)

        if action.action_type in ["FILTER", "FILTER_MIXTURE"]:
            return self._handle_filtration(action)

        if action.action_type in ["HEAT", "EVAPORATE_AND_CRYSTALLIZE"]:
            return self._handle_evaporation(action)

        return StepResult(
            success=False,
            step_index=self.state.current_step,
            is_step_completed=False,
            error=SimulationError(
                code="ERR_UNSUPPORTED_MIXTURE_ACTION",
                category=ErrorCategory.UNSUPPORTED_COMBINATION,
                title="عملیات جداسازی نامعتبر است",
                description=f"عملیات «{action.action_type}» در فرآیند جداسازی ماسه و نمک تعریف نشده است.",
                scientific_rationale="جداسازی این مخلوط شامل ۳ مرحله اصلی است: حل‌کردن در آب، صاف‌کردن و تبخیر.",
                recommended_action="یکی از مراحل انحلال، فیلتراسیون یا تبخیر را انتخاب کنید."
            ),
            state_snapshot=self.state.to_dict()
        )

    def _has_tool(self, tool_id: str) -> bool:
        normalized_tools = {t.replace("-", "_") for t in self.state.workbench_tools}
        target = tool_id.replace("-", "_")
        if target in normalized_tools:
            return True
        alias = TOOL_ALIASES.get(target)
        if alias and alias.replace("-", "_") in normalized_tools:
            return True
        return False

    def _handle_dissolution(self, action: LabAction) -> StepResult:
        """گام ۱: افزودن آب به مخلوط و هم‌زدن برای انحلال نمک"""
        # کنترل حضور وسایل روی میز
        if not self._has_tool("beaker_sand_salt"):
            return self._make_precondition_error("beaker_sand_salt", "بشر مخلوط نمک و ماسه")
        if not self._has_tool("wash_bottle_water"):
            return self._make_precondition_error("wash_bottle_water", "پیست آب‌مقطر")

        # تغییر وضعیت فیزیکی
        self.mixture_physics.water_volume_ml = 50.0
        self.mixture_physics.is_salt_dissolved = True

        obs = (
            "آب مقطر به مخلوط اضافه شد. با هم زدن، نمک طعام (NaCl) به دلیل ساختار یونی قطبی در آب کاملاً حل شد، "
            "اما ذرات ماسه (SiO2) به دلیل پیوند کووالانسی شبکه‌ای نامحلول مانده و در ته بشر ته‌نشین شدند."
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
                "water_volume_ml": self.mixture_physics.water_volume_ml,
                "salt_dissolved": self.mixture_physics.is_salt_dissolved,
                "sand_phase": "رسوب نامحلول",
                "phase_description": self.mixture_physics.liquid_phase_description
            },
            state_snapshot=self.state.to_dict()
        )

    def _handle_filtration(self, action: LabAction) -> StepResult:
        """گام ۲: فیلتراسیون ماسه با قیف و کاغذ صافی"""
        tools = self.state.workbench_tools

        # کنترل پیش‌نیاز: آیا مرحله انحلال انجام شده است؟
        if not self.mixture_physics.has_liquid or not self.mixture_physics.is_salt_dissolved:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_FILTER_WITHOUT_DISSOLUTION",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="مخلوط فاقد حلال مایع است",
                    description="نمی‌توان مخلوط جامد خشک ماسه و نمک را بدون افزودن آب از کاغذ صافی عبور داد.",
                    scientific_rationale="کاغذ صافی ذرات جامد معلق در مایع را جدا می‌کند. ابتدا باید نمک حل شود.",
                    recommended_action="ابتدا به مخلوط آب اضافه کرده و هم بزنید، سپس آن را صاف کنید."
                ),
                state_snapshot=self.state.to_dict()
            )

        if not self._has_tool("funnel_filter_paper"):
            return self._make_precondition_error("funnel_filter_paper", "قیف و کاغذ صافی")

        self.mixture_physics.is_sand_filtered = True

        obs = (
            "محتویات بشر روی قیف و کاغذ صافی ریخته شد. ذرات درشت ماسه پشت روزنه‌های کاغذ صافی باقی ماندند "
            "و محلول زلال و شفاف آب‌نمک از فیلتر عبور کرده و در ارلن جمع‌آوری شد."
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
                "sand_filtered": True,
                "filtrate": "محلول زلال آب‌نمک",
                "filter_residue": "ماسه مرطوب"
            },
            state_snapshot=self.state.to_dict()
        )

    def _handle_evaporation(self, action: LabAction) -> StepResult:
        """گام ۳: تبخیر آب روی شعله و بازیابی بلورهای نمک"""
        # کنترل خطای بحرانی: حرارت دادن قبل از صاف کردن
        if not self.mixture_physics.is_sand_filtered:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_HEAT_BEFORE_FILTER",
                    category=ErrorCategory.ORDER_VIOLATION,
                    title="حرارت دادن پیش از فیلتراسیون ماسه خطاست",
                    description="شما قبل از جدا کردن ماسه، مخلوط را روی شعله حرارت دادید.",
                    scientific_rationale="حرارت دادن مخلوط همراه با ماسه باعث سوختن رسوب و پاشش خطرناک می‌شود و نمک را از ماسه جدا نمی‌کند.",
                    recommended_action="ابتدا ماسه را با قیف و کاغذ صافی جدا کنید، سپس مایع زلال آب‌نمک را حرارت دهید."
                ),
                state_snapshot=self.state.to_dict()
            )

        if not self._has_tool("evaporating_dish"):
            return self._make_precondition_error("evaporating_dish", "کپسول چینی تبخیر")
        if not self._has_tool("bunsen_burner"):
            return self._make_precondition_error("bunsen_burner", "چراغ بونزن و سه‌پایه")

        self.mixture_physics.has_heat_source = True
        self.mixture_physics.is_water_evaporated = True
        self.mixture_physics.is_salt_recovered = True
        self.state.is_completed = True

        obs = (
            "محلول آب‌نمک درون کپسول چینی روی شعله بونزن به جوش آمد (نقطه جوش ۱۰۰°C). با تبخیر تدریجی آب، "
            "بلورهای سفید و مکعبی نمک طعام (NaCl) در کف کپسول چینی تبلور یافته و جداسازی کامل گردید."
        )

        return StepResult(
            success=True,
            step_index=3,
            is_step_completed=True,
            observations=[obs],
            measurements={
                "water_evaporated": True,
                "salt_recovered_g": self.mixture_physics.salt_mass_g,
                "purity_percent": 99.2,
                "crystallized": True
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
                scientific_rationale="انجام عملیات آزمایشگاهی مستلزم استقرار ابزار روی میز کار است.",
                recommended_action=f"ابزار «{tool_name}» را از قفسه انتخاب نمایید."
            ),
            state_snapshot=self.state.to_dict()
        )
