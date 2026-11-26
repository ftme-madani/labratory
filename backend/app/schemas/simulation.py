from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ActionExecuteRequest(BaseModel):
    action_type: str
    source_id: str
    target_id: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)

class SimulationErrorSchema(BaseModel):
    code: str
    category: str
    title: str
    description: str
    scientific_rationale: str
    recommended_action: str

class ActionExecuteResponse(BaseModel):
    success: bool
    step_index: int
    is_step_completed: bool
    error: Optional[SimulationErrorSchema] = None
    observations: List[str] = Field(default_factory=list)
    measurements: Dict[str, Any] = Field(default_factory=dict)
    state_snapshot: Dict[str, Any] = Field(default_factory=dict)
    is_terminal: bool = False

class HintRequest(BaseModel):
    step_index: int
    error_code: str
    forced_level: Optional[int] = None

class HintResponse(BaseModel):
    error_code: str
    category: str
    level: int
    can_escalate: bool
    content: str
    scientific_rationale: str

class StartAttemptResponse(BaseModel):
    attempt_id: str
    experiment_id: int
    experiment_slug: str
    experiment_title: str
    total_steps: int
    current_step: int
    status: str

class FinishAttemptResponse(BaseModel):
    attempt_id: str
    status: str
    score: float
    total_steps: int
    steps_completed: int
    observations_count: int
