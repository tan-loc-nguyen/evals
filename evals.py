import os
import csv
import json
import time
import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
import asyncio
from agents import Agent, Runner, TResponseInputItem, trace, set_default_openai_key, RunResult

set_default_openai_key(os.environ.get('OPENAI_API_KEY'))

@dataclass
class UserPreference:
  hotel_city: str
  hotel_name: str
  check_in_date: str
  check_out_date: str
  number_of_nights: int
  number_of_adults: int
  has_children: bool
  themes: List[str]
  must_do_activities: List[str]
  trip_pace: str
  activity_budget: str
  food_style: str
  dietary_requirements: List[str]
  proximity_preference: str
  free_text: str 

@dataclass
class EvalResult:
  score: float
  feedback: str

@dataclass
class FinalResult(EvalResult):
  id: str # id of config (system/user prompt)
  type: str # "Free-text" | "Structured"
  run_no: int
  input: str
  response: str
  latency: float
  created_at: str

def _load_configs() -> Dict[str, Dict[str, str]]:
  """Load the two prompt configurations"""
  # Config A - Detailed structured approach
  config_a = {
    "id": "config_a",
    "type": "free-form",
    "system_prompt": "Your task is to create a detailed daily travel itinerary.",
    "user_prompt": """I'm going to {hotel_city} for {number_of_nights} nights between {check_in_date} and {check_out_date}, with {number_of_adults} adult(s){children_clause}.
I'm staying at {hotel_name}.

I'd like specific activities. Eg. "Cultural Immersion Day" is not specific, but "Visit the Eiffel Tower" is specific.

For some of the activities, include an insider tip. Eg. for the Royal Botanic Garden in Sydney, you might add:
"Insider tip: Walk all the way out to Mrs Macquarie's Chair for the best unobstructed view of the Opera House and Harbour Bridge together - perfect for photos without the tour groups."
No need to add a tip for every activity, perhaps for about a third of them. And, only if you have a genuinely useful tip.

I'd like a specific restaurant recommendation for each evening. (Do not add an insider tip for restaurants, cafés, bars, or any other meal recommendations)

Most activities can have a fairly short description. For the highlight activities though, include a longer description. A few sentences is fine.

Make sure each activity includes the name of the place. This might be a landmark, a place, or an establishment. It's what I'd search for to find it on Google Maps, Google Places, etc.

Can you also make sure that each activity has a start time?

Trip Pace: {trip_pace}
Themes: {themes_text}
Must-do Activities: {must_do_text}
Activity Budget: {activity_budget}
Food Style: {food_style}
Dietary Requirements: {dietary_text}
Proximity Preference: {proximity_preference}
Additional Notes: {free_text}

So remember:
- A great overall trip, that considers my preferences but isn't totally dominated by them
- Specific activities on each day
- Insider tips for activities, but not for restaurants, cafés, bars, or any other meal recommendations
- Longer descriptions for highlight activities
- A specific restaurant recommendation for each evening
- The place name or location for each activity (it might be the name of an establishment, a landmark, or a place - the thing I'd search for on Google Maps, Google Places, etc.)

Please also suggest two additional "alternate days", that I might like to swap in, if I don't like one of the existing days. They should follow the same format as the main days."""
    }
        
    # Config B - Structured role-based approach
  config_b = {
    "id": "config_b", 
    "type": "free-form",
    "system_prompt": """Role : You are an imaginative yet practical travel-planner.
Task : Draft a full multi-day itinerary that
        • reflects ≥⅔ of the traveller's selected themes,
        • respects "must-do" items,
        • matches the requested pace & budget,
        • accounts for dietary needs **and excludes any activities in conflict with them (e.g. wine-tasting for alcohol-free)**,
        • clusters activities sensibly,
        • provides a specific restaurant each evening,
        • adds insider tips to ≈⅓ of non-meal activities,
        • assigns a start-time to every activity,
        • offers two fully-formed alternate days.
Highlight activities should have slightly longer descriptions (2-4 sentences).
Example insider tip  
Walk all the way out to **Mrs Macquarie's Chair** for the best unobstructed view of the Opera House and Harbour Bridge together — perfect for photos without the tour groups.
Format: free text grouped by day headings, en-GB spelling.""",
        "user_prompt": """## Trip Basics
Destination : {hotel_city}
Hotel       : {hotel_name}
Dates       : {check_in_date} → {check_out_date}  ({number_of_nights} nights)
Travellers  : {number_of_adults} adult(s){children_clause}

### Themes (≈70 % of trip)
{themes_list}

### Must-do Activities
{must_do_list}

### Trip Pace
{trip_pace}

### Activity Budget
{activity_budget}

### Food Style
{food_style}

### Dietary Requirements
{dietary_list}

### Proximity Preference
{proximity_preference}

### Additional Notes
{free_text}"""
  }

  return {"config_a": config_a, "config_b": config_b}


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

