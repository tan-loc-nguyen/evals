"""
CLI-focused evaluation runner for LLM evaluations.

This module provides the EvaluationRunner class that handles CLI-specific
concerns like file I/O, formatting, and console output while using the
core API for the actual evaluation logic.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from evals.core.api import evaluate_from_config
from evals.core.input_loaders import InputData
from evals.models.base import GenerationTrace
from evals.strategies.base import EvalTrace
from evals.utils.logger import get_logger

logger = get_logger(__name__)


class EvaluationRunner:
    """CLI-focused evaluation runner with file I/O and formatting capabilities."""

    def __init__(self, config_path: str, output_path: str | None = None):
        self.config_path = Path(config_path)
        self.output_path = (Path(output_path) if output_path else
                            f"results/{self.config_path.stem}_"
                            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        self.input_data: InputData | None = None
        self.responses: List[GenerationTrace] = []
        self.results: List[EvalTrace] = []

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
            print(
                f"🤖 Candidates: {[c['model'] for c in self.input_data.candidates]}")
            print(f"⚖️  Judge: {self.input_data.judge['model']}")
            print(
                f"📊 Criteria: {len(self.input_data.criteria)} evaluation criteria")

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
                preview = (trace.response[:100] + "..." if len(trace.response) > 100
                           else trace.response)
                print(f"   Response: {preview}")

        print("\n" + "="*80)

    def save_results(self) -> None:
        """Save evaluation results to file."""
        if not self.output_path:
            return

        formatted_results = self.format_results()

        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(formatted_results, f, indent=2,
                          ensure_ascii=False, default=str)

            logger.info("Results saved to: %s", self.output_path)
        except Exception as e:
            logger.error("Failed to save results: %s", e)
            raise RuntimeError(
                f"Could not save results to {self.output_path}: {e}") from e

    async def run(self) -> List[EvalTrace]:
        """Main execution flow for CLI."""
        logger.info("Starting evaluation from config: %s", self.config_path)

        try:
            # Use the core API for evaluation
            self.input_data, self.responses, self.results = await evaluate_from_config(str(self.config_path))

            # CLI-specific output and formatting
            self.pretty_print_results()

            if self.output_path:
                self.save_results()

            logger.info("Evaluation completed successfully")
            return self.results

        except Exception as e:
            logger.error("Evaluation failed: %s", e)
            raise RuntimeError(f"Evaluation execution failed: {e}") from e


# CLI functionality has been moved to cli/run_eval.py
# This module now contains only the core evaluation logic
