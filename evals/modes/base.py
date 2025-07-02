from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Literal

from evals.core.input_loaders import InputData
from evals.strategies.base import EvalTrace


class BaseMode(ABC):
  def __init__(self, input_data: InputData) -> None:
    self.input_data = input_data

  @abstractmethod
  async def run(self) -> List[EvalTrace]:
    ...
