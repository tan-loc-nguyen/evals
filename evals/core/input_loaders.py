import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal

import yaml
from jinja2 import Template


@dataclass
class Prompt:
  prompt_id: str
  system_prompt: str
  user_prompt: str

@dataclass
class ExpectedOutput:
  quality: float | str  # Can be a score (out of ten) or string (e.g. "good", "bad", "mediocre")
  description: str | None = None
  response: str | None = None

@dataclass
class Criterion:
  type: Literal["rubric", "comparison", "similarity", "structure"]
  name: str
  question: str
  weight: float

@dataclass
class RawConfig:
  mode: Literal["reference_free", "ground_truth", "comparison"]
  structured: bool
  candidates: List[Dict[str, Any]]
  judge: Dict[str, Any]
  criteria: List[Criterion]
  prompt_file: str | List[str] | None = None
  expected_response_file: str | List[str] | None = None
  metadata: Dict[str, Any] | None = None


@dataclass
class InputData:
  prompt: Prompt
  mode: Literal["reference_free", "ground_truth", "comparison"]
  structured: bool
  candidates: List[Dict[str, Any]]
  judge: Dict[str, Any]
  criteria: List[Criterion]
  expected_response: List[ExpectedOutput] | None = None
  metadata: Dict[str, Any] | None = None

# -------------------------------------------------------------
# Prompt Loaders
# -------------------------------------------------------------
def extract_variables(template_str: str) -> List[str]:
  """Extract variables from a template string."""
  return re.findall(r'{{\s*(\w+)\s*}}', template_str)

def render_user_prompt(template_str: str, variables: Dict[str,str]) -> str:
  """Render user prompt string with input values for variables."""
  template = Template(template_str)
  return template.render(**variables)

def get_prompt_data(prompt_yaml_path: str) -> Prompt:
  with open(prompt_yaml_path, 'r', encoding='utf-8') as f:
    prompt_data = yaml.safe_load(f)

  variables = extract_variables(prompt_data['user_prompt'])

  """If prompt template doesn't need variable return the prompt"""
  if len(variables) == 0:
    return Prompt(
      prompt_id=prompt_data['prompt_id'],
      system_prompt=prompt_data['system_prompt'],
      user_prompt=prompt_data['user_prompt']
    )

  user_inputs = {}
  for variable in variables:
    user_inputs[variable] = input(f"Enter value for {variable}: ")

  return Prompt(
    prompt_id=prompt_data['prompt_id'],
    system_prompt=prompt_data['system_prompt'],
    user_prompt=render_user_prompt(prompt_data['user_prompt'], user_inputs)
  )

# -------------------------------------------------------------
# Expected Output Loaders
# -------------------------------------------------------------
def get_expected_response_data(expected_response_file: str) -> List[ExpectedOutput]:
  with open(expected_response_file, 'r', encoding='utf-8') as f:
    expected_response_data = yaml.safe_load(f)

  return [ExpectedOutput(**expected_response) for expected_response in expected_response_data['expected_responses']]

# -------------------------------------------------------------
# Config Loaders
# -------------------------------------------------------------

def load_config(config_yaml_path: str) -> RawConfig:
  with open(config_yaml_path, 'r', encoding='utf-8') as f:
    config_data = yaml.safe_load(f)
  
  # Convert criteria dictionaries to Criterion objects
  if 'criteria' in config_data:
    criteria_objects = []
    for criterion_dict in config_data['criteria']:
      criterion = Criterion(
        type=criterion_dict['type'],
        name=criterion_dict['name'],
        question=criterion_dict['question'],
        weight=criterion_dict['weight']
      )
      criteria_objects.append(criterion)
    config_data['criteria'] = criteria_objects
  
  return RawConfig(**config_data)

def get_config_data(config_yaml_path: str) -> InputData:
  config_data = load_config(config_yaml_path)

  prompt_data = None
  if config_data.prompt_file:
    if isinstance(config_data.prompt_file, str):
      prompt_data = get_prompt_data(config_data.prompt_file)
    elif isinstance(config_data.prompt_file, list): # TODO: Handle multiple prompts with the same config
      prompt_data = [get_prompt_data(prompt_file) for prompt_file in config_data.prompt_file]
  else:
    raise ValueError("Missing `prompt_file` in config.")

  expected_response_data = None
  if config_data.expected_response_file:
    if isinstance(config_data.expected_response_file, str):
      expected_response_data = get_expected_response_data(config_data.expected_response_file)
    elif isinstance(config_data.expected_response_file, list): # TODO: Handle multiple expected outputs with the same config
      expected_response_data = [get_expected_response_data(expected_response_file) for expected_response_file in config_data.expected_response_file]
  else:
    raise ValueError("Missing `expected_response_file` in config.")

  input_data = InputData(
    prompt=prompt_data,
    mode=config_data.mode,
    structured=config_data.structured,
    candidates=config_data.candidates,
    judge=config_data.judge,
    criteria=config_data.criteria,
    expected_response=expected_response_data,
    metadata=config_data.metadata
  )

  return input_data
