from typing import Dict, Any, List
from ..base import BaseExperimentEngine
from ..schema import (
    SimulationState,
    LabAction,
    StepResult,
    SimulationError,
    ErrorCategory
)
from .models import WaterFilterState, LAYER_SPECS

TOOL_ALIASES = {
    "filter_column_bottle": "filter_column_bottle",
    "bottle": "filter_column_bottle",
    "plastic_bottle": "filter_column_bottle",
    "cotton_layer": "cotton_layer",
    "cotton": "cotton_layer",
    "fine_sand_layer": "fine_sand_layer",
    "sand_layer": "fine_sand_layer",
    "sand": "fine_sand_layer",
    "gravel_layer": "gravel_layer",
    "gravel": "gravel_layer",
    "dirty_water_flask": "dirty_water_flask",
    "turbid_water_beaker": "dirty_water_flask",
    "dirty_water": "dirty_water_flask",
    "collection_beaker": "collection_beaker",
    "collection_cup": "collection_beaker",
    "beaker": "collection_beaker"
}

class WaterFiltrationEngine(BaseExperimentEngine):
    """
    موتور شبیه‌سازی ساخت صافی چندلایه آب و تصفیه فیزیکی ذرات معلق.
    منبع: علوم تجربی پایه هفتم، فصل ۳ (اتم‌ها، الفبای مواد و مخلوط‌ها).
    """

    def __init__(self):
        super().__init__(experiment_id="water-filtration-column", total_steps=5)
        self.filter_physics = WaterFilterState()

    def _create_initial_state(self) -> SimulationState:
        self.filter_physics = WaterFilterState()
        return SimulationState(
            experiment_id="water-filtration-column",
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

        # ۱. بررسی فرضیه‌سازی و خطاهای بهداشتی/مفهومی تصفیه آب دانش‌آموز
        params = action.parameters or {}
        prediction = str(params.get("prediction", "")).lower()
        if action.action_type in ["DRINK_WATER", "DRINK_FILTERED_WATER"] or params.get("is_potable") is True or prediction in ["potable", "drinkable", "آشامیدنی"]:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_MISCONCEPTION_POTABLE_WATER",
                    category=ErrorCategory.HAZARDOUS_ACTION,
                    title="هشدار بهداشتی: آب خروجی غیرقابل شرب است",
                    description="آب حاصل از فیلتراسیون فیزیکی به هیچ وجه استریل و آشامیدنی نیست.",
                    scientific_rationale="صافی شنی تنها ذرات جامد معلق (کدورت) را حذف می‌کند؛ باکتری‌ها، ویروس‌ها و آلاینده‌های شیمیایی محلول عبور کرده و آب حتماً نیازمند گندزدایی است.",
                    recommended_action="غیرقابل شرب بودن آب بدون فرآیند کلرزنی یا جوشاندن را تأیید کنید."
                ),
                state_snapshot=self.state.to_dict()
            )

        if prediction in ["removes_salt", "filters_solute", "حذف_نمک_محلول"]:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_FILTER_SOLUBLE_SUBSTANCES",
                    category=ErrorCategory.SCIENTIFIC_MISCONCEPTION,
                    title="تصور نادرست حذف مواد محلول با صافی فیزیکی",
                    description="نمک‌های حل‌شده و یون‌ها از منافذ ماسه عبور می‌کنند.",
                    scientific_rationale="فیلتراسیون فیزیکی فقط ذرات نامحلول را به دام می‌اندازد. برای جداسازی نمک حل‌شده نیازمند تقطیر یا اسمز معکوس هستیم.",
                    recommended_action="تأیید نمایید که نمک حل‌شده با صافی شنی جدا نمی‌شود."
                ),
                state_snapshot=self.state.to_dict()
            )

        if action.action_type in ["PREPARE_BOTTLE", "SETUP_COLUMN"]:
            return self._handle_prepare_bottle(action)

        if action.action_type in ["ADD_LAYER", "ARRANGE_LAYERS", "ARRANGE_FILTER_LAYERS", "ADD_COTTON", "ADD_SAND", "ADD_GRAVEL"]:
            return self._handle_add_layer(action)

        if action.action_type in ["POUR_DIRTY_WATER", "ADD_DIRTY_WATER"]:
            return self._handle_pour_dirty_water(action)

        if action.action_type in ["OBSERVE_FILTRATION", "FLOW_WATER"]:
            return self._handle_observe_filtration(action)

        if action.action_type in ["COMPARE_WATER", "ANALYZE_PURITY", "COMPARE_AND_EVALUATE"]:
            return self._handle_compare_water(action)

        if action.action_type == "SET_PARAMETERS":
            params = action.parameters or {}
            if "layers" in params and isinstance(params["layers"], list):
                self.filter_physics.layers = params["layers"]
            if "sand_thickness" in params:
                self.filter_physics.layer_thicknesses["sand"] = float(params["sand_thickness"])
            if "gravel_thickness" in params:
                self.filter_physics.layer_thicknesses["gravel"] = float(params["gravel_thickness"])

            eff = self.filter_physics.calculate_filtration_efficiency()
            return StepResult(
                success=True,
                step_index=self.state.current_step,
                is_step_completed=False,
                observations=["پارامترهای ضخامت و چینش لایه‌های صافی به‌روزرسانی شد."],
                measurements=eff,
                state_snapshot=self.state.to_dict()
            )

        return StepResult(
            success=False,
            step_index=self.state.current_step,
            is_step_completed=False,
            error=SimulationError(
                code="ERR_UNSUPPORTED_FILTRATION_ACTION",
                category=ErrorCategory.UNSUPPORTED_COMBINATION,
                title="عملیات فیلتراسیون نامعتبر است",
                description=f"عملیات «{action.action_type}» در این شبیه‌سازی تعریف نشده است.",
                scientific_rationale="آزمایش شامل آماده‌سازی بطری، چیدن لایه‌های پنبه، ماسه و شن، ریختن آب گل‌آلود و بررسی آب خروجی است.",
                recommended_action="یکی از مراحل تصفیه آب را انجام دهید."
            ),
            state_snapshot=self.state.to_dict()
        )

    def _handle_prepare_bottle(self, action: LabAction) -> StepResult:
        """گام ۱: آماده‌سازی بدنه بطری پلاستیکی به عنوان ستون صافی"""
        if "filter_column_bottle" not in self.state.workbench_tools:
            self.state.workbench_tools.append("filter_column_bottle")

        self.filter_physics.is_column_ready = True
        obs = "بطری پلاستیکی وارونه با دهانه باریک به عنوان بدنه ستون تصفیه روی پایه قرار گرفت."

        is_step_completed = False
        if self.state.current_step == 1:
            is_step_completed = True
            self.state.current_step = 2

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={"column_ready": True},
            state_snapshot=self.state.to_dict()
        )

    def _handle_add_layer(self, action: LabAction) -> StepResult:
        """گام ۲: قرار دادن لایه‌های پنبه، ماسه و شن"""
        if not self.filter_physics.is_column_ready:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_LAYERS_BEFORE_BOTTLE",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="ستون صافی هنوز آماده نیست",
                    description="ابتدا باید بدنه بطری صافی را روی میز مستقر کنید.",
                    scientific_rationale="لایه‌های فیلتر باید درون محفظه نگهدارنده چیده شوند.",
                    recommended_action="ابتدا بطری صافی را آماده نمایید."
                ),
                state_snapshot=self.state.to_dict()
            )

        if action.action_type in ["ARRANGE_LAYERS", "ARRANGE_FILTER_LAYERS"] or (action.parameters and "layers" in action.parameters):
            for t in ["cotton_layer", "fine_sand_layer", "gravel_layer"]:
                if t not in self.state.workbench_tools:
                    self.state.workbench_tools.append(t)

        # کنترل حضور ابزارها
        if not self._has_tool("cotton_layer"):
            return self._make_precondition_error("cotton_layer", "پنبه بهداشتی")
        if not self._has_tool("fine_sand_layer"):
            return self._make_precondition_error("fine_sand_layer", "ماسه بادی ریز")
        if not self._has_tool("gravel_layer"):
            return self._make_precondition_error("gravel_layer", "شن نخودی درشت")

        # کنترل چینش معکوس لایه‌ها
        if action.parameters and "layers" in action.parameters:
            custom_layers = action.parameters["layers"]
            if isinstance(custom_layers, list) and len(custom_layers) >= 2:
                if custom_layers[0] != "cotton" or (len(custom_layers) >= 3 and custom_layers[1] != "sand"):
                    return StepResult(
                        success=False,
                        step_index=self.state.current_step,
                        is_step_completed=False,
                        error=SimulationError(
                            code="ERR_INVERTED_FILTER_LAYERS",
                            category=ErrorCategory.ORDER_VIOLATION,
                            title="ترتیب لایه‌های صافی نادرست است",
                            description="لایه‌ها باید از دانه‌ریز به دانه‌درشت از پایین به بالا چیده شوند.",
                            scientific_rationale="شن درشت باید در بالا خاشاک را بگیرد و ماسه در وسط ذرات ریز را. چینش معکوس باعث مسدود شدن آنی صافی می‌شود.",
                            recommended_action="ابتدا پنبه، سپس ماسه و در نهایت شن را قرار دهید."
                        ),
                        state_snapshot=self.state.to_dict()
                    )

        # چیدن پیش‌فرض یا بر اساس پارامتر ورودی
        layer_type = action.parameters.get("layer_type") if action.parameters else None
        if layer_type and layer_type in LAYER_SPECS:
            if layer_type not in self.filter_physics.layers:
                self.filter_physics.layers.append(layer_type)
        else:
            # ترتیب استاندارد علمی
            self.filter_physics.layers = ["cotton", "sand", "gravel"]

        obs = "لایه‌های صافی با ترتیب علمی استقرار یافتند: پنبه در کف دهانه، ماسه ریز در میانه، و شن درشت در لایه بالایی."

        is_step_completed = False
        if self.state.current_step <= 2:
            is_step_completed = True
            self.state.current_step = 3

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={"layers": self.filter_physics.layers, "is_order_correct": self.filter_physics.is_order_correct()},
            state_snapshot=self.state.to_dict()
        )

    def _handle_pour_dirty_water(self, action: LabAction) -> StepResult:
        """گام ۳: ریختن آب گل‌آلود و استقرار ظرف جمع‌آوری"""
        if len(self.filter_physics.layers) == 0:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_WATER_BEFORE_LAYERS",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="صافی فاقد لایه‌های فیلترکننده است",
                    description="ریختن آب گل‌آلود در ستون بدون لایه‌های پنبه، ماسه و شن بدون تصفیه خارج می‌شود.",
                    scientific_rationale="جداسازی فیزیکی ذرات معلق مستلزم عبور آب از تخلخل‌های چندلایه است.",
                    recommended_action="ابتدا لایه‌های صافی را داخل بطری بچینید."
                ),
                state_snapshot=self.state.to_dict()
            )

        if not self._has_tool("dirty_water_flask"):
            return self._make_precondition_error("dirty_water_flask", "بشر آب کدر و گل‌آلود")
        if not self._has_tool("collection_beaker"):
            self.state.workbench_tools.append("collection_beaker")

        self.filter_physics.is_dirty_water_added = True
        obs = "آب کدر و گل‌آلود دارای ذرات معلق روی لایه بالایی صافی ریخته شد و ظرف تمیز در زیر خروجی قرار گرفت."

        is_step_completed = False
        if self.state.current_step <= 3:
            is_step_completed = True
            self.state.current_step = 4

        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=is_step_completed,
            observations=[obs],
            measurements={"inlet_turbidity_ntu": self.filter_physics.inlet_turbidity_ntu},
            state_snapshot=self.state.to_dict()
        )

    def _handle_observe_filtration(self, action: LabAction) -> StepResult:
        """گام ۴: مشاهده جریان آب و به دام افتادن ذرات در لایه‌ها"""
        if not self.filter_physics.is_dirty_water_added:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_OBSERVE_BEFORE_POURING",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="هنوز آبی وارد صافی نشده است",
                    description="برای مشاهده فیلتراسیون، باید ابتدا آب کدر را به ستون اضافه کنید.",
                    scientific_rationale="فرآیند فیلتراسیون با عبور ثقلی آب از خلل و فرج ذرات آغاز می‌شود.",
                    recommended_action="آب گل‌آلود را به صافی بیفزایید."
                ),
                state_snapshot=self.state.to_dict()
            )

        eff = self.filter_physics.calculate_filtration_efficiency()
        obs = (
            f"آب با نیروی جاذبه به سمت پایین جریان یافت: ذرات درشت و خاشاک در لایه شن به دام افتادند، "
            f"ذرات متوسط گل در روزنه‌های ماسه رسوب کردند و پنبه از خروج ذرات ماسه جلوگیری نمود. "
            f"آب زلال قطره‌قطره در ظرف پایین جمع‌آوری شد."
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
            measurements=eff,
            state_snapshot=self.state.to_dict()
        )

    def _handle_compare_water(self, action: LabAction) -> StepResult:
        """گام ۵: مقایسه آب ورودی و خروجی و اعلام اخطار بهداشتی"""
        if not self.filter_physics.is_dirty_water_added:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_COMPARE_WITHOUT_FILTRATION",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="آزمایش هنوز تکمیل نشده است",
                    description="آب خروجی هنوز تولید نشده است.",
                    scientific_rationale="مقایسه نیازمند نمونه آب اولیه و خروجی فیلتر است.",
                    recommended_action="مراحل قبل را تکمیل کنید."
                ),
                state_snapshot=self.state.to_dict()
            )

        eff = self.filter_physics.calculate_filtration_efficiency()
        self.state.is_completed = True

        obs = (
            f"مقایسه آب ورودی و خروجی: شفافیت آب تا {eff['clarity_improvement_percent']}٪ بهبود یافت "
            f"و کدورت از {eff['inlet_turbidity_ntu']} NTU به {eff['outlet_turbidity_ntu']} NTU کاهش یافت. "
            f"{eff['status_description']} "
            f"[{eff['safety_warning']}]"
        )

        return StepResult(
            success=True,
            step_index=5,
            is_step_completed=True,
            observations=[obs],
            measurements=eff,
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
                scientific_rationale="تصفیه آب نیازمند حضور متریال‌های فیلتر و ظروف مربوطه است.",
                recommended_action=f"«{tool_name}» را از قفسه انتخاب نمایید."
            ),
            state_snapshot=self.state.to_dict()
        )
