"""
Scientific Simulation Engine for Virtual School Science Laboratory.
Independent, deterministic, rule-based scientific modeling.
"""

from .schema import (
    SimulationState,
    LabAction,
    StepResult,
    ErrorCategory,
    SimulationError,
    ReagentProperties
)
from .base import BaseExperimentEngine
from .acid_base.engine import AcidBaseSimulationEngine
from .mixture_separation.engine import MixtureSeparationEngine
from .simple_circuit.engine import SimpleCircuitSimulationEngine
from .vinegar_baking_soda.engine import VinegarBakingSodaEngine
from .simple_pendulum.engine import SimplePendulumEngine
from .plant_transport.engine import PlantWaterTransportEngine
from .density_column.engine import LiquidDensityColumnEngine
from .water_filtration.engine import WaterFiltrationEngine
from .registry import get_simulation_engine, ENGINE_REGISTRY

__all__ = [
    "SimulationState",
    "LabAction",
    "StepResult",
    "ErrorCategory",
    "SimulationError",
    "ReagentProperties",
    "BaseExperimentEngine",
    "AcidBaseSimulationEngine",
    "MixtureSeparationEngine",
    "SimpleCircuitSimulationEngine",
    "VinegarBakingSodaEngine",
    "SimplePendulumEngine",
    "PlantWaterTransportEngine",
    "LiquidDensityColumnEngine",
    "WaterFiltrationEngine",
    "get_simulation_engine",
    "ENGINE_REGISTRY"
]
