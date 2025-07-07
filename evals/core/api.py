"""
Main API interface for LLM evaluations.

This module provides the primary interface for external tools (CLI, Streamlit app, etc.)
to interact with the evaluation system. It exposes clean, composable functions that
can be used independently or together.
"""

from typing import List, Tuple, Optional
from evals.core.input_loaders import InputData, get_config_data
from evals.evaluators.evaluators import run_evaluation as run_eval_mode
from evals.models.base import GenerationTrace
from evals.strategies.base import EvalTrace
from evals.utils.logger import get_logger
from evals.generators.generator import generate_response

logger = get_logger(__name__)


async def run_evaluation(
    input_data: InputData,
    responses: List[GenerationTrace]
) -> List[EvalTrace]:
    """
    Run evaluation using the specified mode in input_data.

    Args:
        input_data: Configuration containing evaluation mode and criteria
        responses: List of candidate responses to evaluate

    Returns:
        List of evaluation traces with scores and reasoning
    """
    logger.info("Running evaluation in mode: %s", input_data.mode)

    results = await run_eval_mode(input_data.mode, input_data, responses)

    logger.info("Evaluation completed with %d traces", len(results))
    return results

# Convenience functions for specific evaluation modes
async def evaluate_reference_free(
    input_data: InputData,
    responses: Optional[List[GenerationTrace]] = None
) -> List[EvalTrace]:
    """
    Run reference-free evaluation.

    Args:
        input_data: Configuration (mode will be overridden to "reference_free")
        responses: Optional pre-generated responses. If None, will generate them.

    Returns:
        List of evaluation traces
    """
    # Override mode to ensure reference-free evaluation
    input_data.mode = "reference_free"

    if responses is None:
        responses = await generate_response(input_data)

    return await run_evaluation(input_data, responses)


async def evaluate_ground_truth(
    input_data: InputData,
    responses: Optional[List[GenerationTrace]] = None
) -> List[EvalTrace]:
    """
    Run ground truth evaluation.

    Args:
        input_data: Configuration (mode will be overridden to "ground_truth")
        responses: Optional pre-generated responses. If None, will generate them.

    Returns:
        List of evaluation traces
    """
    # Override mode to ensure ground truth evaluation
    input_data.mode = "ground_truth"

    if responses is None:
        responses = await generate_response(input_data)

    return await run_evaluation(input_data, responses)


# Export commonly used functions for easier imports
__all__ = [
    "generate_response",
    "run_evaluation",
    "evaluate_from_config",
    "evaluate",
    "evaluate_reference_free",
    "evaluate_ground_truth"
]
