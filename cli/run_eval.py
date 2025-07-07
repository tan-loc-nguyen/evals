"""
CLI command for running LLM evaluations.

This module provides the command-line interface for running evaluations
using the config-driven approach.
"""

import argparse
import asyncio
import logging
import sys

from evals.core.runner import EvaluationRunner
from evals.utils.logger import get_logger, set_log_level
from cli.utils import validate_config_file, print_success_message, print_error_message

logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Run LLM evaluations using config-driven approach",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
python -m cli.run_eval evals/configs/sample.yaml
python -m cli.run_eval evals/configs/tripPlanner/reference_free.yaml --output results.json
python -m cli.run_eval evals/configs/tripPlanner/comparison.yaml -o comparison_results.json
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

    return parser


async def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    if args.verbose:
        set_log_level(logging.DEBUG)

    # Validate config file
    config_path = validate_config_file(args.config_path)

    try:
        runner = EvaluationRunner(
            config_path=str(config_path),
            output_path=args.output_path
        )

        await runner.run()
        print_success_message("Evaluation completed successfully! 🎉")

    except KeyboardInterrupt:
        print_error_message("Evaluation interrupted by user")
        sys.exit(1)
    except (RuntimeError, ValueError, FileNotFoundError, OSError) as e:
        print_error_message(f"Evaluation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print_error_message(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
