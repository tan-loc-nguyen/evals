import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from time import perf_counter
from pathlib import Path
from typing import Dict, List, Type

from evals.core.input_loaders import InputData, get_config_data
from evals.core.utils.logger import get_logger, set_log_level
from evals.models.base import GenerationTrace
from evals.strategies.base import EvalTrace
from evals.modes.base import BaseMode
from evals.modes.registry import MODE_REGISTRY
from evals.core.response_generator import ResponseGenerator

logger = get_logger(__name__)

class EvaluationRunner:
  """Central orchestrator for LLM evaluations."""
  
  def __init__(self, config_path: str, output_path: str | None = None):
    self.config_path = Path(config_path)
    self.output_path = Path(output_path) if output_path else f"results/{self.config_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    self.input_data: InputData | None = None
    self.responses: List[GenerationTrace] = []
    self.results: List[EvalTrace] = []
  
  def load_config(self) -> None:
    """Load and validate configuration from YAML file."""
    try:
      logger.info(f"Loading config from: {self.config_path}")
      self.input_data = get_config_data(str(self.config_path))
      logger.info(f"Config loaded successfully. Mode: {self.input_data.mode}")
    except Exception as e:
      logger.error(f"Failed to load config: {e}")
      raise RuntimeError(f"Configuration loading failed: {e}")
  
  def select_mode(self) -> BaseMode:
    """Dynamically select and instantiate the appropriate mode."""
    if not self.input_data:
      raise RuntimeError("Config must be loaded before selecting mode")
    
    mode_name = self.input_data.mode
    if mode_name not in MODE_REGISTRY:
      available_modes = ", ".join(MODE_REGISTRY.keys())
      raise ValueError(f"Unknown mode '{mode_name}'. Available modes: {available_modes}")
    
    mode_class = MODE_REGISTRY[mode_name]
    logger.info(f"Selected mode: {mode_name}")
    return mode_class(self.input_data)
  
  async def generate_responses(self) -> List[GenerationTrace]:
    """Generate responses for the candidates."""
    response_generator = ResponseGenerator(self.input_data.candidates)
    system_prompt = self.input_data.prompt.system_prompt
    user_prompt = self.input_data.prompt.user_prompt
    return await response_generator.generate_responses(system_prompt, user_prompt)
  
  async def run_evaluation(self) -> List[EvalTrace]:
    """Execute the evaluation using the selected mode."""
    mode = self.select_mode()
    
    logger.info("Starting evaluation...")
    start_time = perf_counter()
    
    try:
      self.results = await mode.run(self.responses)
      end_time = perf_counter()
      duration = end_time - start_time
      
      logger.info(f"Evaluation completed in {duration:.2f}s")
      logger.info(f"Generated {len(self.results)} evaluation traces")
      
      return self.results
      
    except Exception as e:
      logger.error(f"Evaluation failed: {e}")
      raise RuntimeError(f"Evaluation execution failed: {e}")
  
  def format_results(self) -> Dict:
    """Format evaluation results for output."""
    if not self.input_data or not self.results:
      return {}
    
    formatted_results = {
      "evaluation_summary": {
        "config_file": str(self.config_path),
        "mode": self.input_data.mode,
        "prompt_id": self.input_data.prompt.prompt_id,
        "timestamp": datetime.now().isoformat(),
        "total_traces": len(self.results),
        "candidates": [
          {
            "model": candidate["model"],
            "temperature": candidate.get("temperature", 1.0),
            "top_p": candidate.get("top_p", 1.0),
            "effort": candidate.get("effort", "medium")
          }
          for candidate in self.input_data.candidates
        ],
        "judge": {
          "model": self.input_data.judge["model"],
          "temperature": self.input_data.judge.get("temperature", 1.0),
          "top_p": self.input_data.judge.get("top_p", 1.0),
          "effort": self.input_data.judge.get("effort", "medium")
        },
        "criteria": [
          {
            "name": criterion.name,
            "type": criterion.type,
            "weight": criterion.weight,
            "question": criterion.question
          }
          for criterion in self.input_data.criteria
        ]
      },
      "evaluation_results": []
    }
    
    # Process each trace (one per criterion)
    for trace in self.results:
      result_entry = {
        "criterion": getattr(trace, 'criterion_name', 'unknown'),
        "model": trace.model,
        "run_type": trace.run_type,
        "latency": trace.latency,
        "system_prompt": trace.system_prompt,
        "user_prompt": trace.user_prompt,
        "response": trace.response,
        "params": trace.params,
        "metadata": trace.metadata
      }
      formatted_results["evaluation_results"].append(result_entry)
    
    return formatted_results
  
  def pretty_print_results(self) -> None:
    """Pretty print evaluation results to console."""
    if not self.results:
      print("No results to display.")
      return
    
    print("\n" + "="*80)
    print("🎯 EVALUATION RESULTS")
    print("="*80)
    
    if self.input_data:
      print(f"📋 Config: {self.config_path.name}")
      print(f"🔧 Mode: {self.input_data.mode}")
      print(f"💬 Prompt: {self.input_data.prompt.prompt_id}")
      print(f"🤖 Candidates: {[c['model'] for c in self.input_data.candidates]}")
      print(f"⚖️  Judge: {self.input_data.judge['model']}")
      print(f"📊 Criteria: {len(self.input_data.criteria)} evaluation criteria")
    
    print(f"\n📈 Generated {len(self.results)} evaluation traces")
    
    # Display results per criterion
    for i, trace in enumerate(self.results, 1):
      print(f"\n📋 Trace {i}:")
      print(f"   Model: {trace.model}")
      print(f"   Run Type: {trace.run_type}")
      print(f"   Question: {trace.question}")
      if trace.latency:
        print(f"   Latency: {trace.latency:.2f}s")
      
      # Show response if it's an EvalResult
      if hasattr(trace.response, 'scores') and hasattr(trace.response, 'reasons'):
        print(f"   Scores: {trace.response.scores}")
        print(f"   Reasons: {trace.response.reasons}")
      elif isinstance(trace.response, str):
        preview = trace.response[:100] + "..." if len(trace.response) > 100 else trace.response
        print(f"   Response: {preview}")
    
    print("\n" + "="*80)
  
  def save_results(self) -> None:
    """Save evaluation results to file."""
    if not self.output_path:
      return
    
    formatted_results = self.format_results()
    
    try:
      with open(self.output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_results, f, indent=2, ensure_ascii=False, default=str)
      
      logger.info(f"Results saved to: {self.output_path}")
    except Exception as e:
      logger.error(f"Failed to save results: {e}")
      raise RuntimeError(f"Could not save results to {self.output_path}: {e}")
  
  async def run(self) -> List[EvalTrace]:
    """Main execution flow."""
    self.load_config()
    self.responses = await self.generate_responses()
    self.results = await self.run_evaluation()
    
    # Output results
    self.pretty_print_results()
    
    if self.output_path:
      self.save_results()
    
    return self.results


