from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .schema import (
    SimulationState,
    LabAction,
    StepResult,
    SimulationError,
    ErrorCategory
)

class BaseExperimentEngine(ABC):
    """
    کلاس پایه مجرد برای موتورهای شبیه‌سازی آزمایش‌های علمی.
    کاملاً ایزوله از UI و بدون وابستگی به فریم‌ورک‌های وب.
    """
    def __init__(self, experiment_id: str, total_steps: int):
        self.experiment_id = experiment_id
        self.total_steps = total_steps
        self.state = self._create_initial_state()

    @abstractmethod
    def _create_initial_state(self) -> SimulationState:
        """ایجاد وضعیت اولیه پاک و استاندارد برای آزمایش"""
        pass

    def reset(self) -> SimulationState:
        """بازنشانی کامل وضعیت آزمایش به حالت اولیه"""
        self.state = self._create_initial_state()
        return self.state

    def add_tool_to_workbench(self, tool_id: str) -> StepResult:
        """انتقال یک ابزار یا ظرف از قفسه به روی میز کار"""
        if not tool_id or not isinstance(tool_id, str):
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_INVALID_TOOL_ID",
                    category=ErrorCategory.WRONG_TOOL,
                    title="شناسه ابزار نامعتبر است",
                    description="شناسه ابزار ارسال‌شده خالی یا غیراستاندارد است.",
                    scientific_rationale="هر ابزار آزمایشگاهی دارای هویت مشخص فیزیکی است.",
                    recommended_action="ابزار را از فهرست مجاز قفسه انتخاب نمایید."
                ),
                state_snapshot=self.state.to_dict()
            )

        if tool_id in self.state.workbench_tools:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_TOOL_ALREADY_ON_WORKBENCH",
                    category=ErrorCategory.MISSING_PRECONDITION,
                    title="ابزار از قبل روی میز کار قرار دارد",
                    description=f"ابزار «{tool_id}» پیش‌تر به میز آزمایشگاه منتقل شده است.",
                    scientific_rationale="از شلوغ کردن غیرضروری میز کار آزمایشگاه خودداری کنید.",
                    recommended_action="از همان ابزار موجود روی میز برای گام جاری استفاده کنید."
                ),
                state_snapshot=self.state.to_dict()
            )

        self.state.workbench_tools.append(tool_id)
        return StepResult(
            success=True,
            step_index=self.state.current_step,
            is_step_completed=False,
            observations=[f"ابزار «{tool_id}» با موفقیت روی میز کار قرار گرفت."],
            state_snapshot=self.state.to_dict()
        )

    def remove_tool_from_workbench(self, tool_id: str) -> StepResult:
        """برداشتن ابزار از روی میز کار"""
        if tool_id in self.state.workbench_tools:
            self.state.workbench_tools.remove(tool_id)
            return StepResult(
                success=True,
                step_index=self.state.current_step,
                is_step_completed=False,
                observations=[f"ابزار «{tool_id}» از روی میز برداشته شد."],
                state_snapshot=self.state.to_dict()
            )
        return StepResult(
            success=False,
            step_index=self.state.current_step,
            is_step_completed=False,
            error=SimulationError(
                code="ERR_TOOL_NOT_ON_WORKBENCH",
                category=ErrorCategory.WRONG_TOOL,
                title="ابزار روی میز موجود نیست",
                description=f"ابزار «{tool_id}» روی میز کار آزمایشگاه قرار ندارد.",
                scientific_rationale="ابزاری که روی میز کار نیست نمی‌تواند برداشته شود.",
                recommended_action="ابتدا ابزار را به میز اضافه کنید."
            ),
            state_snapshot=self.state.to_dict()
        )

    def execute_action(self, action: LabAction) -> StepResult:
        """
        پردازش یک کنش آزمایشگاهی با اعتبارسنجی قطعی ورودی و حالت
        """
        # 1. کنترل امنیتی ورودی نامعتبر (Graceful fallback against crash)
        if not action or not action.action_type:
            return StepResult(
                success=False,
                step_index=self.state.current_step,
                is_step_completed=False,
                error=SimulationError(
                    code="ERR_MALFORMED_ACTION",
                    category=ErrorCategory.UNSUPPORTED_COMBINATION,
                    title="قالب کنش نامعتبر است",
                    description="درخواست ارسال‌شده فاقد نوع عملیات (action_type) معتبر است.",
                    scientific_rationale="کنش‌های آزمایشگاهی باید دارای عملگر و اهداف مشخص فیزیکی باشند.",
                    recommended_action="پارامترهای درخواست را اصلاح کنید."
                ),
                state_snapshot=self.state.to_dict()
            )

        # 2. مدیریت کنش بازنشانی
        if action.action_type == "RESET":
            self.reset()
            return StepResult(
                success=True,
                step_index=1,
                is_step_completed=False,
                observations=["محیط آزمایشگاه به وضعیت تمیز اولیه بازنشانی شد."],
                state_snapshot=self.state.to_dict()
            )

        # 3. مدیریت افزودن یا حذف ابزار
        if action.action_type == "ADD_TOOL":
            return self.add_tool_to_workbench(action.source_id)

        if action.action_type == "REMOVE_TOOL":
            return self.remove_tool_from_workbench(action.source_id)

        # 4. ارجاع به منطق علمی اختصاصی هر آزمایش
        result = self._process_scientific_action(action)

        # لاگ کردن تاریخچه کنش
        self.state.action_history.append({
            "action_type": action.action_type,
            "source_id": action.source_id,
            "target_id": action.target_id,
            "success": result.success,
            "is_step_completed": result.is_step_completed
        })

        if result.success and result.observations:
            for obs in result.observations:
                if obs not in self.state.recorded_observations:
                    self.state.recorded_observations.append(obs)

        return result

    @abstractmethod
    def _process_scientific_action(self, action: LabAction) -> StepResult:
        """منطق پردازش علمی اختصاصی قوانین هر آزمایش"""
        pass
