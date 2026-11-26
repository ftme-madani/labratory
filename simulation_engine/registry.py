from typing import Optional, Dict, Type
from .base import BaseExperimentEngine
from .acid_base.engine import AcidBaseSimulationEngine
from .mixture_separation.engine import MixtureSeparationEngine
from .simple_circuit.engine import SimpleCircuitSimulationEngine
from .vinegar_baking_soda.engine import VinegarBakingSodaEngine
from .simple_pendulum.engine import SimplePendulumEngine
from .plant_transport.engine import PlantWaterTransportEngine
from .density_column.engine import LiquidDensityColumnEngine
from .water_filtration.engine import WaterFiltrationEngine

ENGINE_REGISTRY: Dict[str, Type[BaseExperimentEngine]] = {
    # آزمایش‌های پایه قبلی
    "exp-acid-base": AcidBaseSimulationEngine,
    "acid-base-indicators": AcidBaseSimulationEngine,
    "exp-mixture-separation": MixtureSeparationEngine,
    "mixture-separation-sand-salt": MixtureSeparationEngine,
    "exp-simple-circuit": SimpleCircuitSimulationEngine,
    "simple-electric-circuit-ohm": SimpleCircuitSimulationEngine,

    # ۵ آزمایش جدید
    "exp-vinegar-baking-soda": VinegarBakingSodaEngine,
    "vinegar-baking-soda-reaction": VinegarBakingSodaEngine,

    "exp-simple-pendulum": SimplePendulumEngine,
    "simple-pendulum-motion": SimplePendulumEngine,

    "exp-plant-transport": PlantWaterTransportEngine,
    "plant-water-transport-celery": PlantWaterTransportEngine,

    "exp-density-column": LiquidDensityColumnEngine,
    "liquid-density-column": LiquidDensityColumnEngine,

    "exp-water-filtration": WaterFiltrationEngine,
    "water-filtration-column": WaterFiltrationEngine
}

def get_simulation_engine(experiment_id_or_slug: str) -> Optional[BaseExperimentEngine]:
    """
    کارخانه (Factory) تولید و دریافت نمونه موتور علمی متناسب با شناسه آزمایش.
    """
    engine_cls = ENGINE_REGISTRY.get(experiment_id_or_slug)
    if engine_cls:
        return engine_cls()
    return None
