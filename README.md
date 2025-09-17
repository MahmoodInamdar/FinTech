# 📊 AI-Powered Data Analytics Dashboard

## 🏗️ System Architecture Overview

This is a sophisticated multi-agent AI system built with Streamlit that provides intelligent data analysis with automatic visualization generation. The system uses a **Two-Model Architecture** where specialized AI agents work together to deliver comprehensive data insights.

---

## 📁 Project Structure

```
FinTech/
├── modular/                    # Main application directory
│   ├── main.py                 # Main Streamlit application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables (API keys)
│   ├── .gitignore             # Git ignore rules
│   └── agents/                # AI Agent modules
│       ├── __init__.py        # Package initialization
│       ├── base_agent.py      # Abstract base class for all agents
│       ├── coordinator.py     # Traditional multi-agent coordinator
│       ├── data_agent.py      # Data processing and analysis agent
│       ├── visualization_agent.py # Chart and graph generation agent
│       ├── code_execution_agent.py # Python code execution agent
│       ├── meta_prompt_agent.py # Dynamic prompt generation agent
│       ├── two_model_coordinator.py # Two-model system coordinator
│       ├── data_context_analyzer.py # Model 2: Data context analyzer
│       └── data_analyst_chatbot.py # Model 1: Conversational analyst
└── venv/                      # Python virtual environment
```

---

## 🤖 AI Agents Detailed Breakdown

### Core System Files

#### `main.py` - Main Application Controller
**Purpose**: Central Streamlit application that orchestrates all AI agents and manages user interface
**Key Functions**:
- `FinTechApp.run()` - Main application loop
- `render_chat_interface()` - Manages conversational AI interface
- `render_powerbi_visualization_interface()` - Direct visualization creation
- `render_traditional_interface()` - Multi-agent workflow interface
- `load_and_process_data()` - Data upload and preprocessing

**Features**:
- Three analysis modes: 2-Model Analyst Chatbot, Power BI Style Visualizations, Traditional Multi-Agent System
- File upload support (CSV, Excel)
- Real-time chat interface with AI analyst
- Automatic chart generation
- Multi-language support

---

### AI Agent Architecture

#### `base_agent.py` - Foundation Class
**Purpose**: Abstract base class defining the common interface for all AI agents
**Key Components**:
- `BaseAgent.__init__()` - Initialize agent with model and API key
- `process()` - Abstract method that all agents must implement
- `initialize_model()` - OpenAI client setup

#### `two_model_coordinator.py` - System Orchestrator
**Purpose**: Coordinates the two-model system (Data Context Analyzer + Data Analyst Chatbot)
**Key Functions**:
- `process()` - Manages communication between Model 1 and Model 2
- `initialize_models()` - Sets up both AI models with data access
- `chat()` - Handles conversational flow between models

**Workflow**:
1. Model 2 analyzes data structure and creates context
2. Model 1 receives context and becomes domain-specific analyst
3. Coordinator manages conversation flow and visualization requests

---

### Model 2: Data Intelligence Layer

#### `data_context_analyzer.py` - Smart Data Understanding
**Purpose**: Analyzes uploaded data to understand structure, patterns, and business context
**Key Functions**:
- `analyze_data_and_generate_context()` - Main analysis orchestrator
- `analyze_data_structure()` - Examines columns, types, distributions
- `extract_key_insights()` - Finds correlations, trends, target variables
- `detect_business_context()` - Identifies domain (sales, healthcare, etc.)
- `generate_system_prompt()` - Creates dynamic context for Model 1

**Intelligence Features**:
- Automatic business domain detection (sales, healthcare, HR, etc.)
- Correlation analysis between numeric variables
- Time trend identification
- Key metric detection (revenue, sales, profit columns)
- Dynamic system prompt generation for context-aware analysis

---

### Model 1: Conversational Analytics Layer

