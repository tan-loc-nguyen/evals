import os
import csv
import time
import datetime
import yaml
from dotenv import load_dotenv
from core.input_loaders import get_prompt_data, extract_variables, render_user_prompt
from typing import Dict, List
from dataclasses import dataclass
import asyncio
from openai import AsyncOpenAI
import numpy as np

load_dotenv()

client = AsyncOpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

UserPreference = Dict[str, str]

@dataclass
class EvalResult:
  score: float
  feedback: str

@dataclass
class FinalResult(EvalResult):
  prompt_id: str
  run_no: int
  input: str
  response: str
  latency: float
  created_at: str


async def generate_trip(model: str, system_prompt: str, user_prompt: str) -> tuple[str, float]:
  start_time = time.time()

  response = await client.responses.create(
    model=model,
    instructions = system_prompt,
    input=user_prompt,
    reasoning={
      'effort': 'medium'
    }
  )

  end_time = time.time()
  latency = end_time - start_time
  
  return response.output_text, latency


async def judge_response(model: str, user_preference: UserPreference, response: str) -> EvalResult:
  judge_instructions = """You are an eval auto grader for trip planning itineraries. Your job is to decide how good a trip plan is. Score between 0 and 10, where 10 is excellent. You are a harsh but fair grader.
Evaluate based on these criteria:
1. Relevance to user preferences (themes, pace, budget, dietary needs)
2. Feasibility of the itinerary (realistic timing, logistics)
3. Quality of recommendations (specific places, insider tips)
4. Completeness of the plan (all days covered, restaurants, alternates)
ALWAYS provide your response in this exact format:
SCORE: [0-10 number]
REASONING: [2-3 sentences explaining the score, focusing on strengths and key weaknesses]"""

  judge_request = f"""Please evaluate this trip plan:

Trip Requirements:
- Destination: {user_preference['hotel_city']}
- Duration: {user_preference['number_of_nights']} nights
- Number of Adults: {user_preference['number_of_adults']}
- Check-in Date: {user_preference['check_in_date']}
- Check-out Date: {user_preference['check_out_date']}
- Hotel Name: {user_preference['hotel_name']}
{f"- Themes: {user_preference['themes_text']}" if 'themes_text' in user_preference else ''}
{f"- Must-do: {user_preference['must_do_text']}" if 'must_do_text' in user_preference else ''}
{f"- Pace: {user_preference['trip_pace']}" if 'trip_pace' in user_preference else ''}
{f"- Budget: {user_preference['activity_budget']}" if 'activity_budget' in user_preference else ''}
{f"- Food Style: {user_preference['food_style']}" if 'food_style' in user_preference else ''}
{f"- Dietary: {user_preference['dietary_text']}" if 'dietary_text' in user_preference else ''}
{f"- Proximity: {user_preference['proximity_preference']}" if 'proximity_preference' in user_preference else ''}
{f"- Notes: {user_preference['free_text']}" if 'free_text' in user_preference else ''}

Trip Plan to Evaluate:
{response}

Rubric if corresponding user preferences are provided in the response:
- Pace: Is the overall pace of the itinerary consistent with the user's preference?
- Proximity: Do the suggested activities match the user's proximity preference?
- Budget: Are the suggested activities appropriate for the stated budget?
- Theme: Does the output reflect the selected trip themes?
- Must-do Activities: Does the output include the user's must-do activities?
- Food Style: Are the food suggestions aligned with the user's food style?
- Dietary Requirements: Are the food suggestions aligned with the user's dietary requirements?
- Free Text: Does the output include the user's preferences in the additional notes?
"""

  eval_response = await client.responses.create(
    model=model,
    instructions = judge_instructions,
    input = judge_request
  )

  # Parse the response to extract score and reasoning
  eval_content = eval_response.output_text
  try:
    lines = eval_content.split('\n')
    score_line = [line for line in lines if line.startswith('SCORE:')][0]
    reasoning_line = [line for line in lines if line.startswith('REASONING:')][0]
    
    score = float(score_line.split(':')[1].strip())
    feedback = reasoning_line.split(':', 1)[1].strip()
    
    return EvalResult(score=score, feedback=feedback)
  except (IndexError, ValueError) as e:
    print(f"Error parsing evaluation response: {e}")
    return EvalResult(score=0.0, feedback=eval_content)