def generate_sample_inputs() -> List[UserPreference]:
  return [
    UserPreference(
      hotel_city="Sydney, Australia",
      hotel_name="Shangri-La Sydney",
      check_in_date="2025-09-18",
      check_out_date="2025-09-22",
      number_of_nights=4,
      number_of_adults=2,
      has_children=False,
      themes=["culture", "food", "harbour views"],
      must_do_activities=["climb Sydney Harbour Bridge", "dinner in The Rocks"],
      trip_pace="balanced",
      activity_budget="Open Wallet",
      food_style="Only the Best",
      dietary_requirements=[],
      proximity_preference="See the best within reach",
      free_text="early risers, keen on fine-dining with views"
    ),
    UserPreference(
      hotel_city="Sydney, Australia",
      hotel_name="The Langham, Sydney",
      check_in_date="2025-12-05",
      check_out_date="2025-12-09",
      number_of_nights=4,
      number_of_adults=2,
      has_children=True,
      themes=["family", "beach", "exploration"],
      must_do_activities=["Taronga Zoo visit", "ferry to Manly Beach"],
      trip_pace="relaxed",
      activity_budget="A Little Splash",
      food_style="Casual Indulgence",
      dietary_requirements=["nut allergy"],
      proximity_preference="Keep it local",
      free_text="travelling with a 6-year-old; need pram-friendly activities"
    ),
    UserPreference(
      hotel_city="Sydney, Australia",
      hotel_name="QT Sydney",
      check_in_date="2026-02-14",
      check_out_date="2026-02-17",
      number_of_nights=3,
      number_of_adults=2,
      has_children=False,
      themes=["shopping", "nightlife", "art"],
      must_do_activities=["tour Art Gallery of NSW", "cocktails in Surry Hills"],
      trip_pace="active",
      activity_budget="Mix & Match",
      food_style="Full-on Foodie",
      dietary_requirements=["vegetarian"],
      proximity_preference="Keen to get out and about",
      free_text="couple’s getaway; love quirky design and hidden bars"
    ),
    UserPreference(
      hotel_city="Sydney, Australia",
      hotel_name="Four Seasons Hotel Sydney",
      check_in_date="2025-10-03",
      check_out_date="2025-10-07",
      number_of_nights=4,
      number_of_adults=1,
      has_children=False,
      themes=["business", "wellness", "culture"],
      must_do_activities=["morning walk in Royal Botanic Garden", "Sydney Opera House tour"],
      trip_pace="balanced",
      activity_budget="Keep It Simple",
      food_style="Keep It Simple",
      dietary_requirements=["gluten-free"],
      proximity_preference="See the best within reach",
      free_text="solo work trip; interested in wellness classes after meetings"
    ),
    UserPreference(
      hotel_city="Sydney, Australia",
      hotel_name="Ovolo Woolloomooloo",
      check_in_date="2025-08-20",
      check_out_date="2025-08-24",
      number_of_nights=4,
      number_of_adults=3,
      has_children=False,
      themes=["adventure", "food", "nightlife"],
      must_do_activities=["kayaking in Sydney Harbour", "pub crawl in Newtown"],
      trip_pace="active",
      activity_budget="Mix & Match",
      food_style="Casual Indulgence",
      dietary_requirements=[],
      proximity_preference="Keen to get out and about",
      free_text="group of friends; want craft-beer spots and live music"
    )
  ]


def format_user_prompt(config: Dict[str, str], trip_input: UserPreference) -> str:
  """Format the prompt template with trip input data"""
  children_clause = f" and {1 if trip_input.has_children else 0} child(ren)" if trip_input.has_children else ""
  themes_text = ", ".join(trip_input.themes)
  themes_list = "\n".join([f"• {theme}" for theme in trip_input.themes])
  must_do_text = ", ".join(trip_input.must_do_activities)
  must_do_list = "\n".join([f"• {activity}" for activity in trip_input.must_do_activities])
  dietary_text = ", ".join(trip_input.dietary_requirements) if trip_input.dietary_requirements else "None"
  dietary_list = "\n".join([f"• {req}" for req in trip_input.dietary_requirements]) if trip_input.dietary_requirements else "None"
  
  user_prompt = config["user_prompt"].format(
      hotel_city=trip_input.hotel_city,
      hotel_name=trip_input.hotel_name,
      check_in_date=trip_input.check_in_date,
      check_out_date=trip_input.check_out_date,
      number_of_nights=trip_input.number_of_nights,
      number_of_adults=trip_input.number_of_adults,
      children_clause=children_clause,
      themes_text=themes_text,
      themes_list=themes_list,
      must_do_text=must_do_text,
      must_do_list=must_do_list,
      trip_pace=trip_input.trip_pace,
      activity_budget=trip_input.activity_budget,
      food_style=trip_input.food_style,
      dietary_text=dietary_text,
      dietary_list=dietary_list,
      proximity_preference=trip_input.proximity_preference,
      free_text=trip_input.free_text
  )
  
  return user_prompt


