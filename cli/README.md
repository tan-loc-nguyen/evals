# LLM Evaluation CLI

This directory contains the command-line interface for the LLM evaluation system. The CLI has been separated from the core evaluation logic to provide a clean interface while keeping the `evals` package as a pure library.

## Structure

```
cli/
├── __init__.py       # Package initialization
├── main.py           # Main CLI entry point with subcommands
├── run_eval.py       # Run evaluation command
├── utils.py          # CLI utility functions
└── README.md         # This file
```

## Usage

### Method 1: Using the convenience script

```bash
# Run an evaluation
python eval_cli.py run-eval evals/configs/sample.yaml

# Run with output file
python eval_cli.py run-eval evals/configs/sample.yaml --output results.json

# Run with verbose logging
python eval_cli.py run-eval evals/configs/sample.yaml --verbose
```

### Method 2: Using Python modules

```bash
# Run the main CLI
python -m cli.main run-eval evals/configs/sample.yaml

# Run specific command directly
python -m cli.run_eval evals/configs/sample.yaml
```

## Available Commands

### run-eval

Run an evaluation using a configuration file.

**Usage:**
```bash
python eval_cli.py run-eval <config_path> [options]
```

**Arguments:**
- `config_path`: Path to the YAML configuration file

**Options:**
- `-o, --output`: Optional path to save evaluation results (JSON format)
- `-v, --verbose`: Enable verbose logging

**Examples:**
```bash
# Basic evaluation
python eval_cli.py run-eval evals/configs/tripPlanner/reference_free.yaml

# Save results to specific file
python eval_cli.py run-eval evals/configs/tripPlanner/reference_free.yaml --output my_results.json

# Enable verbose logging
python eval_cli.py run-eval evals/configs/tripPlanner/reference_free.yaml --verbose
```

## Configuration Files

The CLI expects YAML configuration files that define:
- Evaluation mode (reference_free, ground_truth, comparison)
- Candidate models to evaluate
- Judge model for scoring
- Evaluation criteria
- Prompts and expected outputs

See `evals/configs/` for example configuration files.

## Adding New Commands

To add a new CLI command:

1. Create a new module in the `cli/` directory (e.g., `cli/new_command.py`)
2. Implement the command logic with a `main()` function
3. Add the command to the subparsers in `cli/main.py`
4. Add a handler function in `cli/main.py`

## Architecture

The CLI follows a clear separation of concerns:

- **CLI Layer** (`cli/`): Handles command-line interface, argument parsing, and user interaction
- **Core Logic** (`evals/`): Contains the pure evaluation logic without any CLI dependencies
- **Entry Points**: Simple scripts that wire everything together

This design allows the `evals` package to be used as a library in other applications while providing a user-friendly CLI interface. 