async def evaluation_process(user_prompt: str, user_inputs: Dict[str, str], agent_model: str, eval_model: str, system_prompt: str, run_id: int, prompt_id: str, NUMBER_OF_RUNS: int) -> FinalResult:
  """Process a single user preference and return the final result"""
  print(f"\n📍 Processing input {run_id + 1}/{NUMBER_OF_RUNS}")

  ## First call for the response + latency
  response, latency = await generate_trip(agent_model, system_prompt, user_prompt)
  print(f'\n Finished generating {run_id + 1} in {latency:.2f}s')
  ## Second call for eval
  evalResult = await judge_response(eval_model, user_inputs, response)
  
  print(f"Run {run_id + 1}:\n- Latency: {latency:.2f}s\n- Evaluation: {evalResult.score}\n")
  
  # Create and return final result
  return FinalResult(
      prompt_id=prompt_id,
      run_no=run_id + 1,
      input=user_prompt,
      response=response,
      latency=latency,
      score=evalResult.score,
      feedback=evalResult.feedback,
      created_at=datetime.datetime.now().isoformat()
  )


def save_to_csv(results: List[FinalResult]) -> str:
  """Save evaluation results to CSV file"""
  timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
  os.makedirs("./results", exist_ok=True)
  filename = f"./results/{results[0].prompt_id}_{timestamp}.csv"
  
  fieldnames = [
    'prompt_id', 'run_no', 'score', 'latency', 'feedback', 'created_at',
    'input', 'response'
  ]
  
  with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for result in results:
      writer.writerow({
        'prompt_id': result.prompt_id,
        'run_no': result.run_no,
        'score': result.score,
        'latency': round(result.latency, 2),
        'feedback': result.feedback,
        'created_at': result.created_at,
        'input': result.input,
        'response': result.response
      })
  
  return filename


def get_prompt_config(prompt_yaml_path: str) -> tuple[str, str, str, Dict[str, str]]:
  # Load the prompt data and handle variable collection efficiently
  with open(prompt_yaml_path, 'r', encoding='utf-8') as f:
    prompt_data = yaml.safe_load(f)
  
  variables = extract_variables(prompt_data['user_prompt'])
  user_inputs = {}
  
  # Collect user inputs if variables exist
  if len(variables) > 0:
    for variable in variables:
      user_inputs[variable] = input(f"Enter value for {variable}: ")
    
    # Render the user prompt with the collected inputs
    rendered_user_prompt = render_user_prompt(prompt_data['user_prompt'], user_inputs)
  else:
    rendered_user_prompt = prompt_data['user_prompt']
  
  return prompt_data['prompt_id'], prompt_data['system_prompt'], rendered_user_prompt, user_inputs

def print_summary(results: List[FinalResult], prompt_id: str):
  """Print evaluation summary"""
  scores = [r.score for r in results]
  latency = [r.latency for r in results]
  
  print("\n" + "="*60)
  print("📊 EVALUATION SUMMARY")
  print("="*60)
  
  print(f"Detailed Structured [{prompt_id}]:")
  if scores:
    print(f"Score:")
    print(f"  Average Score: {sum(scores)/len(scores):.1f}/10")
    print(f"  Median: {np.median(scores):.1f}")
    print(f"  Q1: {np.percentile(scores, 25):.1f}")
    print(f"  Q3: {np.percentile(scores, 75):.1f}")

  if latency:
    print(f"Latency:")
    print(f"  Average Latency: {sum(latency)/len(latency):.1f}s")
    print(f"  Median: {np.median(latency):.1f}")
    print(f"  Q1: {np.percentile(latency, 25):.1f}")
    print(f"  Q3: {np.percentile(latency, 75):.1f}")

  print(f"\nTotal Evaluations: {len(results)}")


async def main():
  if not os.environ.get('OPENAI_API_KEY'):
    print('Error: API key not found')
    return

  # Store user_prompt, system_prompt, and the run metadata
  # Change here to test different config
  # Add more config in _load_configs following structure in README
  agent_model = "o3"
  eval_model = "o3-mini"
  NUMBER_OF_RUNS = 50

  config_file_name = input("Enter the config file name: ")

  prompt_id, system_prompt, user_prompt, user_inputs = get_prompt_config(f"evals/prompts/tripPlanner/{config_file_name}.yaml")

  print(f"⚙️  Running {prompt_id}...")

  # Create tasks for all evaluations to run concurrently
  tasks = [
    evaluation_process(user_prompt, user_inputs, agent_model, eval_model, system_prompt, run_id, prompt_id, NUMBER_OF_RUNS)
    for run_id in range(NUMBER_OF_RUNS)
  ]

  # Run all tasks concurrently
  results = await asyncio.gather(*tasks)

  print(f"\n✅ Completed all {len(results)} evaluations")

  # Save results to CSV
  csv_filename = save_to_csv(results)
  print(f"📊 Results saved to: {csv_filename}")

  print_summary(results, prompt_id)

if __name__ == "__main__":
  asyncio.run(main())
