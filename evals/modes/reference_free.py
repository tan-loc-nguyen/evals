from typing import List
from evals.modes.base import BaseMode
from evals.core.input_loaders import InputData
from evals.strategies.base import EvalTrace
from evals.strategies.rubric import RubricStrategy
from evals.models.response_api import JudgeResponseAPI
from evals.core.utils.logger import get_logger
from evals.models.base import GenerationTrace

# TODO: Refactor the response generation from this to isolate the responsibility of the mode to only judge the responses.
class ReferenceFreeMode(BaseMode):
  def __init__(self, input_data: InputData) -> None:
    super().__init__(input_data)
    self.logger = get_logger(__name__)

  async def run(self, to_be_judged_responses: List[GenerationTrace]) -> List[EvalTrace]:
    self.logger.info(f"Starting reference-free evaluation with {len(self.input_data.candidates)} candidates and {len(self.input_data.criteria)} criteria")

    judge = JudgeResponseAPI(
      model=self.input_data.judge.get('model'),
      temperature=self.input_data.judge.get('temperature', 1.0),
      top_p=self.input_data.judge.get('top_p', 1.0),
      effort=self.input_data.judge.get('effort', "medium")
    )

    judged_outputs: List[EvalTrace] = []
    for criterion in self.input_data.criteria:
      strategyInstance = RubricStrategy(
        name=criterion.name,
        judge=judge,
        question=criterion.question,
        weight=criterion.weight
      )

      # Extract response content for strategy evaluation
      candidate_responses = [trace.response for trace in to_be_judged_responses if isinstance(trace.response, str)]
      
      judge_trace = await strategyInstance.evaluate_async(candidate_responses)
      judged_outputs.append(judge_trace)

    return judged_outputs
