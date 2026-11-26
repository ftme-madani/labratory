from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Any, Dict, List

class ErrorCategory(str, Enum):
    WRONG_TOOL = "WRONG_TOOL"
    WRONG_REAGENT = "WRONG_REAGENT"
    MISSING_PRECONDITION = "MISSING_PRECONDITION"
    ORDER_VIOLATION = "ORDER_VIOLATION"
    UNSUPPORTED_COMBINATION = "UNSUPPORTED_COMBINATION"
    HAZARDOUS_ACTION = "HAZARDOUS_ACTION"
    SCIENTIFIC_MISCONCEPTION = "SCIENTIFIC_MISCONCEPTION"

@dataclass
class SimulationError:
    code: str
    category: ErrorCategory
    title: str
    description: str
    scientific_rationale: str
    recommended_action: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['category'] = self.category.value
        return d

@dataclass
class LabAction:
    action_type: str  # e.g., 'ADD_TOOL', 'REMOVE_TOOL', 'DIP_INDICATOR', 'MIX', 'HEAT', 'RESET'
    source_id: str
    target_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReagentProperties:
    id: str
    name: str
    ph: float
    color_hex: str
    phase: str = "liquid"
    concentration_molar: float = 0.1
    temperature_celsius: float = 25.0

    @property
    def is_acid(self) -> bool:
        return self.ph < 6.8

    @property
    def is_base(self) -> bool:
        return self.ph > 7.2

    @property
    def is_neutral(self) -> bool:
        return 6.8 <= self.ph <= 7.2

@dataclass
class StepResult:
    success: bool
    step_index: int
    is_step_completed: bool
    error: Optional[SimulationError] = None
    observations: List[str] = field(default_factory=list)
    measurements: Dict[str, Any] = field(default_factory=dict)
    state_snapshot: Dict[str, Any] = field(default_factory=dict)
    is_terminal: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "step_index": self.step_index,
            "is_step_completed": self.is_step_completed,
            "error": self.error.to_dict() if self.error else None,
            "observations": self.observations,
            "measurements": self.measurements,
            "state_snapshot": self.state_snapshot,
            "is_terminal": self.is_terminal
        }

@dataclass
class SimulationState:
    experiment_id: str
    current_step: int = 1
    total_steps: int = 3
    workbench_tools: List[str] = field(default_factory=list)
    active_solutions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    recorded_observations: List[str] = field(default_factory=list)
    action_history: List[Dict[str, Any]] = field(default_factory=list)
    is_completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
