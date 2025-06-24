# Travel Itinerary Evaluation Script

This script evaluates different AI prompt configurations for generating travel itineraries using OpenAI's models.

## Overview

The `evals.py` script compares two different prompt strategies for AI-powered travel planning:
- **Config A**: Detailed free-form approach with specific formatting requirements
- **Config B**: Structured role-based approach with clear task breakdown

Each configuration is tested against 5 sample Sydney travel scenarios and evaluated by an AI judge for quality scoring.

## Prerequisites

1. **Python Environment**: Python 3.8+ required
2. **OpenAI API Access**: 
   - GPT-4o model access (for itinerary generation)
   - o3-mini model access (for evaluation)

## Setup

### 1. Install Dependencies
```bash
pip install openai-agents
# Note: The custom 'agents' library must be available in your Python environment
```

### 2. Set OpenAI API Key

```
#.env
OPENAI_API_KEY="your-openai-api-key-here"
```

Or

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

## Usage

### Basic Execution
```bash
python -u evals.py
```

### Configuration Selection
By default, the script runs `config_a`. To change the configuration being tested, modify the config selection in `evals.py`:

```python
# Change this line to test different configurations
config = _load_configs()['config_a']  # or 'config_b'
```

### Model Selection
You can also configure which models to use for generation and evaluation:

```python
agent_model = "gpt-4o"      # Model for itinerary generation
eval_model = "o3-mini"      # Model for evaluation
```

## What the Script Does

1. **Loads Configuration**: Retrieves prompt templates for the selected configuration
2. **Generates Sample Inputs**: Creates 5 diverse Sydney travel scenarios with different:
   - Hotel locations and types
   - Travel dates and durations
   - Group compositions (couples, families, solo, friends)
   - Themes and preferences
   - Budgets and dietary requirements

3. **Runs Evaluations**: For each sample input:
   - Formats the user prompt with trip details
   - Generates a travel itinerary using GPT-4o
   - Evaluates the itinerary using o3-mini as a judge
   - Records latency and scores

4. **Provides Results**: Outputs scores (0-10) and feedback for each evaluation

## Sample Scenarios

The script tests these travel scenarios:

1. **Luxury Couple**: Shangri-La Sydney, fine dining, harbour views
2. **Family Trip**: The Langham, kid-friendly, relaxed pace, nut allergy considerations
3. **Couple's Getaway**: QT Sydney, nightlife, art, vegetarian preferences
4. **Solo Business**: Four Seasons, wellness, culture, gluten-free requirements
5. **Friends Group**: Ovolo Woolloomooloo, adventure, craft beer, active pace

## Evaluation Criteria

The AI judge evaluates itineraries based on:

1. **Relevance**: How well the plan matches user preferences (themes, pace, budget, dietary needs)
2. **Feasibility**: Realistic timing and logistics
3. **Quality**: Specific place recommendations and useful insider tips
4. **Completeness**: All days covered, restaurant recommendations, alternate day options

## Customization

### Adding New Scenarios
Modify the `generate_sample_inputs()` function to add new test cases with different destinations, preferences, or requirements.

### Creating New Configurations
Add new prompt configurations in the `_load_configs()` function following the existing structure:

```python
config_name = {
    "id": "config_name",
    "type": "your-type",
    "system_prompt": "Your system prompt...",
    "user_prompt": "Your user prompt template with {placeholders}..."
}
```

### Modifying Evaluation Criteria
Update the judge's instructions in the `_create_judge()` function to change how itineraries are evaluated.

### Changing Models
To use different OpenAI models, modify the model variables in the `main()` function:

```python
agent_model = "gpt-4o"      # For itinerary generation
eval_model = "o3-mini"      # For evaluation scoring
```

Available options include `gpt-4o`, `gpt-4`, `o3-mini`, etc., depending on your OpenAI access.

## Data Structure

The script uses these main data structures:

- `UserPreference`: Trip requirements and preferences
- `EvalResult`: Judge's score and feedback
- `FinalResult`: Complete evaluation result with metadata

## Troubleshooting

**Common Issues:**

1. **Missing API Key**: Ensure `OPENAI_API_KEY` environment variable is set
2. **Model Access**: Verify you have access to both GPT-4o and o3-mini models
3. **Agents Library**: The custom agents library must be properly installed and importable
4. **Rate Limits**: If you hit OpenAI rate limits, the script will fail - consider adding retry logic

**Error Messages:**
- `Error: API key not found` - Set your OpenAI API key
- Import errors - Ensure the agents library is available
- Model access errors - Check your OpenAI account permissions
