from typing import List, Dict, Any
from evals.core.input_loaders import InputData
from evals.models.response_api import CandidateResponseAPI
from evals.models.base import GenerationTrace
from evals.core.utils.logger import get_logger


class ResponseGenerator:
  """
  Service responsible for generating responses from candidates.
  Isolated from evaluation logic to follow single responsibility principle.
  """
  
  def __init__(self, candidates: List[Dict[str, Any]]):
    self.logger = get_logger(__name__)
    self.candidates = candidates
  
  async def generate_responses(self, system_prompt: str, user_prompt: str) -> List[GenerationTrace]:
    """
    Generate responses from all candidates in the input data.
    
    Args:
        input_data: Input data containing candidates and prompts
        
    Returns:
        List of EvalTrace objects containing generated responses
    """
    self.logger.info(f"Generating responses for {len(self.candidates)} candidates")
    
    generated_responses: List[GenerationTrace] = []
    
    for candidate in self.candidates:
      response_api_candidate = CandidateResponseAPI(
        model=candidate.get('model'),
        temperature=candidate.get('temperature', 1.0),
        top_p=candidate.get('top_p', 1.0),
        effort=candidate.get('effort', "medium")
      )
      
      response = await response_api_candidate.generate(
        system_prompt, 
        user_prompt
      )
      generated_responses.append(response)
    
    self.logger.info(f"Successfully generated {len(generated_responses)} responses")
    return generated_responses