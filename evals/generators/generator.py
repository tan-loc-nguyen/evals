"""
Generators for LLM responses.
"""

from typing import Literal

from evals.constants.models import MODEL_NAMES
from evals.models.response_api import CandidateResponseAPI
from evals.models.base import GenerationTrace, LLMParams


async def generate_response(
    model: MODEL_NAMES,
    system_prompt: str,
    user_prompt: str,
    temperature: float | None = None,
    top_p: float | None = None,
    effort: Literal["low", "medium", "high"] | None = None,
    summary: Literal["auto", "concise", "detailed", "none"] | None = None
) -> GenerationTrace:
    """
    Generate a response from a model.
    """
    candidate = CandidateResponseAPI(
        model,
        LLMParams(
            temperature=temperature,
            top_p=top_p,
            effort=effort,
            summary=summary
        )
    )

    response = await candidate.generate(system_prompt, user_prompt)

    return response
