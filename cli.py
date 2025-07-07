#!/usr/bin/env python3
"""
Simple entry point for the LLM evaluation CLI.

Usage:
    python cli.py run-eval config.yaml
    python cli.py run-eval config.yaml --output results.json
"""

import asyncio
import sys
from pathlib import Path

from cli.main import main

# Add the project root to the path so we can import our modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


if __name__ == "__main__":
    asyncio.run(main())
