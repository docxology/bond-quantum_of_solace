"""QUANTUM — special-agent mission software for Quantum of Solace (2008).

The pure domain core models the film's central threat — control of water and
desert logistics by a shadow cartel — with six deterministic, real-data
modules:

* :mod:`quantum_of_solace.hydrology` — desert water network: sources, routes,
  evaporation loss, shortest routing and maximum flow.
* :mod:`quantum_of_solace.water_cartel` — reservoir (dam) operation and the
  leverage a cartel exerts by withholding releases from downstream demand.
* :mod:`quantum_of_solace.cartel_graph` — multi-resource commodity control:
  market concentration (HHI), concentration ratios, and actor dominance.
* :mod:`quantum_of_solace.pricing` — linear-demand water scarcity pricing,
  point elasticity, and the monopoly solution with its deadweight loss.
* :mod:`quantum_of_solace.resilience` — aqueduct interdiction: per-route
  criticality, greedy worst-case attack sequences, and minimum cuts.
* :mod:`quantum_of_solace.shapley` — cooperative power over the commodity
  portfolio: exact Shapley values and the Banzhaf–Coleman index.

:mod:`quantum_of_solace.analysis` composes all six into one canonical,
deterministic assessment, and :mod:`quantum_of_solace.mission` adapts that
assessment to the frozen ``bond_api`` ``MissionProvider`` protocol so the
orchestrator can discover and drive the film. The six domain modules are
deliberately infrastructure-free and importable without ``bond_api``.
"""

from quantum_of_solace.cartel_graph import CommodityCartelGraph, concentration_band
from quantum_of_solace.hydrology import Aquifer, HydrologicalNetwork, Route
from quantum_of_solace.pricing import market_outcome, scarcity_impact
from quantum_of_solace.resilience import minimum_cut, resilience_index, single_route_criticality
from quantum_of_solace.shapley import banzhaf_power, shapley_value
from quantum_of_solace.water_cartel import Dam, cartel_leverage, run_reservoir

__all__ = [
    "Aquifer",
    "CommodityCartelGraph",
    "Dam",
    "HydrologicalNetwork",
    "Route",
    "banzhaf_power",
    "cartel_leverage",
    "concentration_band",
    "market_outcome",
    "minimum_cut",
    "resilience_index",
    "run_reservoir",
    "scarcity_impact",
    "shapley_value",
    "single_route_criticality",
]
