from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Literal

from pydantic import BaseModel as PydanticBaseModel

from evals.constants.models import MODEL_NAMES


@dataclass
class LLMParams:
  temperature: float
  top_p: float
  effort: Literal["low", "medium", "high"]

class EvalResult(PydanticBaseModel):
  """Structured verdict returned by a judge call."""
  scores: List[float]
  reasons: List[str]

@dataclass(slots=True)
class GenerationTrace:
  """Metadata captured for every LLM interaction."""
  model: MODEL_NAMES
  run_type: Literal["candidate", "judge"]
  system_prompt: str
  user_prompt: str
  response: EvalResult | str | None # TODO: Add a more generic type for the response
  latency: float | None
  params: LLMParams | None
  metadata: Dict[str, Any] | None


class BaseModel(ABC):
  """
  Base class for all models.
  """
  def __init__(
    self,
    model: MODEL_NAMES,
    temperature: float = 1.0,
    top_p: float = 1.0,
    effort: Literal["low", "medium", "high"] = "medium",
    **kwargs
  ) -> None:
    self.model = model
    self.temperature = temperature
    self.top_p = top_p
    self.effort = effort
    self.kwargs = kwargs

  @abstractmethod
  async def generate(self, system_prompt: str, user_prompt: str) -> GenerationTrace:
    ...