#### `data_analyst_chatbot.py` - AI Data Analyst
**Purpose**: Acts as a senior data analyst providing conversational insights to stakeholders
**Key Functions**:
- `chat()` - Main conversational interface
- `analyze_question_intent()` - Determines analysis type from user questions
- `generate_analyst_response()` - Creates business-focused insights
- `generate_visualizations()` - Automatically creates relevant charts
- `create_simple_comparison_chart()` - Fallback visualization generator

**Analysis Types**:
- **Time Analysis**: Trends, seasonality, growth patterns
- **Comparative Analysis**: Category comparisons, performance gaps
- **Performance Analysis**: Rankings, top/bottom performers
- **Correlation Analysis**: Relationship discovery
- **Overview Analysis**: Comprehensive data summaries

**Visualization Strategy**:
- Automatically generates charts for every meaningful question
- Multiple fallback mechanisms ensure charts are always created
- No permission-asking - directly provides visual insights

---

### Specialized Agent Layer

#### `visualization_agent.py` - Chart Generation Specialist
**Purpose**: Creates interactive Plotly visualizations based on data analysis requirements
**Key Functions**:
- `process()` - Main visualization request handler
- `plan_visualizations()` - Determines optimal chart types
- `create_bar_chart()`, `create_line_chart()`, etc. - Specific chart creators
- `generate_viz_options()` - Interactive chart selection system

**Supported Chart Types**:
- **Bar Charts**: Category comparisons, rankings
- **Line Charts**: Time trends with automatic trend lines
- **Scatter Plots**: Correlation analysis with regression
- **Histograms**: Distribution analysis
- **Heatmaps**: Correlation matrices, pivot tables
- **Box Plots**: Statistical distributions by categories
- **Pie Charts**: Proportional data visualization

#### `data_agent.py` - Data Processing Engine
**Purpose**: Advanced data manipulation, statistical analysis, and preprocessing
**Key Functions**:
- `process()` - Main data processing orchestrator
- `basic_analysis()` - Descriptive statistics and data profiling
- `advanced_analysis()` - Correlation analysis, outlier detection
- `data_quality_check()` - Missing data analysis, data validation

#### `code_execution_agent.py` - Dynamic Code Runner
**Purpose**: Executes Python code dynamically for custom analysis requests
**Key Functions**:
- `process()` - Code execution with safety constraints
- `validate_code()` - Security checks for code execution
- `execute_safely()` - Sandboxed code runner

#### `meta_prompt_agent.py` - Dynamic Prompt Engineer
**Purpose**: Generates context-aware prompts based on data characteristics
**Key Functions**:
- `process()` - Prompt generation based on data analysis
- `analyze_data_context()` - Understands data for prompt optimization

#### `coordinator.py` - Traditional Multi-Agent System
**Purpose**: Orchestrates multiple agents in a traditional workflow
**Key Functions**:
- `process()` - Manages agent workflow and task distribution
- `delegate_task()` - Routes tasks to appropriate specialized agents

---

## 🔄 System Workflows

### Two-Model Architecture Workflow

```
[Data Upload]
    ↓
[Model 2: Data Context Analyzer]
    ├── Analyzes data structure
    ├── Detects business domain
    ├── Finds key patterns/correlations
    ├── Identifies target metrics
    └── Generates dynamic system prompt
    ↓
[Model 1: Data Analyst Chatbot]
    ├── Receives context from Model 2
    ├── Becomes domain-specific analyst
    ├── Processes user questions
    ├── Generates business insights
    └── Auto-creates visualizations
    ↓
[User Interface]
    ├── Displays analytical response
    ├── Shows interactive charts
    └── Provides follow-up questions
```

### Power BI Style Workflow

```
[Data Upload]
    ↓
[Direct Chart Configuration]
    ├── User selects chart type
    ├── Configures columns/settings
    ├── Creates instant visualization
    └── Downloads chart as HTML
```

### Traditional Multi-Agent Workflow

