import os
from time import perf_counter
from dotenv import load_dotenv
from typing import Literal
from openai import AsyncOpenAI
from evals.models.base import BaseModel, GenerationTrace, EvalResult
from evals.constants.models import MODEL_NAMES
from evals.core.utils.logger import get_logger

load_dotenv()
API_KEY = os.environ.get('OPENAI_API_KEY')

logger = get_logger(__name__)

class CandidateResponseAPI(BaseModel):
  def __init__(
    self,
    model: MODEL_NAMES,
    temperature: float = 1.0,
    top_p: float = 1.0,
    effort: Literal["low", "medium", "high"] = "medium",
    **kwargs
  ) -> None:
    super().__init__(model, temperature, top_p, effort, **kwargs)
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
        temperature=self.temperature,
        top_p=self.top_p,
        reasoning={
          "effort": self.effort
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
        "temperature": self.temperature,
        "top_p": self.top_p,
        "effort": self.effort
      },
      metadata=None
    )


class JudgeResponseAPI(BaseModel):
  def __init__(
    self,
    model: MODEL_NAMES,
    temperature: float = 1.0,
    top_p: float = 1.0,
    effort: Literal["low", "medium", "high"] = "medium",
    **kwargs
  ) -> None:
    super().__init__(model, temperature, top_p, effort, **kwargs)
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
        temperature=self.temperature,
        top_p=self.top_p,
        reasoning={
          "effort": self.effort
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
        "temperature": self.temperature,
        "top_p": self.top_p,
        "effort": self.effort
      },
      metadata=None
    )