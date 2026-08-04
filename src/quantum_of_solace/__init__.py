"""QUANTUM — special-agent mission software for Quantum of Solace (2008).

The pure domain core models the film's central threat — control of water and
desert logistics by a shadow cartel — with three deterministic, real-data
modules:

* :mod:`quantum_of_solace.hydrology` — desert water network: sources, routes,
  evaporation loss, shortest routing and maximum flow.
* :mod:`quantum_of_solace.water_cartel` — reservoir (dam) operation and the
  leverage a cartel exerts by withholding releases from downstream demand.
* :mod:`quantum_of_solace.cartel_graph` — multi-resource commodity control:
  market concentration (HHI), concentration ratios, and actor dominance.

:mod:`quantum_of_solace.mission` adapts this core to the frozen ``bond_api``
``MissionProvider`` protocol so the orchestrator can discover and drive the
film. The three domain modules are deliberately infrastructure-free and
importable without ``bond_api``.
"""

from quantum_of_solace.cartel_graph import CommodityCartelGraph
from quantum_of_solace.hydrology import Aquifer, HydrologicalNetwork, Route
from quantum_of_solace.water_cartel import Dam, run_reservoir, cartel_leverage

__all__ = [
    "Aquifer",
    "CommodityCartelGraph",
    "Dam",
    "HydrologicalNetwork",
    "Route",
    "cartel_leverage",
    "run_reservoir",
]
