"""
Base classes for evaluation strategies.

This module provides the base classes for implementing different evaluation
strategies like rubric-based, comparison-based, etc.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from evals.models.base import GenerationTrace
from evals.models.response_api import JudgeResponseAPI


@dataclass
class EvalTrace(GenerationTrace):
    """
    Unified container returned by every strategy.
    TODO: Create strategies to use this class besides rubric (Future)
    """
    name: str
    question: str


class BaseStrategy(ABC):
    """Abstract base class for evaluation strategies."""

    def __init__(
        self,
        name: str,
        judge: JudgeResponseAPI | None = None,
    ) -> None:
        """Initialize the strategy with a name and optional judge."""
        self.name = name
        self.judge = judge

    @abstractmethod
    async def evaluate_async(
        self,
        to_be_judged_responses: List[str],
        expected_response: str | None = None,
    ) -> EvalTrace:
        """Evaluate responses asynchronously and return evaluation trace."""