async def main():
  """Main entry point with CLI argument parsing."""
  parser = argparse.ArgumentParser(
    description="Run LLM evaluations using config-driven approach",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
python -m evals.core.runner evals/configs/sample.yaml
python -m evals.core.runner evals/configs/tripPlanner/reference_free.yaml --output results.json
python -m evals.core.runner evals/configs/tripPlanner/comparison.yaml -o comparison_results.json
    """
  )
  
  parser.add_argument(
    "config_path",
    help="Path to the YAML configuration file"
  )
  
  parser.add_argument(
    "-o", "--output",
    dest="output_path",
    help="Optional path to save evaluation results (JSON format)"
  )
  
  parser.add_argument(
    "-v", "--verbose",
    action="store_true",
    help="Enable verbose logging"
  )
  
  args = parser.parse_args()
  
  if args.verbose:
    set_log_level(logging.DEBUG)
  
  # Validate config file exists
  config_path = Path(args.config_path)
  if not config_path.exists():
    logger.error(f"Config file not found: {config_path}")
    sys.exit(1)
  
  if not config_path.suffix.lower() in ['.yaml', '.yml']:
    logger.error(f"Config file must be YAML format: {config_path}")
    sys.exit(1)
  
  try:
    runner = EvaluationRunner(
      config_path=str(config_path),
      output_path=args.output_path
    )

    await runner.run()
    logger.info("Evaluation completed successfully! 🎉")
    
  except KeyboardInterrupt:
    logger.info("Evaluation interrupted by user")
    sys.exit(1)
  except Exception as e:
    logger.error(f"Evaluation failed: {e}")
    sys.exit(1)


if __name__ == "__main__":
  asyncio.run(main())
