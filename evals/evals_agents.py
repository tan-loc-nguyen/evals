import os
import csv
import time
import datetime
from dotenv import load_dotenv
from evals.utils.parsing import parse_user_prompt, get_system_prompt, get_prompt_id
from typing import Dict, List
from dataclasses import dataclass
import asyncio
from agents import Agent, Runner, TResponseInputItem, set_default_openai_key, RunResult
import numpy as np
import requests
import json
import argparse

load_dotenv()

set_default_openai_key(os.environ.get('OPENAI_API_KEY'))

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


def _create_agent(model: str, system_prompt: str) -> Agent:
  return Agent(
    name="TripPlanner",
    model=model,
    instructions=system_prompt
  )

def _create_judge(model: str) -> Agent:
  return Agent(
    name="TripPlanJudge",
    model=model,
    instructions=""""You are an eval auto grader for trip planning itineraries. Your job is to decide how good a trip plan is. Score between 0 and 10, where 10 is excellent. You are a harsh but fair grader.
Evaluate based on these criteria:
1. Relevance to user preferences (themes, pace, budget, dietary needs)
2. Feasibility of the itinerary (realistic timing, logistics)
3. Quality of recommendations (specific places, insider tips)
4. Completeness of the plan (all days covered, restaurants, alternates)
ALWAYS provide your response in this exact format:
SCORE: [0-10 number]
REASONING: [2-3 sentences explaining the score, focusing on strengths and key weaknesses]""",
  output_type=EvalResult
  )

# def generate_sample_inputs() -> List[UserPreference]:
#   return [
#     UserPreference(
#       hotel_city="Sydney, Australia",
#       hotel_name="Shangri-La Sydney",
#       check_in_date="2025-09-18",
#       check_out_date="2025-09-22",
#       number_of_nights=4,
#       number_of_adults=2,
#       has_children=False,
#       themes=["culture", "food", "harbour views"],
#       must_do_activities=["climb Sydney Harbour Bridge", "dinner in The Rocks"],
#       trip_pace="balanced",
#       activity_budget="Open Wallet",
#       food_style="Only the Best",
#       dietary_requirements=[],
#       proximity_preference="See the best within reach",
#       free_text="early risers, keen on fine-dining with views"
#     ),
#     UserPreference(
#       hotel_city="Sydney, Australia",
#       hotel_name="The Langham, Sydney",
#       check_in_date="2025-12-05",
#       check_out_date="2025-12-09",
#       number_of_nights=4,
#       number_of_adults=2,
#       has_children=True,
#       themes=["family", "beach", "exploration"],
#       must_do_activities=["Taronga Zoo visit", "ferry to Manly Beach"],
#       trip_pace="relaxed",
#       activity_budget="A Little Splash",
#       food_style="Casual Indulgence",
#       dietary_requirements=["nut allergy"],
#       proximity_preference="Keep it local",
#       free_text="travelling with a 6-year-old; need pram-friendly activities"
#     ),
#     UserPreference(
#       hotel_city="Sydney, Australia",
#       hotel_name="QT Sydney",
#       check_in_date="2026-02-14",
#       check_out_date="2026-02-17",
#       number_of_nights=3,
#       number_of_adults=2,
#       has_children=False,
#       themes=["shopping", "nightlife", "art"],
#       must_do_activities=["tour Art Gallery of NSW", "cocktails in Surry Hills"],
#       trip_pace="active",
#       activity_budget="Mix & Match",
#       food_style="Full-on Foodie",
#       dietary_requirements=["vegetarian"],
#       proximity_preference="Keen to get out and about",
#       free_text="couple's getaway; love quirky design and hidden bars"
#     ),
#     UserPreference(
#       hotel_city="Sydney, Australia",
#       hotel_name="Four Seasons Hotel Sydney",
#       check_in_date="2025-10-03",
#       check_out_date="2025-10-07",
#       number_of_nights=4,
#       number_of_adults=1,
#       has_children=False,
#       themes=["business", "wellness", "culture"],
#       must_do_activities=["morning walk in Royal Botanic Garden", "Sydney Opera House tour"],
#       trip_pace="balanced",
#       activity_budget="Keep It Simple",
#       food_style="Keep It Simple",
#       dietary_requirements=["gluten-free"],
#       proximity_preference="See the best within reach",
#       free_text="solo work trip; interested in wellness classes after meetings"
#     ),
#     UserPreference(
#       hotel_city="Sydney, Australia",
#       hotel_name="Ovolo Woolloomooloo",
#       check_in_date="2025-08-20",
#       check_out_date="2025-08-24",
#       number_of_nights=4,
#       number_of_adults=3,
#       has_children=False,
#       themes=["adventure", "food", "nightlife"],
#       must_do_activities=["kayaking in Sydney Harbour", "pub crawl in Newtown"],
#       trip_pace="active",
#       activity_budget="Mix & Match",
#       food_style="Casual Indulgence",
#       dietary_requirements=[],
#       proximity_preference="Keen to get out and about",
#       free_text="group of friends; want craft-beer spots and live music"
#     )
#   ]


