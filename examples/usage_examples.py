"""
Examples showing how to use the new functional LLM evaluation API.

This demonstrates the flexibility of the new API design that works
seamlessly in both CLI and Streamlit app contexts.
"""

import asyncio
from typing import List, Dict, Any

# Import the main API functions
from evals import evaluate_from_config, evaluate, generate_responses, run_evaluation
from evals.core.input_loaders import InputData, Prompt, Criterion, get_config_data
from evals.models.base import GenerationTrace
from evals.strategies.base import EvalTrace


async def example_1_simple_evaluation():
    """Example 1: Simple evaluation from config file (CLI-style)"""
    print("🎯 Example 1: Simple evaluation from config file")

    # This is the simplest way - just provide a config file path
    config_path = "configs/sample.yaml"

    try:
        # Get just the results
        results = await evaluate(config_path)
        print(f"✅ Evaluation completed with {len(results)} traces")
        return results
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


async def example_2_full_pipeline():
    """Example 2: Full pipeline with access to intermediate data"""
    print("\n🔧 Example 2: Full pipeline with intermediate data")

    config_path = "configs/sample.yaml"

    try:
        # Get all intermediate data
        input_data, responses, results = await evaluate_from_config(config_path)

        print(f"📋 Config: {input_data.mode} mode")
        print(f"🤖 Generated {len(responses)} responses")
        print(f"📊 Produced {len(results)} evaluation traces")

        # You can now use the intermediate data for further processing
        return input_data, responses, results

    except Exception as e:
        print(f"❌ Error: {e}")
        return None, [], []


async def example_3_programmatic_config():
    """Example 3: Programmatic configuration (Streamlit-style)"""
    print("\n⚙️ Example 3: Programmatic configuration")

    # Create configuration programmatically (useful for Streamlit)
    input_data = InputData(
        prompt=Prompt(
            prompt_id="test-prompt",
            system_prompt="You are a helpful assistant.",
            user_prompt="Tell me about Python."
        ),
        mode="reference_free",
        structured=False,
        candidates=[
            {
                "model": "gpt-4o-mini",
                "temperature": 0.7,
                "top_p": 0.9,
                "effort": "medium"
            }
        ],
        judge={
            "model": "gpt-4o",
            "temperature": 0.1,
            "top_p": 0.95,
            "effort": "high"
        },
        criteria=[
            Criterion(
                type="rubric",
                name="helpfulness",
                question="How helpful is this response?",
                weight=1.0
            )
        ]
    )

    try:
        # Step 1: Generate responses
        responses = await generate_responses(input_data)
        print(f"🤖 Generated {len(responses)} responses")

        # Step 2: Run evaluation
        results = await run_evaluation(input_data, responses)
        print(f"📊 Completed evaluation with {len(results)} traces")

        return input_data, responses, results

    except Exception as e:
        print(f"❌ Error: {e}")
        return None, [], []


async def example_4_mode_specific():
    """Example 4: Mode-specific evaluation functions"""
    print("\n🎯 Example 4: Mode-specific evaluation")

    config_path = "configs/sample.yaml"

    try:
        # Load config first
        input_data = get_config_data(config_path)

        # Use mode-specific functions
        if input_data.mode == "reference_free":
            from evals import evaluate_reference_free
            results = await evaluate_reference_free(input_data)
            print(f"✅ Reference-free evaluation: {len(results)} traces")
        elif input_data.mode == "ground_truth":
            from evals import evaluate_ground_truth
            results = await evaluate_ground_truth(input_data)
            print(f"✅ Ground truth evaluation: {len(results)} traces")
        else:
            print(f"❌ Unknown mode: {input_data.mode}")
            results = []

        return results

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def streamlit_example():
    """Example 5: How to use in Streamlit app"""
    print("\n🎨 Example 5: Streamlit integration pattern")

    # This is how you would integrate with Streamlit
    streamlit_code = '''
import streamlit as st
import asyncio
from evals import evaluate_from_config, generate_responses, run_evaluation
from evals.core.input_loaders import InputData, Prompt, Criterion

# Streamlit UI components
st.title("LLM Evaluation System")

# Get user inputs
model = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini"])
temperature = st.slider("Temperature", 0.0, 2.0, 1.0)
mode = st.selectbox("Mode", ["reference_free", "ground_truth"])

# Build config programmatically
if st.button("Run Evaluation"):
    config_data = InputData(
        prompt=Prompt(
            prompt_id="streamlit-prompt",
            system_prompt=st.text_area("System Prompt"),
            user_prompt=st.text_area("User Prompt")
        ),
        mode=mode,
        structured=False,
        candidates=[{
            "model": model,
            "temperature": temperature,
            "top_p": 0.9,
            "effort": "medium"
        }],
        judge={
            "model": "gpt-4o",
            "temperature": 0.1,
            "effort": "high"
        },
        criteria=[
            Criterion(
                type="rubric",
                name="quality",
                question="How good is this response?",
                weight=1.0
            )
        ]
    )
    
    # Run evaluation
    with st.spinner("Running evaluation..."):
        input_data, responses, results = asyncio.run(
            evaluate_from_config_programmatic(config_data)
        )
        
    # Display results
    st.success(f"Evaluation completed with {len(results)} traces")
    st.json([r.__dict__ for r in results])

async def evaluate_from_config_programmatic(config_data):
    """Helper function for Streamlit"""
    responses = await generate_responses(config_data)
    results = await run_evaluation(config_data, responses)
    return config_data, responses, results
    '''

    print("📝 Streamlit integration code example above shows how to:")
    print("   • Build configuration programmatically")
    print("   • Use the core API functions")
    print("   • Handle async operations in Streamlit")
    print("   • Display results in the UI")


async def main():
    """Run all examples"""
    print("🚀 LLM Evaluation API Usage Examples")
    print("=" * 50)

    # Note: These examples assume you have valid config files
    # For demonstration, we'll show the patterns without actually running

    print("\n📚 Available Usage Patterns:")
    print("1. Simple evaluation from config file (CLI-style)")
    print("2. Full pipeline with intermediate data access")
    print("3. Programmatic configuration (Streamlit-style)")
    print("4. Mode-specific evaluation functions")
    print("5. Streamlit integration pattern")

    # Show the Streamlit example
    streamlit_example()

    print("\n✅ All examples demonstrated!")
    print("\n🎯 Key Benefits of the New API:")
    print("   • Pure functions - easy to test and reason about")
    print("   • Composable - use components independently")
    print("   • Reusable - works in CLI, Streamlit, and other contexts")
    print("   • Clean separation - core logic separate from UI concerns")


if __name__ == "__main__":
    asyncio.run(main())
