# Data Analytics Software with Multi-Agent Framework

A powerful data analytics application built with Streamlit and powered by OpenAI that allows users to explore data using natural language commands.

## Features

🤖 **Multi-Agent Architecture**
- Data Analysis Agent: Handles data operations (filter, sort, group, aggregate)
- Meta-Prompt Agent: Creates contextual prompts for other agents
- Visualization Agent: Generates interactive charts and graphs
- Code Execution Agent: Executes Python code in a sandboxed environment

📊 **Interactive Visualizations**
- Dynamic chart generation based on data characteristics
- Multiple chart types: bar, line, scatter, histogram, heatmap, correlation matrix
- Plotly-powered interactive visualizations
- Feature selection and filtering capabilities

💬 **Natural Language Interface**
- Talk to your data instead of writing complex queries
- Smart suggestions based on data characteristics
- Context-aware prompt generation
- Multiple interpretation options for ambiguous requests

🔒 **Safe Code Execution**
- Sandboxed Python environment
- Code validation and security checks
- Support for pandas, plotly, numpy, and other data science libraries
- Real-time code execution with output capture

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd data_analytics_app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run main.py
```

## Usage

1. **Configure API Key**: Enter your OpenAI API key in the sidebar
2. **Upload Data**: Upload a CSV file or load sample data
3. **Explore**: Use natural language commands to explore your data
4. **Visualize**: Get automatic visualizations based on your requests
5. **Code**: Write custom Python code in the sandbox environment
6. **Export**: Download results as CSV files

## Example Commands

- "Show seasonality by region"
- "Top 5 products this quarter" 
- "Correlation between sales and discount"
- "Group revenue by customer age"
- "Display trends over time"
- "Find missing values in the dataset"

## Architecture

The application follows an agentic multi-agent architecture where:

1. **Meta-Prompt Agent** analyzes user commands and data context
2. **Data Analysis Agent** performs data operations based on the analysis
3. **Visualization Agent** creates appropriate charts and visualizations  
4. **Code Execution Agent** handles custom Python code execution
5. **Coordinator** orchestrates communication between agents

## Technologies

- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Data Processing**: Pandas, NumPy
- **AI**: OpenAI GPT-3.5-turbo
- **Agent Framework**: Custom multi-agent system
- **Code Execution**: Secure Python sandbox

## Security

- Sandboxed code execution environment
- Input validation and sanitization
- Restricted library imports
- Safe operation patterns

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details
