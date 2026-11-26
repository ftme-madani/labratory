from typing import Optional, Dict, Any, List
from ..base import BaseExperimentEngine
from ..schema import (
    SimulationState,
    LabAction,
    StepResult,
    SimulationError,
    ErrorCategory
)
from .models import KNOWN_SOLUTIONS, KNOWN_INDICATORS, AqueousSolution, ChemicalIndicator

ACID_BASE_SOLUTION_ALIASES = {
    "beaker_soda": "beaker_baking_soda",
    "beaker_baking_soda": "beaker_baking_soda"
}

class AcidBaseSimulationEngine(BaseExperimentEngine):
    """
    موتور شبیه‌سازی آزمایش اسید، باز و شناساگرها (علوم تجربی هشتم، فصل ۲، ص ۱۶).
    مدل‌سازی دقیق تغییر رنگ شناساگرها بر حسب pH با قطعیت ۱۰۰٪ و بدون تصادف.
    """

    def __init__(self):
        super().__init__(experiment_id="exp-acid-base", total_steps=3)

    def _create_initial_state(self) -> SimulationState:
        return SimulationState(
            experiment_id="exp-acid-base",
            current_step=1,
            total_steps=3,
            workbench_tools=[],
            active_solutions={},
            recorded_observations=[],
            action_history=[],
            is_completed=False
        )

    def _process_scientific_action(self, action: LabAction) -> StepResult:
        """
        پردازش کنش غوطه‌وری شناساگر در محلول یا اندازه‌گیری pH
        """
        # بررسی فرضیه‌سازی و پیش‌بینی‌های نادرست اسید و باز دانش‌آموز
        params = action.parameters or {}
        prediction = str(params.get("prediction", "")).lower()
        if action.action_type in ["SUBMIT_PREDICTION", "PREDICT_PH", "PREDICT_INDICATOR"] or prediction:
            if prediction in ["phenolphthalein_pink_in_acid", "acid_is_pink", "phenolphthalein_broken"]:
                return StepResult(
                    success=False,
                    step_index=self.state.current_step,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_PHENOLPHTHALEIN_ACID_MISINTERPRETATION",
                        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
                        title="تفسیر نادرست رفتار فنل‌فتالئین در اسید",
                        description="بی‌رنگ ماندن فنل‌فتالئین در اسید طبیعی است و نشانه خرابی شناساگر نیست.",
                        scientific_rationale="فنل‌فتالئین در محیط‌های اسیدی (pH < 7) کاملاً بی‌رنگ است و منحصراً در بازها (pH > 8.2) ارغوانی می‌شود.",
                        recommended_action="تأیید کنید که فنل‌فتالئین در محیط اسیدی بی‌رنگ می‌ماند."
                    ),
                    state_snapshot=self.state.to_dict()
                )

            if prediction in ["water_is_acid", "water_is_base", "آب_مقطر_اسید_است", "آب_مقطر_باز_است"] or (params.get("target_id") in ["beaker_water", "water"] and params.get("predicted_ph") not in [None, 7, 7.0, "7", "neutral", "خنثی"]):
                return StepResult(
                    success=False,
                    step_index=self.state.current_step,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_WATER_PH_MISCONCEPTION",
                        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
                        title="اشتباه در خصلت خنثی آب خالص",
                        description="آب مقطر خالص اسیدی یا بازی نیست و pH آن برابر ۷ است.",
                        scientific_rationale="در آب خالص غلظت یون‌های H+ و OH- برابر است؛ بنابراین ماده‌ای کاملاً خنثی است و رنگ تورنسل را تغییر نمی‌دهد.",
                        recommended_action="مقدار pH آب خالص را برابر ۷ و خنثی ثبت فرمایید."
                    ),
                    state_snapshot=self.state.to_dict()
                )

        # کنش اصلی آزمایش: فرو بردن شناساگر در محلول
        if action.action_type in ["DIP_INDICATOR", "TEST_SOLUTION"]:
            return self._handle_indicator_test(action)

        # کنش سنجش مستقیم با pH‌متر دیجیتال
        if action.action_type == "MEASURE_PH":
            return self._handle_ph_measurement(action)

        # کنش ناشناخته یا پشتیبانی‌نشده
        return StepResult(
            success=False,
            step_index=self.state.current_step,
            is_step_completed=False,
            error=SimulationError(
                code="ERR_UNSUPPORTED_ACTION",
                category=ErrorCategory.UNSUPPORTED_COMBINATION,
                title="عملیات علمی پشتیبانی‌نشده",
                description=f"عملیات «{action.action_type}» برای این آزمایش تعریف نشده است.",
                scientific_rationale="در این آزمایش فقط آزمون‌های مبتنی بر شناساگر و اندازه‌گیری pH مجاز هستند.",
                recommended_action="شناساگر را انتخاب کرده و در محلول مورد نظر قرار دهید."
            ),
            state_snapshot=self.state.to_dict()
        )

    def _handle_indicator_test(self, action: LabAction) -> StepResult:
        indicator_raw = action.source_id or ""
        solution_raw = action.target_id or ""
        indicator_id = indicator_raw.replace("-", "_")
        target_solution_id = solution_raw.replace("-", "_")
        if target_solution_id in ACID_BASE_SOLUTION_ALIASES:
            target_solution_id = ACID_BASE_SOLUTION_ALIASES[target_solution_id]

        # ۱. اعتبارسنجی حضور شناساگر
        if not indicator_id or indicator_id not in KNOWN_INDICATORS:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_WRONG_TOOL_INDICATOR",
                    category=ErrorCategory.WRONG_TOOL,
                    title="وسیلهٔ انتخاب‌شده شناساگر شیمیایی نیست",
                    description=f"وسیله «{action.source_id}» قابلیت تشخیص اسید و باز را ندارد.",
                    scientific_rationale="برای بررسی اسید و باز باید از شناساگرهای رنگی نظیر تورنسل یا فنل‌فتالئین استفاده شود.",
                    recommended_action="از قفسه ابزارها، کاغذ تورنسل آبی یا سرخ را انتخاب کنید."
                ),
                state_snapshot=self.state.to_dict()
            )

        # ۲. اعتبارسنجی حضور محلول هدف
        if not target_solution_id or target_solution_id not in KNOWN_SOLUTIONS:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_WRONG_REAGENT_SOLUTION",
                    category=ErrorCategory.WRONG_REAGENT,
                    title="ظرف یا مادهٔ انتخابی نامعتبر است",
                    description=f"محلول «{action.target_id}» در فهرست مواد این آزمایش وجود ندارد.",
                    scientific_rationale="شناساگر باید درون یک محلول مجهول آبی استاندارد فرو برده شود.",
                    recommended_action="یکی از بشرهای آب‌لیمو، آب‌صابون یا آب‌مقطر را به عنوان هدف انتخاب کنید."
                ),
                state_snapshot=self.state.to_dict()
            )

        # ۳. کنترل پیش‌شرط: آیا هر دو ابزار روی میز آزمایشگاه هستند؟
        bench_normalized = {t.replace("-", "_") for t in self.state.workbench_tools}
        for b in list(bench_normalized):
            if b in ACID_BASE_SOLUTION_ALIASES:
                bench_normalized.add(ACID_BASE_SOLUTION_ALIASES[b])

        if indicator_id not in bench_normalized and indicator_raw not in self.state.workbench_tools:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_PRECONDITION_INDICATOR_NOT_ON_BENCH",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="شناساگر هنوز روی میز قرار نگرفته است",
                    description=f"ابزار «{action.source_id}» هنوز از قفسه به میز کار اضافه نشده است.",
                    scientific_rationale="ابتدا ابزار باید در دسترس آزمایشگر روی میز چیده شود.",
                    recommended_action=f"ابتدا با عملیات ADD_TOOL شناساگر «{action.source_id}» را روی میز بیاورید."
                ),
                state_snapshot=self.state.to_dict()
            )

        if target_solution_id not in bench_normalized and solution_raw not in self.state.workbench_tools:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_PRECONDITION_SOLUTION_NOT_ON_BENCH",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="ظرف محلول روی میز کار نیست",
                    description=f"ظرف «{action.target_id}» روی میز کار آزمایشگاه قرار ندارد.",
                    scientific_rationale="برای انجام واکنش، ظرف آزمایش باید روی سطح کار مستقر باشد.",
                    recommended_action=f"ظرف «{action.target_id}» را از قفسه به میز کار انتقال دهید."
                ),
                state_snapshot=self.state.to_dict()
            )

        solution = KNOWN_SOLUTIONS[target_solution_id]
        indicator = KNOWN_INDICATORS[indicator_id]

        # ۴. محاسبه دقیق تغییر رنگ بر پایه pH محلول (Deterministic Chemical Calculation)
        resulting_color, color_name_fa, color_changed = self._calculate_indicator_color(solution, indicator)

        observations: List[str] = []
        is_step_completed = False

        # ۵. ارزیابی گام درسی بر اساس سرفصل علوم پایه هشتم (صفحه ۱۶)
        # گام ۱: اثبات خصلت اسیدی آب‌لیمو با تورنسل آبی
        if self.state.current_step == 1:
            if solution.id == "beaker_lemon" and indicator.id == "litmus_blue":
                observations.append(
                    f"کاغذ تورنسل آبی پس از تماس با {solution.name_fa} بلافاصله به رنگ سرخ درآمد (pH={solution.nominal_ph}). این پدیده خصلت اسیدی آب‌لیمو را اثبات می‌کند."
                )
                is_step_completed = True
                self.state.current_step = 2
            elif solution.id == "beaker_lemon" and indicator.id == "litmus_red":
                # خطای آموزشی: استفاده از تورنسل سرخ برای اسید
                return StepResult(
                    success=False,
                    step_index=1,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_INEFFECTIVE_INDICATOR_RED_ON_ACID",
                        category=ErrorCategory.WRONG_TOOL,
                        title="شناساگر برای اثبات خاصیت اسیدی مناسب نیست",
                        description="کاغذ تورنسل سرخ در تماس با آب‌لیمو بدون تغییر ماند.",
                        scientific_rationale="کاغذ تورنسل سرخ از قبل در فرم اسیدی قرار دارد و در محیط‌های اسیدی (pH < 7) تغییر رنگ نمی‌دهد.",
                        recommended_action="برای اثبات خصلت اسیدی از کاغذ تورنسل آبی استفاده کنید تا با سرخ شدن، حضور اسید را نشان دهد."
                    ),
                    measurements={"ph": solution.nominal_ph, "color": resulting_color},
                    state_snapshot=self.state.to_dict()
                )
            else:
                # ترتیب نادرست
                return StepResult(
                    success=False,
                    step_index=1,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_ORDER_VIOLATION_STEP1",
                        category=ErrorCategory.ORDER_VIOLATION,
                        title="ترتیب گام‌های آزمایش رعایت نشد",
                        description=f"در گام اول باید خصلت اسیدی آب‌لیمو بررسی شود، اما شما «{solution.name_fa}» را آزمودید.",
                        scientific_rationale="پروتکل درسی آزمایش‌ها به منظور مقایسه هدفمند، با نمونه اسیدی آغاز می‌شود.",
                        recommended_action="ابتدا بشر آب‌لیمو را با کاغذ تورنسل آبی آزمایش کنید."
                    ),
                    state_snapshot=self.state.to_dict()
                )

        # گام ۲: اثبات خصلت بازی آب‌صابون / جوش شیرین با تورنسل سرخ
        elif self.state.current_step == 2:
            if solution.id in ["beaker_soap", "beaker_baking_soda"] and indicator.id == "litmus_red":
                observations.append(
                    f"کاغذ تورنسل سرخ در تماس با {solution.name_fa} به رنگ آبی تغییر کرد (pH={solution.nominal_ph}). این واکنش خصلت بازی را اثبات می‌کند."
                )
                is_step_completed = True
                self.state.current_step = 3
            elif solution.id in ["beaker_soap", "beaker_baking_soda"] and indicator.id == "litmus_blue":
                return StepResult(
                    success=False,
                    step_index=2,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_INEFFECTIVE_INDICATOR_BLUE_ON_BASE",
                        category=ErrorCategory.WRONG_TOOL,
                        title="شناساگر برای اثبات خاصیت بازی مناسب نیست",
                        description=f"کاغذ تورنسل آبی در تماس با {solution.name_fa} تغییر رنگ نداد و آبی ماند.",
                        scientific_rationale="کاغذ تورنسل آبی در محیط‌های بازی (pH > 7) تغییر رنگ نمی‌دهد.",
                        recommended_action="برای اثبات خصلت بازی، از کاغذ تورنسل سرخ استفاده کنید."
                    ),
                    measurements={"ph": solution.nominal_ph, "color": resulting_color},
                    state_snapshot=self.state.to_dict()
                )
            else:
                return StepResult(
                    success=False,
                    step_index=2,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_ORDER_VIOLATION_STEP2",
                        category=ErrorCategory.ORDER_VIOLATION,
                        title="محلول نامربوط در گام دوم",
                        description=f"در گام دوم باید محلول بازی بررسی شود، اما شما «{solution.name_fa}» را انتخاب کردید.",
                        scientific_rationale="گام دوم به بررسی نمونه قلیایی اختصاص دارد.",
                        recommended_action="بشر بازی را با کاغذ تورنسل سرخ آزمایش کنید."
                    ),
                    state_snapshot=self.state.to_dict()
                )

        # گام ۳: اثبات خصلت خنثی آب‌مقطر (عدم تغییر رنگ هر دو شناساگر)
        elif self.state.current_step == 3:
            if solution.id == "beaker_water":
                observations.append(
                    f"کاغذ {indicator.name_fa} در تماس با آب‌مقطر خالص تغییر رنگ نداد ({color_name_fa} ماند). غلظت یون‌های H+ و OH- برابر است و ماده خنثی است (pH=7.0)."
                )
                is_step_completed = True
                self.state.is_completed = True
            else:
                return StepResult(
                    success=False,
                    step_index=3,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_ORDER_VIOLATION_STEP3",
                        category=ErrorCategory.ORDER_VIOLATION,
                        title="محلول نامربوط در گام سوم",
                        description="در گام پایانی باید رفتار آب‌مقطر به عنوان نمونه خنثی بررسی شود.",
                        scientific_rationale="نمونه خنثی مقیاس مقایسه با اسید و باز است.",
                        recommended_action="بشر آب‌مقطر را انتخاب کنید."
                    ),
                    state_snapshot=self.state.to_dict()
                )

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=observations,
            measurements={
                "target_solution": solution.id,
                "solution_ph": solution.nominal_ph,
                "indicator_id": indicator.id,
                "resulting_color_hex": resulting_color,
                "color_name_fa": color_name_fa,
                "color_changed": color_changed
            },
            state_snapshot=self.state.to_dict(),
            is_terminal=self.state.is_completed
        )

    def _calculate_indicator_color(self, solution: AqueousSolution, indicator: ChemicalIndicator) -> tuple[str, str, bool]:
        """
        محاسبه علمی رنگ نهایی شناساگر با تکیه بر آستانه pH:
        - اگر pH < transition_low_ph: رنگ اسیدی
        - اگر pH > transition_high_ph: رنگ بازی
        - در غیر این صورت: رنگ خنثی
        """
        ph = solution.nominal_ph

        if indicator.id == "litmus_blue":
            if ph < indicator.transition_low_ph:
                return indicator.acidic_color_hex, "سرخ", True
            else:
                return indicator.basic_color_hex, "آبی بدون تغییر", False

        elif indicator.id == "litmus_red":
            if ph > indicator.transition_high_ph:
                return indicator.basic_color_hex, "آبی", True
            else:
                return indicator.acidic_color_hex, "سرخ بدون تغییر", False

        elif indicator.id == "phenolphthalein":
            if ph >= indicator.transition_low_ph:
                return indicator.basic_color_hex, "ارغوانی تند", True
            else:
                return indicator.acidic_color_hex, "بی‌رنگ شفاف", False

        return "#CBD5E1", "نامشخص", False

    def _handle_ph_measurement(self, action: LabAction) -> StepResult:
        """سنجش دقیق pH با سنسور یا پی‌اچ‌متر دیجیتال"""
        solution_raw = action.target_id or ""
        solution_id = solution_raw.replace("-", "_")
        if solution_id in ACID_BASE_SOLUTION_ALIASES:
            solution_id = ACID_BASE_SOLUTION_ALIASES[solution_id]

        if not solution_id or solution_id not in KNOWN_SOLUTIONS:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_UNKNOWN_SOLUTION_PH",
                    category=ErrorCategory.WRONG_REAGENT,
                    title="محلول نامعتبر برای سنجش pH",
                    description=f"محلول «{solution_id}» برای اندازه‌گیری وجود ندارد.",
                    scientific_rationale="الکترود pH‌متر باید درون محلول آبی تمیز غوطه‌ور شود.",
                    recommended_action="یکی از بشرهای آزمایشگاه را انتخاب کنید."
                ),
                state_snapshot=self.state.to_dict()
            )

        solution = KNOWN_SOLUTIONS[solution_id]
        obs = f"دستگاه pH‌متر دیجیتال برای {solution.name_fa} مقدار دقیق pH={solution.nominal_ph} را ثبت کرد."

        is_step_completed = False
        if self.state.current_step == 3:
            is_step_completed = True
            self.state.is_completed = True

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={
                "solution_id": solution.id,
                "ph_value": solution.nominal_ph,
                "classification": "اسیدی" if solution.nominal_ph < 7 else ("بازی" if solution.nominal_ph > 7 else "خنثی")
            },
            state_snapshot=self.state.to_dict(),
            is_terminal=self.state.is_completed
        )
