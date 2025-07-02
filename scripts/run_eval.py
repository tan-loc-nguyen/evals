#!/usr/bin/env python3
"""
Command-line entry point for running LLM evaluations.
This script provides a convenient way to run evaluations from anywhere.
"""

import sys
from pathlib import Path

# Add the evals directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "evals"))

# Import and run the main function from core.runner
from evals.core.runner import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main()) 