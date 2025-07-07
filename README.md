# 🎯 LLM Evaluation System

A comprehensive system for evaluating Large Language Model outputs with both command-line tools and visual dashboards. The system supports multiple evaluation modes, configurable judges, and detailed analysis capabilities.

## 🚀 Quick Start

### Using the CLI (Recommended)
```bash
# Run a basic evaluation
python eval_cli.py run-eval evals/configs/sample.yaml

# Run with custom output file
python eval_cli.py run-eval evals/configs/tripPlanner/reference_free.yaml --output results.json

# Run with verbose logging
python eval_cli.py run-eval evals/configs/sample.yaml --verbose
```

### Using the Dashboard
```bash
# Start the Streamlit dashboard
streamlit run app.py
```

## 📋 System Overview

The system consists of two main components:

### 1. 🖥️ CLI Tools (`/cli`)
Command-line interface for running evaluations programmatically:
- **Config-driven evaluations**: YAML-based configuration
- **Multiple evaluation modes**: Reference-free, ground-truth, comparison
- **Flexible model support**: Multiple LLM providers and models
- **Structured output**: JSON results for integration

### 2. 📊 Dashboard (`/app`)
Web-based visualization and analysis interface:

## Features

### 🧠 Quality Evaluation Dashboard
- **Judge Variant Selection**: Choose between different LLM judges (GPT-4, Claude-3, Custom-Rubric)
- **Test Variant Overview**: Compare model performance with bar charts and summary tables
- **Run-Level Analysis**: Track score trends over time with interactive line charts
- **Trace-Level Drilldown**: Deep dive into individual evaluation traces with detailed scoring breakdowns
- **Export Capabilities**: Download full trace data as CSV or JSONL for further analysis

### ⏱ Latency Evaluation Dashboard
- **Performance Metrics**: View comprehensive latency statistics (mean, median, percentiles)
- **Distribution Visualization**: Box plots showing latency distributions across test variants
- **Per-Run Detail**: Analyze individual run performance with histograms and time-series plots
- **Statistical Analysis**: Detailed percentile breakdowns and outlier detection

## 🏗️ Architecture

The system follows a clean separation of concerns:

```
├── cli/                    # Command-line interface
│   ├── main.py            # Main CLI entry point
│   ├── run_eval.py        # Evaluation commands
│   └── utils.py           # CLI utilities
├── evals/                 # Core evaluation logic (pure library)
│   ├── core/              # Core evaluation engine
│   ├── models/            # Model interfaces
│   ├── modes/             # Evaluation modes
│   ├── strategies/        # Evaluation strategies
│   └── configs/           # Configuration templates
├── app/                   # Streamlit dashboard
│   ├── dashboard.py       # Main dashboard logic
│   └── pages/             # Individual dashboard pages
├── eval_cli.py            # Convenient CLI entry point
└── app.py                 # Dashboard entry point
```

## 🛠️ Installation & Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your environment**
   ```bash
   # Add your OpenAI API key
   export OPENAI_API_KEY=your_api_key_here
   ```

3. **Run evaluations**
   ```bash
   # CLI approach
   python eval_cli.py run-eval evals/configs/sample.yaml
   
   # Dashboard approach
   streamlit run app.py
   ```

## Dashboard Navigation

### Main Interface
- Use the **sidebar** to switch between evaluation types
- **Quality Dashboard**: Focuses on LLM-as-judge evaluations with multi-criteria scoring
- **Latency Dashboard**: Analyzes performance metrics and response times

### Progressive Drill-Down
1. **Overview Level**: Compare all test variants at a glance
2. **Run Level**: Analyze performance trends over time
3. **Trace Level**: (Quality only) Examine individual evaluation instances
4. **Export**: Download detailed data for external analysis

## Data Structure

The dashboard currently uses mock data but is designed to work with:

### Quality Evaluation Data
- **Test Variants**: Different model configurations being evaluated
- **Judge Variants**: Different evaluation approaches or LLM judges
- **Runs**: Individual evaluation attempts with unique run IDs
- **Traces**: Individual evaluation instances with detailed scoring

### Latency Evaluation Data
- **Test Variants**: Different model configurations
- **Runs**: Performance measurement sessions
- **Metrics**: Response time statistics and percentiles

## Customization

The dashboard is built with a modular structure:
- `generate_mock_*_data()`: Replace with your actual data loading functions
- `render_*_dashboard()`: Customize the visualization components
- CSS styling can be modified in the `st.markdown()` sections

## Technology Stack

- **Streamlit**: Interactive web application framework
- **Plotly**: Interactive charts and visualizations
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing

## Future Enhancements

- Real-time data integration
- Advanced filtering and comparison features
- Custom rubric configuration
- Automated report generation
- Multi-user collaboration features 