async def generate_trip(agent: Agent ,user_prompt: str) -> RunResult:
  input_items: list[TResponseInputItem] = [{"content": user_prompt, "role": "user"}]

  response = await Runner.run(
    agent,
    input_items
  )

  return response


async def judge_response(evaluator: Agent, user_preference: UserPreference, response: str) -> RunResult:
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
  eval_response = await Runner.run(
    evaluator,
    judge_request
  )

  return eval_response


async def evaluation_process(user_prompt: str, user_inputs: Dict[str, str], agent_model: str, system_prompt: str, evaluator: Agent, run_id: int, prompt_id: str, NUMBER_OF_RUNS: int) -> FinalResult:
  """Process a single user preference and return the final result"""
  print(f"\n📍 Processing input {run_id + 1}/{NUMBER_OF_RUNS}")

  start_time = time.time()
  # Create a fresh agent for this run
  agent = _create_agent(agent_model, system_prompt)
  
  ## First call for the response + latency
  response = await generate_trip(agent, user_prompt)
  end_time = time.time()
  latency = end_time - start_time
  print(f'\n Finished generating {run_id + 1} in {latency:.2f}s')
  ## Second call for eval
  evalResult = await judge_response(evaluator, user_inputs, response.final_output)
  
  print(f"Run {run_id + 1}:\n- Latency: {latency:.2f}s\n- Evaluation: {evalResult.final_output.score}\n")
  
  # Create and return final result
  return FinalResult(
      prompt_id=prompt_id,
      run_no=run_id + 1,
      input=user_prompt,
      response=response.final_output,
      latency=latency,
      score=evalResult.final_output.score if hasattr(evalResult.final_output, 'score') else 0,
      feedback=evalResult.final_output.feedback if hasattr(evalResult.final_output, 'feedback') else str(evalResult.final_output),
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


def get_prompt_config(prompt_yaml_path: str) -> tuple[str, str, str, str]:
  user_prompt, user_inputs = parse_user_prompt(prompt_yaml_path)
  system_prompt = get_system_prompt(prompt_yaml_path)
  prompt_id = get_prompt_id(prompt_yaml_path)
  return prompt_id, system_prompt, user_prompt, user_inputs

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
    print(f"  Average Score: {sum(scores)/len(scores):.2f}/10")
    print(f"  Median: {np.median(scores)}")
    print(f"  Q1: {np.percentile(scores, 25)}")
    print(f"  Q3: {np.percentile(scores, 75)}")

  if latency:
    print(f"Latency:")
    print(f"  Average Latency: {sum(latency)/len(latency):.2f}s")
    print(f"  Median: {np.median(latency)}")
    print(f"  Q1: {np.percentile(latency, 25)}")
    print(f"  Q3: {np.percentile(latency, 75)}")

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

  evaluator = _create_judge(eval_model)
  print(f"⚙️  Running {prompt_id}...")

  # Create tasks for all user preferences to run concurrently
  # Each task will create its own fresh agent instance
  tasks = [
    evaluation_process(user_prompt, user_inputs, agent_model, system_prompt, evaluator, run_id, prompt_id, NUMBER_OF_RUNS)
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
