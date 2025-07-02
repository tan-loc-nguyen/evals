from typing import Literal

MODELS_REGISTRY = {
  "gpt-4o": {
    "name": "gpt-4o",
    "provider": "openai",
    "model": "gpt-4o",
    "temperature": 1.0,
    "top_p": 1.0,
    "effort": "medium",
  },
  "gpt-4o-mini": {
    "name": "gpt-4o-mini",
    "provider": "openai",
    "model": "gpt-4o-mini",
    "temperature": 1.0,
    "top_p": 1.0,
    "effort": "medium",
  },
  "gpt-4.5": {
    "name": "gpt-4.5",
    "provider": "openai",
    "model": "gpt-4.5",
    "temperature": 1.0,
    "top_p": 1.0,
    "effort": "medium",
  },
  "o3-mini": {
    "name": "o3-mini",
    "provider": "openai",
    "model": "o3-mini",
    "temperature": 1.0,
    "top_p": 1.0,
    "effort": "medium",
  },
  "o3": {
    "name": "o3",
    "provider": "openai",
    "model": "o3",
    "temperature": 1.0,
    "top_p": 1.0,
    "effort": "medium",
  },
}

MODEL_NAMES = Literal[
  "gpt-4o", "gpt-4o-mini", "gpt-4.5", "o3-mini", "o3"
]