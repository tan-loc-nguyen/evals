from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import asyncio

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
  def __init__(
    self,
    name: str,
    judge: JudgeResponseAPI | None = None,
  ) -> None:
    self.name = name
    self.judge = judge

  @abstractmethod
  async def evaluate_async(
    self,
    to_be_judged_responses: List[str],
    reference_output: str | None = None,
  ) -> EvalTrace:
    ...
