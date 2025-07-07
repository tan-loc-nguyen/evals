"""
Base classes for LLM models.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Literal

from pydantic import BaseModel as PydanticBaseModel

from evals.constants.models import MODEL_NAMES


@dataclass
class LLMParams:
    """Parameters for the LLM."""
    temperature: float | None
    top_p: float | None
    effort: Literal["low", "medium", "high"] | None
    summary: Literal["auto", "concise", "detailed", "none"] | None


class EvalResult(PydanticBaseModel):
    """Structured verdict returned by a judge call."""
    scores: List[float]
    reasons: List[str]


@dataclass
class GenerationTrace:
    """Metadata captured for every LLM interaction."""
    model: MODEL_NAMES
    run_type: Literal["candidate", "judge"]
    system_prompt: str
    user_prompt: str
    # TODO: Add a more generic type for the response
    response: EvalResult | str | None
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
        params: LLMParams,
        **kwargs
    ) -> None:
        """Initialize the model."""
        self.model = model
        self.params = params
        self.kwargs = kwargs

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> GenerationTrace:
        """Generate a response from the model."""

    def __repr__(self) -> str:
        """Return a string representation of the model."""
        return f"{self.model} with params: {self.params}"