```
[Data Upload]
    ↓
[Agent Coordinator]
    ├── Routes to Data Agent
    ├── Routes to Visualization Agent
    ├── Routes to Code Execution Agent
    └── Aggregates results
```

---

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- OpenAI API key
- Virtual environment (recommended)

### Installation Steps

1. **Clone and Navigate**
   ```bash
   cd modular
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   Create `.env` file with your API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run Application**
   ```bash
   streamlit run main.py
   ```

---

## 🎯 Usage Guide

### 1. Two-Model Analyst Chatbot Mode (Recommended)
- Upload your CSV/Excel data
- Ask natural language questions like:
  - "Show me revenue trends by region"
  - "Which products are performing best?"
  - "What patterns do you see in the sales data?"
- Get automatic visualizations with business insights

### 2. Power BI Style Mode
- Upload data
- Select chart type (bar, line, scatter, etc.)
- Configure axes and settings
- Generate instant visualizations
- Download charts as HTML files

### 3. Traditional Multi-Agent Mode
- Upload data
- Use structured agent workflow
- Get comprehensive analysis reports

---

## 🔧 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │ Chat Interface│ │Power BI Mode│ │Traditional Workflow │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                 TWO-MODEL COORDINATOR                       │
│  ┌─────────────────┐              ┌─────────────────────┐   │
│  │    MODEL 2      │             │      MODEL 1        │   │
│  │Data Context     │   context   │  Data Analyst       │   │
│  │Analyzer         │────────────→│  Chatbot            │   │
│  │                 │             │                     │   │
│  │• Domain Detection│             │• Business Insights  │   │
│  │• Pattern Analysis│             │• Conversational AI  │   │
│  │• Prompt Generation│             │• Auto-Visualization │   │
│  └─────────────────┘             └─────────────────────┘   │
└─────────────────────────────────────┬───────────────────────┘
                                      │
┌─────────────────────────────────────┴───────────────────────┐
│                 SPECIALIZED AGENTS                          │
│  ┌──────────┐ ┌──────────────┐ ┌─────────┐ ┌─────────────┐ │
│  │Visualization│ │  Data Agent  │ │Code Exec│ │Meta Prompt  │ │
│  │   Agent     │ │             │ │ Agent   │ │   Agent     │ │
│  │             │ │• Statistics  │ │         │ │             │ │
│  │• Charts     │ │• Analysis    │ │• Python │ │• Dynamic    │ │
│  │• Plotly     │ │• Processing  │ │ Exec    │ │ Prompts     │ │
│  └──────────┘ └──────────────┘ └─────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Key Features

### ✅ Intelligent Data Analysis
- Automatic business domain detection
- Context-aware insights generation
- Multi-language support
- Real-time conversation with AI analyst

### ✅ Advanced Visualizations
- 7+ chart types with automatic selection
- Interactive Plotly charts
- Trend analysis with regression lines
- Correlation heatmaps
- Statistical distribution plots

### ✅ Robust Architecture
- Modular agent-based design
- Multiple analysis modes
- Fallback mechanisms for reliability
- Secure code execution environment

### ✅ User Experience
- Drag-and-drop file upload
- Natural language queries
- Automatic chart generation (no permission asking)
- Business-focused insights
- Follow-up question suggestions

---

## 🔒 Security Features

- Sandboxed code execution
- API key environment protection
- Input validation and sanitization
- Safe file upload handling

---

## 🤝 Contributing

This system is designed with modularity in mind. To add new features:

1. **New Agent**: Extend `BaseAgent` class
2. **New Chart Type**: Add method to `VisualizationAgent`
3. **New Analysis**: Extend analysis methods in `DataAnalysisAgent`
4. **New Interface**: Add interface methods in `main.py`

---

## 📈 Performance Optimization

- Data sampling for large datasets (>50k rows)
- Caching with Streamlit `@st.cache_data`
- Efficient memory management
- Asynchronous processing capabilities

---

*Built with ❤️ using Streamlit, OpenAI GPT-4, and Plotly*
