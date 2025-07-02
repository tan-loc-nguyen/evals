#!/usr/bin/env python3
"""
Test script for the evaluation runner.
Demonstrates usage of the runner.py with different configurations.
"""

import asyncio
import sys
from pathlib import Path

# Add the evals directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "evals"))

from evals.core.runner import EvaluationRunner

async def test_reference_free_evaluation():
    """Test reference-free evaluation mode."""
    print("🧪 Testing Reference-Free Evaluation...")
    
    config_path = "evals/configs/sample.yaml"
    output_path = "results/test_reference_free_results.json"
    
    try:
        runner = EvaluationRunner(
            config_path=config_path,
            output_path=output_path
        )
        
        results = await runner.run()
        print(f"✅ Reference-free test completed! Generated {len(results)} traces.")
        
    except Exception as e:
        print(f"❌ Reference-free test failed: {e}")

async def test_trip_planner_evaluation():
    """Test trip planner evaluation."""
    print("\n🧪 Testing Trip Planner Evaluation...")
    
    config_path = "evals/configs/tripPlanner/reference_free.yaml"
    output_path = "results/test_trip_planner_results.json"
    
    try:
        runner = EvaluationRunner(
            config_path=config_path,
            output_path=output_path
        )
        
        results = await runner.run()
        print(f"✅ Trip planner test completed! Generated {len(results)} traces.")
        
    except Exception as e:
        print(f"❌ Trip planner test failed: {e}")

async def main():
    """Run all tests."""
    print("🎯 Running Runner Tests")
    print("=" * 50)
    
    # Create results directory
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    # Run tests
    await test_reference_free_evaluation()
    await test_trip_planner_evaluation()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 