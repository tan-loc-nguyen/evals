"""
Model registry and constants for LLM evaluations.

This module provides model configurations and type definitions
for supported LLM models.
"""

from typing import Literal

MODELS_REGISTRY = {
  "gpt-4o": {
    "provider": "openai",
    "model": "gpt-4o",
  },
  "gpt-4o-mini": {
    "provider": "openai",
    "model": "gpt-4o-mini",
  },
  "gpt-4.5": {
    "provider": "openai",
    "model": "gpt-4.1",
  },
  "o3-mini": {
    "provider": "openai",
    "model": "o3-mini",
  },
  "o3": {
    "provider": "openai",
    "model": "o3",
  },
}

MODEL_NAMES = Literal[
  "gpt-4o", "gpt-4o-mini", "gpt-4.1", "o3-mini", "o3"
]
