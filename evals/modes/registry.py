from typing import Dict, Type
from evals.modes.base import BaseMode
from evals.modes.reference_free import ReferenceFreeMode
from evals.modes.ground_truth import GroundTruthMode

# Mode registry for dynamic mode selection
MODE_REGISTRY: Dict[str, Type[BaseMode]] = {
  "reference_free": ReferenceFreeMode,
  # TODO: Add other modes as they're implemented
  "ground_truth": GroundTruthMode,
  # "comparison": ComparisonMode,
}