async def generate_trip(agent: Agent ,user_prompt: str) -> tuple[RunResult, float]:
  input_items: list[TResponseInputItem] = [{"content": user_prompt, "role": "user"}]
  start_time = time.time()

  response = await Runner.run(
    agent,
    input_items
  )

  end_time = time.time()
  latency = end_time - start_time
  
  return response, latency


async def judge_response(evaluator: Agent, user_preference: UserPreference, response: str) -> RunResult:
  judge_request = f"""Please evaluate this trip plan:

Trip Requirements:
- Destination: {user_preference.hotel_city}
- Duration: {user_preference.number_of_nights} nights
- Themes: {', '.join(user_preference.themes)}
- Must-do: {', '.join(user_preference.must_do_activities)}
- Pace: {user_preference.trip_pace}
- Budget: {user_preference.activity_budget}
- Food Style: {user_preference.food_style}
- Dietary: {', '.join(user_preference.dietary_requirements) if user_preference.dietary_requirements else 'None'}
- Proximity: {user_preference.proximity_preference}
- Notes: {user_preference.free_text}

Trip Plan to Evaluate:
{response}"""
  eval_response = await Runner.run(
    evaluator,
    judge_request
  )

  return eval_response


async def evaluation_process(config: Dict[str, str], agent: Agent, evaluator: Agent, user_preference: UserPreference, run_id: int) -> FinalResult:
  """Process a single user preference and return the final result"""
  print(f"\n📍 Processing input {run_id}/5: {user_preference.hotel_city}")
  
  user_prompt = format_user_prompt(config, user_preference)
  
  ## First call for the response + latency
  response, latency = await generate_trip(agent, user_prompt)
  ## Second call for eval
  evalResult = await judge_response(evaluator, user_preference, response.final_output)
  
  print(f"Run {run_id}:\n- Latency: {latency:.2f}s\n- Evaluation: {evalResult.final_output}\n")
  
  # Create and return final result
  return FinalResult(
      id=config['id'],
      type=config['type'],
      run_no=run_id,
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
  filename = f"./results/{timestamp}.csv"
  
  fieldnames = [
    'id', 'type', 'run_no', 'score', 'latency', 'feedback', 'created_at',
    'input', 'response'
  ]
  
  with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for result in results:
      writer.writerow({
        'id': result.id,
        'type': result.type,
        'run_no': result.run_no,
        'score': result.score,
        'latency': round(result.latency, 2),
        'feedback': result.feedback,
        'created_at': result.created_at,
        'input': result.input,
        'response': result.response
      })
  
  return filename


async def main():
  if not os.environ.get('OPENAI_API_KEY'):
    print('Error: API key not found')
    return

  # Store user_prompt, system_prompt, and the run metadata
  # Change here to test different config
  # Add more config in _load_configs following structure in README
  config = _load_configs()['config_a']
  agent_model = "gpt-4o"
  eval_model = "o3-mini"

  # Get sample input and format it
  user_preferences_list = generate_sample_inputs()

  agent = _create_agent(agent_model ,config['system_prompt'])
  evaluator = _create_judge(eval_model)
  print(f"⚙️  Running {config['id']}...")

  # Create tasks for all user preferences to run concurrently
  tasks = [
    evaluation_process(config, agent, evaluator, user_preference, run_id)
    for run_id, user_preference in enumerate(user_preferences_list, 1)
  ]

  # Run all tasks concurrently
  results = await asyncio.gather(*tasks)

  print(f"\n✅ Completed all {len(results)} evaluations")
  for result in results:
    print(f"Run {result.run_no}: Score {result.score}/10")

  # Save results to CSV
  csv_filename = save_to_csv(results)
  print(f"📊 Results saved to: {csv_filename}")

if __name__ == "__main__":
  asyncio.run(main())
