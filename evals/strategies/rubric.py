"""
Rubric-based evaluation strategy.

This module provides the RubricStrategy class for evaluating responses
based on specific rubric criteria.
"""

from typing import List

from evals.models.base import GenerationTrace, BaseModel
from evals.strategies.base import BaseStrategy, EvalTrace


class RubricStrategy(BaseStrategy):
    """
    Scores a single rubric criterion (e.g., pace, budget, proximity).

    One instance is created *per* item in the YAML `criteria:` list, all
    sharing the same `BaseModel` injected by the Mode.

    Parameters
    ----------
    name : str
        Short identifier, e.g. `"pace"`.
    judge : BaseModel
        LLM-as-a-judge implementation (JudgeResponseAPI).
    question : str
        Natural-language rubric prompt.
    weight : float
        Optional weight (not used inside the strategy but stored for Mode aggregation).
    """

    def __init__(
        self,
        name: str,
        judge: BaseModel,
        question: str,
        system_prompt: str | None = None,
        weight: float = 1.0,
    ) -> None:
        super().__init__(name=name, judge=judge)
        self.question = question
        self.weight = weight

        self.system_prompt = system_prompt or self._default_system_prompt()

    def _default_system_prompt(self) -> str:
        return (
            "You are an eval auto grader for trip planning itineraries. "
            "Your job is to decide how good a trip plan is based on a question "
            "given in the user prompt. Score between 0 and 10, where 10 is excellent. "
            "You are a harsh but fair grader.\n"
            "ALWAYS provide your response in this exact format:\n"
            "scores: [0.0-10.0 float]\n"
            "reasons: [2-3 sentences explaining the score, focusing on strengths "
            "and key weaknesses for each candidate]\n\n"
            "Example where there is only one candidate:\n"
            "scores: [8.0]\n"
            "reasons: [\"The trip plan is well-structured and covers all the user's "
            "preferences. The itinerary is realistic and feasible, with a good balance "
            "of activities and rest days. The recommendations are specific and relevant "
            "to the user's needs.\"]\n\n"
            "Example where there are multiple candidates:\n"
            "scores: [8.0, 7.0, 9.0]\n"
            "reasons: [\"The trip plan is well-structured and covers all the user's "
            "preferences. The itinerary is realistic and feasible, with a good balance "
            "of activities and rest days. The recommendations are specific and relevant "
            "to the user's needs.\", \"The trip plan is well-structured and covers all "
            "the user's preferences. The itinerary is realistic and feasible, with a "
            "good balance of activities and rest days. The recommendations are specific "
            "and relevant to the user's needs.\", \"The trip plan is well-structured "
            "and covers all the user's preferences. The itinerary is realistic and "
            "feasible, with a good balance of activities and rest days. The "
            "recommendations are specific and relevant to the user's needs.\"]"
        )

    def _build_judge_prompt(
        self, to_be_judged_responses: List[str], expected_response: str | None = None
    ) -> str:
        candidates_text = ''.join(
            f"CANDIDATE {i+1}: {candidate} \n"
            for i, candidate in enumerate(to_be_judged_responses, 1)
        )
        return f"""
        QUESTION:{self.question}
        {candidates_text}
        {f"REFERENCE: {expected_response or 'No reference provided'}"}
        """

    async def evaluate_async(
        self,
        to_be_judged_responses: List[str],
        expected_response: str | None = None,
    ) -> EvalTrace:
        """
        Delegate grading to the injected `judge`.  We simply pass along:
        • rubric question
        • list of candidate outputs
        • optional reference output (unused in reference-free but harmless)
        """
        if self.judge is None:
            raise RuntimeError("RubricStrategy got no Judge instance")

        judge_prompt = self._build_judge_prompt(
            to_be_judged_responses, expected_response)

        response: GenerationTrace = await self.judge.generate(
            system_prompt=self.system_prompt,
            user_prompt=judge_prompt,
        )

        judge_trace = EvalTrace(
            self.judge.model,
            "judge",
            self.system_prompt,
            judge_prompt,
            response.response,
            response.latency,
            response.params,
            response.metadata,
            self.name,
            self.question,
        )

        return judge_trace
