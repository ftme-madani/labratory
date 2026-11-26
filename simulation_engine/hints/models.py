from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from ..schema import ErrorCategory, SimulationError

@dataclass
class TieredHint:
    error_code: str
    category: ErrorCategory
    experiment_id: str
    step_index: int
    level1_question: str      # سوال تفکری سقراطی
    level2_clue: str          # سرنخ مفهومی و ابزاری
    level3_explanation: str   # توضیح کامل علمی و اقدام اصلاحی

    def get_content_for_level(self, level: int) -> str:
        if level == 1:
            return self.level1_question
        elif level == 2:
            return self.level2_clue
        else:
            return self.level3_explanation
