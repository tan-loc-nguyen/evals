"""
Pure evaluation functions for LLM evaluations.

This module provides pure functions for different evaluation modes,
making the evaluation logic reusable across CLI and app contexts.
"""

from typing import List
from evals.core.input_loaders import InputData
from evals.strategies.base import EvalTrace
from evals.strategies.rubric import RubricStrategy
from evals.models.response_api import JudgeResponseAPI
from evals.utils.logger import get_logger
from evals.models.base import GenerationTrace, LLMParams

logger = get_logger(__name__)


async def reference_free_evaluation(
    input_data: InputData,
    to_be_judged_responses: List[GenerationTrace]
) -> List[EvalTrace]:
    """
    Pure function for reference-free evaluation.

    Args:
        input_data: Configuration and criteria for evaluation
        to_be_judged_responses: List of candidate responses to evaluate

    Returns:
        List of evaluation traces with scores and reasoning
    """
    logger.info("Starting reference-free evaluation with %d candidates and %d criteria",
                len(input_data.candidates), len(input_data.criteria))

    judge = JudgeResponseAPI(
        model=input_data.judge.get('model'),
        params=LLMParams(
            temperature=input_data.judge.get('temperature', 1.0),
            top_p=input_data.judge.get('top_p', 1.0),
            effort=input_data.judge.get('effort', "medium"),
            summary=input_data.judge.get('summary', "auto")
        )
    )

    judged_outputs: List[EvalTrace] = []
    for criterion in input_data.criteria:
        strategy_instance = RubricStrategy(
            name=criterion.name,
            judge=judge,
            question=criterion.question,
            weight=criterion.weight
        )

        # Extract response content for strategy evaluation
        candidate_responses = [trace.response for trace in to_be_judged_responses
                               if isinstance(trace.response, str)]

        judge_trace = await strategy_instance.evaluate_async(candidate_responses)
        judged_outputs.append(judge_trace)

    logger.info("Completed reference-free evaluation with %d traces",
                len(judged_outputs))
    return judged_outputs


async def ground_truth_evaluation(
    input_data: InputData,
    to_be_judged_responses: List[GenerationTrace]
) -> List[EvalTrace]:
    """
    Pure function for ground truth evaluation.

    Args:
        input_data: Configuration and criteria for evaluation (must include expected_response)
        to_be_judged_responses: List of candidate responses to evaluate

    Returns:
        List of evaluation traces comparing against ground truth
    """
    logger.info("Starting ground truth evaluation with %d candidates and %d criteria",
                len(input_data.candidates), len(input_data.criteria))

    if not input_data.expected_response:
        raise ValueError(
            "Ground truth evaluation requires expected_response in input_data")

    judge = JudgeResponseAPI(
        model=input_data.judge.get('model'),
        params=LLMParams(
            temperature=input_data.judge.get('temperature', 1.0),
            top_p=input_data.judge.get('top_p', 1.0),
            effort=input_data.judge.get('effort', "medium"),
            summary=input_data.judge.get('summary', "auto")
        )
    )

    judged_outputs: List[EvalTrace] = []

    for criterion in input_data.criteria:
        for expected_response in input_data.expected_response:
            strategy_instance = RubricStrategy(
                name=str(expected_response.quality),
                judge=judge,
                question=criterion.question,
                system_prompt=expected_response.response,
                weight=1.0,
            )

            candidate_responses = [trace.response for trace in to_be_judged_responses
                                   if isinstance(trace.response, str)]
            judge_trace = await strategy_instance.evaluate_async(candidate_responses)
            judged_outputs.append(judge_trace)

    logger.info("Completed ground truth evaluation with %d traces",
                len(judged_outputs))
    return judged_outputs


# Registry of evaluation functions for dynamic dispatch
EVALUATION_FUNCTIONS = {
    "reference_free": reference_free_evaluation,
    "ground_truth": ground_truth_evaluation,
}


async def run_evaluation(
    mode: str,
    input_data: InputData,
    to_be_judged_responses: List[GenerationTrace]
) -> List[EvalTrace]:
    """
    Run evaluation using the specified mode.

    Args:
        mode: Evaluation mode ("reference_free", "ground_truth", etc.)
        input_data: Configuration and criteria for evaluation
        to_be_judged_responses: List of candidate responses to evaluate

    Returns:
        List of evaluation traces

    Raises:
        ValueError: If mode is not supported
    """
    if mode not in EVALUATION_FUNCTIONS:
        available_modes = ", ".join(EVALUATION_FUNCTIONS.keys())
        raise ValueError(
            f"Unknown evaluation mode '{mode}'. Available modes: {available_modes}")

    evaluation_fn = EVALUATION_FUNCTIONS[mode]
    return await evaluation_fn(input_data, to_be_judged_responses)
