"""
Main CLI entry point for the LLM evaluation system.

This module provides the main command-line interface with subcommands
for different evaluation operations.
"""

import argparse
import asyncio
import sys

from evals.utils.logger import get_logger

logger = get_logger(__name__)


def create_main_parser() -> argparse.ArgumentParser:
    """Create the main parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="LLM Evaluation System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available commands:
  run-eval    Run an evaluation using a configuration file
  
Examples:
  python -m cli.main run-eval evals/configs/sample.yaml
  python -m cli.main run-eval evals/configs/tripPlanner/reference_free.yaml --output results.json
    """
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True
    )

    # run-eval subcommand
    run_eval_parser = subparsers.add_parser(
        "run-eval",
        help="Run an evaluation using a configuration file"
    )

    run_eval_parser.add_argument(
        "config_path",
        help="Path to the YAML configuration file"
    )

    run_eval_parser.add_argument(
        "-o", "--output",
        dest="output_path",
        help="Optional path to save evaluation results (JSON format)"
    )

    run_eval_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser


async def handle_run_eval(args) -> None:
    """Handle the run-eval command."""
    import logging
    from evals.core.runner import EvaluationRunner
    from evals.utils.logger import set_log_level
    from cli.utils import validate_config_file, print_success_message, print_error_message

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


async def main():
    """Main entry point for the CLI."""
    parser = create_main_parser()
    args = parser.parse_args()

    try:
        if args.command == "run-eval":
            await handle_run_eval(args)
        else:
            logger.error("Unknown command: %s", args.command)
            sys.exit(1)

    except Exception as e:
        logger.error("CLI error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
