"""
Utility functions for CLI operations.

This module provides common utility functions used across CLI commands.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

from evals.utils.logger import get_logger

logger = get_logger(__name__)


def validate_file_exists(file_path: str, file_type: str = "file") -> Path:
    """
    Validate that a file exists.

    Args:
        file_path: Path to the file to validate
        file_type: Type of file for error messages

    Returns:
        Path object if file exists

    Raises:
        SystemExit: If file doesn't exist
    """
    path = Path(file_path)

    if not path.exists():
        logger.error("%s not found: %s", file_type.capitalize(), path)
        sys.exit(1)

    return path


def validate_config_file(config_path: str) -> Path:
    """
    Validate that a configuration file exists and is a YAML file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Path object if validation passes

    Raises:
        SystemExit: If validation fails
    """
    path = validate_file_exists(config_path, "config file")

    if path.suffix.lower() not in ['.yaml', '.yml']:
        logger.error("Config file must be YAML format: %s", path)
        sys.exit(1)

    return path


def format_results_summary(results: List[Dict[str, Any]]) -> str:
    """
    Format evaluation results into a summary string.

    Args:
        results: List of evaluation results

    Returns:
        Formatted summary string
    """
    if not results:
        return "No results to display."

    summary_lines = [
        "=" * 60,
        "🎯 EVALUATION SUMMARY",
        "=" * 60,
        f"Total traces: {len(results)}",
    ]

    # Group by model
    models = {}
    for result in results:
        model = result.get('model', 'unknown')
        if model not in models:
            models[model] = []
        models[model].append(result)

    for model, model_results in models.items():
        summary_lines.append(f"\n🤖 Model: {model}")
        summary_lines.append(f"   Traces: {len(model_results)}")

        # Show average latency if available
        latencies = [r.get('latency')
                     for r in model_results if r.get('latency')]
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            summary_lines.append(f"   Avg Latency: {avg_latency:.2f}s")

    summary_lines.append("=" * 60)

    return "\n".join(summary_lines)


def print_success_message(message: str) -> None:
    """Print a success message with emoji."""
    print(f"✅ {message}")


def print_error_message(message: str) -> None:
    """Print an error message with emoji."""
    print(f"❌ {message}")


def print_info_message(message: str) -> None:
    """Print an info message with emoji."""
    print(f"ℹ️  {message}")


def print_warning_message(message: str) -> None:
    """Print a warning message with emoji."""
    print(f"⚠️  {message}")
