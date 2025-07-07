"""
Response API implementations for LLM evaluations.

This module provides API implementations for generating responses
from candidate models and judge models.
"""

import os
from time import perf_counter
from typing import Literal

from dotenv import load_dotenv
from openai import AsyncOpenAI

from evals.constants.models import MODEL_NAMES
from evals.utils.logger import get_logger
from evals.models.base import BaseModel, EvalResult, GenerationTrace, LLMParams

load_dotenv()
API_KEY = os.environ.get('OPENAI_API_KEY')

logger = get_logger(__name__)


class CandidateResponseAPI(BaseModel):
    """OpenAI Response API for candidate models."""

    def __init__(
        self,
        model: MODEL_NAMES,
        params: LLMParams,
        **kwargs
    ) -> None:
        super().__init__(model, params, **kwargs)
        # Handle client initialization errors
        if not API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        try:
            self.client = AsyncOpenAI(api_key=API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise RuntimeError(f"Could not initialize OpenAI client: {e}")

    async def generate(self, system_prompt: str, user_prompt: str) -> GenerationTrace:
        try:
            start_time = perf_counter()

            response = await self.client.responses.create(
                model=self.model,
                instructions=system_prompt,
                input=user_prompt,
                temperature=self.params.temperature,
                top_p=self.params.top_p,
                reasoning={
                    "effort": self.params.effort,
                    "summary": self.params.summary
                }
            )

            end_time = perf_counter()
            latency = end_time - start_time

        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise RuntimeError(f"Could not generate response: {e}")

        return GenerationTrace(
            model=self.model,
            run_type="candidate",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response=response.output_text,
            latency=latency,
            params={
                "temperature": self.params.temperature,
                "top_p": self.params.top_p,
                "effort": self.params.effort,
                "summary": self.params.summary
            },
            metadata=None
        )


class JudgeResponseAPI(BaseModel):
    """OpenAI Response API for judge models."""

    def __init__(
        self,
        model: MODEL_NAMES,
        params: LLMParams,
        **kwargs
    ) -> None:
        super().__init__(model, params, **kwargs)
        # Handle client initialization errors
        if not API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        try:
            self.client = AsyncOpenAI(api_key=API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise RuntimeError(f"Could not initialize OpenAI client: {e}")

    async def generate(self, system_prompt: str, user_prompt: str) -> GenerationTrace:
        try:
            response = await self.client.responses.parse(
                model=self.model,
                instructions=system_prompt,
                input=user_prompt,
                temperature=self.params.temperature,
                top_p=self.params.top_p,
                reasoning={
                    "effort": self.params.effort,
                    "summary": self.params.summary
                },
                text_format=EvalResult
            )

        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise RuntimeError(f"Could not generate response: {e}")

        return GenerationTrace(
            model=self.model,
            run_type="judge",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response=response.output_parsed,
            latency=None,
            params={
                "temperature": self.params.temperature,
                "top_p": self.params.top_p,
                "effort": self.params.effort,
                "summary": self.params.summary
            },
            metadata=None
        )
