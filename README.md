# 📊 Evaluation Dashboard

A comprehensive Streamlit dashboard for visualizing and analyzing evaluation results across test variants, judge variants, and evaluation types (quality vs latency).

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

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Dashboard**
   ```bash
   streamlit run app.py
   ```

3. **Access the Dashboard**
   Open your browser and navigate to `http://localhost:8501`

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