from typing import Dict, Any, List
from ..base import BaseExperimentEngine
from ..schema import (
    SimulationState,
    LabAction,
    StepResult,
    SimulationError,
    ErrorCategory
)
from .models import PlantTransportState

TOOL_ALIASES = {
    "glass_cup": "glass_cup",
    "cup": "glass_cup",
    "transparent_cup": "glass_cup",
    "water_pitcher": "water_pitcher",
    "water": "water_pitcher",
    "food_coloring": "food_coloring",
    "food_coloring_bottle": "food_coloring",
    "color": "food_coloring",
    "celery_stalk": "celery_stalk",
    "celery": "celery_stalk"
}

class PlantWaterTransportEngine(BaseExperimentEngine):
    """
    موتور شبیه‌سازی انتقال آب در گیاه و مشاهده هدایت شیره خام در آوندهای چوبی کرفس.
    منبع: علوم تجربی پایه هفتم، فصل ۱۲ (سفره سلامت / انتقال در گیاهان).
    """

    def __init__(self):
        super().__init__(experiment_id="plant-water-transport-celery", total_steps=5)
        self.transport_physics = PlantTransportState()

    def _create_initial_state(self) -> SimulationState:
        self.transport_physics = PlantTransportState()
        return SimulationState(
            experiment_id="plant-water-transport-celery",
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

        # ۱. بررسی فرضیه‌سازی و خطاهای مفهومی گیاه‌شناسی دانش‌آموز
        params = action.parameters or {}
        predicted_path = str(params.get("predicted_path", "")).lower()
        prediction = str(params.get("prediction", "")).lower()
        if action.action_type in ["SUBMIT_PREDICTION", "PREDICT_PATH"] or predicted_path or prediction:
            if predicted_path in ["stem_flesh", "cortex", "skin", "بدون_آوند", "پوست_ساقه", "گوشت_ساقه"] or prediction in ["stem_flesh", "cortex", "skin", "بدون_آوند"]:
                return StepResult(
                    success=False,
                    step_index=self.state.current_step,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_MISCONCEPTION_XYLEM_PATH",
                        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
                        title="تصور نادرست هدایت آب بدون بافت آوندی",
                        description="آب و مواد محلول در ساقه به صورت نامنظم و اسفنجی پخش نمی‌شوند.",
                        scientific_rationale="گیاهان برای جابه‌جایی شیره خام دارای لوله‌های اختصاصی به نام آوند چوبی (Xylem) هستند که در مقطع ساقه به شکل دسته‌های آوندی مشخص دیده می‌شوند.",
                        recommended_action="مسیر صعود آب را منحصراً از طریق آوندهای چوبی ثبت نمایید."
                    ),
                    state_snapshot=self.state.to_dict()
                )

            if params.get("leaves_needed") is False or prediction in ["no_leaves", "بدون_برگ", "no_transpiration"]:
                return StepResult(
                    success=False,
                    step_index=self.state.current_step,
                    is_step_completed=False,
                    error=SimulationError(
                        code="ERR_MISCONCEPTION_NO_LEAVES_NEEDED",
                        category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
                        title="نادیده گرفتن نقش کشش تعرقی روزنه‌های برگ",
                        description="صعود آب به سمت بالای ساقه نیازمند مکش تعرقی ناشی از برگ‌هاست.",
                        scientific_rationale="تبخیر آب از روزنه‌های هوایی برگ (تعرق) موتور محرک اصلی کشش ستون آب در آوندهای چوبی است و بدون برگ این فرآیند متوقف یا بسیار کند می‌شود.",
                        recommended_action="نقش برگ‌ها و کشش تعرقی را در صعود آب تأیید کنید."
                    ),
                    state_snapshot=self.state.to_dict()
                )

        if action.action_type in ["POUR_WATER", "FILL_WATER"]:
            return self._handle_pour_water(action)

        if action.action_type in ["ADD_COLOR", "DROP_FOOD_COLORING", "ADD_FOOD_COLORING"]:
            return self._handle_add_color(action)

        if action.action_type in ["INSERT_CELERY", "PLACE_STALK"]:
            return self._handle_insert_celery(action)

        if action.action_type in ["SET_TIME", "ADVANCE_TIME", "OBSERVE_TIME", "SIMULATE_TIME"]:
            return self._handle_advance_time(action)

        if action.action_type in ["EXAMINE_XYLEM", "CHECK_LEAF_VEINS", "OBSERVE_STALK", "OBSERVE_CROSS_SECTION"]:
            return self._handle_examine_xylem(action)

        if action.action_type == "SET_PARAMETERS":
            params = action.parameters or {}
            if "color" in params:
                self.transport_physics.color_chosen = str(params["color"])
            if "hours" in params:
                self.transport_physics.observation_hours = float(params["hours"])

            data = self.transport_physics.calculate_transport_progress()
            return StepResult(
                success=True,
                step_index=self.state.current_step,
                is_step_completed=False,
                observations=[f"زمان مشاهده روی {self.transport_physics.observation_hours} ساعت و رنگ انتخابی به «{data['color_name_fa']}» تنظیم شد."],
                measurements=data,
                state_snapshot=self.state.to_dict()
            )

        return StepResult(
            success=False,
            step_index=self.state.current_step,
            is_step_completed=False,
            error=SimulationError(
                code="ERR_UNSUPPORTED_PLANT_ACTION",
                category=ErrorCategory.UNSUPPORTED_COMBINATION,
                title="عملیات نامعتبر در آزمایش گیاه",
                description=f"عملیات «{action.action_type}» در این شبیه‌سازی تعریف نشده است.",
                scientific_rationale="آزمایش انتقال آب شامل ریختن آب، چکاندن رنگ خوراکی، قرار دادن ساقه کرفس و رصد پیشروی در زمان است.",
                recommended_action="یکی از مراحل انتقال آب در گیاه را انجام دهید."
            ),
            state_snapshot=self.state.to_dict()
        )

    def _handle_pour_water(self, action: LabAction) -> StepResult:
        """گام ۱: ریختن آب درون لیوان شفاف"""
        if not self._has_tool("glass_cup"):
            return self._make_precondition_error("glass_cup", "لیوان شفاف آزمایشگاهی")
        if not self._has_tool("water_pitcher"):
            return self._make_precondition_error("water_pitcher", "پارچ آب")

        self.transport_physics.is_water_poured = True
        obs = "آب زلال به میزان ۱۵۰ میلی‌لیتر درون لیوان شیشه‌ای شفاف ریخته شد."

        is_step_completed = False
        if self.state.current_step == 1:
            is_step_completed = True
            self.state.current_step = 2

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={"water_volume_ml": 150.0},
            state_snapshot=self.state.to_dict()
        )

    def _handle_add_color(self, action: LabAction) -> StepResult:
        """گام ۲: چکاندن چند قطره رنگ خوراکی در آب و ایجاد محلول رنگی"""
        if not self.transport_physics.is_water_poured:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_COLOR_BEFORE_WATER",
                    category=ErrorCategory.ORDER_VIOLATION,
                    title="ابتدا باید آب در لیوان باشد",
                    description="چکاندن رنگ در لیوان خالی باعث حل شدن و رقیق شدن مناسب آن نمی‌شود.",
                    scientific_rationale="رنگ خوراکی به عنوان ردیاب محلول در آب عمل می‌کند و باید در حلال آب یکنواخت پخش شود.",
                    recommended_action="ابتدا آب را داخل لیوان بریزید و سپس قطرات رنگ را اضافه کنید."
                ),
                state_snapshot=self.state.to_dict()
            )

        if not self._has_tool("food_coloring"):
            return self._make_precondition_error("food_coloring", "قطره‌چکان رنگ خوراکی")

        if action.parameters and "color" in action.parameters:
            self.transport_physics.color_chosen = str(action.parameters["color"])

        self.transport_physics.is_color_added = True
        c_name = "سرخ" if self.transport_physics.color_chosen == "red" else "آبی"
        obs = f"چند قطره رنگ خوراکی {c_name} به آب اضافه شد و با پخش تدریجی، محلول شفاف و رنگینی حاصل شد."

        is_step_completed = False
        if self.state.current_step <= 2:
            is_step_completed = True
            self.state.current_step = 3

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={"solution_color": self.transport_physics.color_chosen, "color_name_fa": c_name},
            state_snapshot=self.state.to_dict()
        )

    def _handle_insert_celery(self, action: LabAction) -> StepResult:
        """گام ۳: قرار دادن انتهای بریده‌شده ساقه کرفس درون آب رنگی"""
        if not self.transport_physics.is_color_added:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_CELERY_IN_CLEAR_WATER",
                    category=ErrorCategory.WRONG_TOOL,
                    title="آب فاقد رنگ نشانگر است",
                    description="قرار دادن ساقه در آب بدون رنگ، امکان رصد بصری مسیر آوندها را از شما می‌گیرد.",
                    scientific_rationale="آب شفاف در بافت گیاه قابل تشخیص نیست و رنگ خوراکی نقش ردیاب فیزیکی را ایفا می‌کند.",
                    recommended_action="ابتدا رنگ خوراکی را به آب بیفزایید تا مسیر آوندها نمایان گردد."
                ),
                state_snapshot=self.state.to_dict()
            )

        if not self._has_tool("celery_stalk"):
            return self._make_precondition_error("celery_stalk", "ساقه کرفس تازه")

        self.transport_physics.is_celery_inserted = True
        obs = "ساقه کرفس با مقطع تازه در آب رنگی قرار گرفت. آوندهای چوبی در انتهای ساقه در تماس مستقیم با محلول قرار دارند."

        is_step_completed = False
        if self.state.current_step <= 3:
            is_step_completed = True
            self.state.current_step = 4

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={"stalk_inserted": True},
            state_snapshot=self.state.to_dict()
        )

    def _handle_advance_time(self, action: LabAction) -> StepResult:
        """گام ۴: مشاهده روند فشرده گذر زمان در آزمایشگاه مجازی"""
        if not self.transport_physics.is_celery_inserted:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_CELERY_NOT_IN_WATER",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="ساقه کرفس هنوز در آب قرار نگرفته است",
                    description="برای مشاهده انتقال آب با گذشت زمان، ابتدا باید کرفس در آب رنگی غوطه‌ور باشد.",
                    scientific_rationale="جذب آب مستلزم قرارگیری اندام جاذب در منبع آب است.",
                    recommended_action="ساقه کرفس را درون لیوان آب رنگی قرار دهید."
                ),
                state_snapshot=self.state.to_dict()
            )

        if action.parameters and "hours" in action.parameters:
            self.transport_physics.observation_hours = float(action.parameters["hours"])

        data = self.transport_physics.calculate_transport_progress()
        obs = (
            f"با شبیه‌سازی گذر زمان فشرده به میزان {data['observation_hours']} ساعت، "
            f"آب رنگی به ارتفاع {data['height_ascended_cm']} سانتی‌متر ({data['ascent_percentage']}٪ از طول ساقه) در آوندهای چوبی بالا رفت."
        )

        is_step_completed = False
        if self.state.current_step <= 4:
            is_step_completed = True
            self.state.current_step = 5

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements=data,
            state_snapshot=self.state.to_dict()
        )

    def _handle_examine_xylem(self, action: LabAction) -> StepResult:
        """گام ۵: بررسی مقطع ساقه، رگبرگ‌ها و ثبت تبیین علمی تعرق و آوند چوبی"""
        if not self.transport_physics.is_celery_inserted:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_CELERY_NOT_READY",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="ساقه کرفس آماده بررسی نیست",
                    description="آزمایش هنوز به مرحله نهایی نرسیده است.",
                    scientific_rationale="بررسی رگبرگ‌ها مستلزم طی شدن فرآیند صعود آب است.",
                    recommended_action="مراحل قبلی را انجام دهید."
                ),
                state_snapshot=self.state.to_dict()
            )

        data = self.transport_physics.calculate_transport_progress()
        self.state.is_completed = True

        obs = (
            f"در مقطع عرضی ساقه، دسته‌های آوند چوبی (Xylem) به وضوح به رنگ {data['color_name_fa']} درآمده‌اند "
            f"و رگبرگ‌های برگ‌ها رنگین شده‌اند. "
            f"این رخداد ثابت می‌کند آب و مواد محلول توسط بافت آوند چوبی و با کمک مکش تعرقی (تبخیر آب از روزنه‌های برگ) به سمت بالا جریان دارند. "
            f"(توجه: این شبیه‌سازی گذر زمان ۲۴ ساعته را به شکل فشرده نمایش می‌دهد)."
        )

        return StepResult(
            success=True,
            step_index=5,
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
                scientific_rationale="انجام آزمایش زیست‌شناسی نیازمند چیدمان وسایل روی میز است.",
                recommended_action=f"«{tool_name}» را از قفسه انتخاب نمایید."
            ),
            state_snapshot=self.state.to_dict()
        )
