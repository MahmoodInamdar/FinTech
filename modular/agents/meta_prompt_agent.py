# Meta-Prompt Agent
from .base_agent import BaseAgent
from typing import Dict, Any, List
import pandas as pd

class MetaPromptAgent(BaseAgent):
    """Agent responsible for creating contextual prompts for other agents"""

    def __init__(self):
        super().__init__("MetaPromptAgent", "gpt-3.5-turbo")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request and generate contextual prompts"""
        command = input_data.get('command', '')
        df = input_data.get('dataframe')
        agent_type = input_data.get('target_agent', 'data')

        context = self.analyze_context(df, command)
        prompt = self.create_contextual_prompt(command, context, agent_type)

        return {
            'prompt': prompt,
            'context': context,
            'agent_type': agent_type
        }

    def analyze_context(self, df: pd.DataFrame, command: str) -> Dict[str, Any]:
        """Analyze data context and user command"""
        if df is None:
            return {'error': 'No dataframe available'}

        # Basic data analysis
        context = {
            'data_shape': df.shape,
            'columns': list(df.columns),
            'numeric_columns': list(df.select_dtypes(include=['number']).columns),
            'categorical_columns': list(df.select_dtypes(include=['object']).columns),
            'date_columns': list(df.select_dtypes(include=['datetime64']).columns),
            'missing_values': df.isnull().sum().sum(),
            'sample_values': {}
        }

        # Get sample values for each column type
        for col in context['numeric_columns'][:3]:
            context['sample_values'][col] = {
                'min': df[col].min(),
                'max': df[col].max(),
                'mean': df[col].mean()
            }

        for col in context['categorical_columns'][:3]:
            context['sample_values'][col] = df[col].value_counts().head(3).to_dict()

        # Analyze command intent
        command_lower = command.lower()
        context['intent'] = self.classify_intent(command_lower)
        context['mentioned_columns'] = self.extract_column_mentions(command_lower, df.columns)

        return context

    def classify_intent(self, command: str) -> str:
        """Classify the user's intent"""
        intent_patterns = {
            'visualization': ['show', 'plot', 'chart', 'graph', 'visualize', 'display'],
            'analysis': ['analyze', 'analysis', 'correlation', 'relationship', 'pattern'],
            'filtering': ['filter', 'where', 'select', 'find', 'get'],
            'aggregation': ['sum', 'average', 'count', 'total', 'group', 'by'],
            'comparison': ['compare', 'versus', 'vs', 'difference', 'top', 'bottom'],
            'trend': ['trend', 'over time', 'seasonal', 'seasonality', 'time series']
        }

        for intent, keywords in intent_patterns.items():
            if any(keyword in command for keyword in keywords):
                return intent

        return 'general'

    def extract_column_mentions(self, command: str, columns: List[str]) -> List[str]:
        """Extract column names mentioned in the command"""
        mentioned = []
        for col in columns:
            if col.lower() in command or col.lower().replace('_', ' ') in command:
                mentioned.append(col)
        return mentioned

    def create_contextual_prompt(self, command: str, context: Dict[str, Any], agent_type: str) -> str:
        """Create contextual prompt for target agent"""
        if agent_type == 'data':
            return self.create_data_analysis_prompt(command, context)
        elif agent_type == 'visualization':
            return self.create_visualization_prompt(command, context)
        elif agent_type == 'code':
            return self.create_code_prompt(command, context)
        else:
            return self.create_general_prompt(command, context)

    def create_data_analysis_prompt(self, command: str, context: Dict[str, Any]) -> str:
        """Create prompt for data analysis agent"""
        prompt = f"""
        You are a data analysis expert. Analyze the following user request in the context of the provided dataset.

        User Command: "{command}"

        Dataset Context:
        - Shape: {context['data_shape'][0]} rows, {context['data_shape'][1]} columns
        - Numeric columns: {', '.join(context['numeric_columns'][:5])}
        - Categorical columns: {', '.join(context['categorical_columns'][:5])}
        - User intent: {context.get('intent', 'general')}
        - Mentioned columns: {', '.join(context.get('mentioned_columns', []))}

        Determine the best data operation to perform:
        1. Identify the operation type (filter, sort, group, aggregate, top, correlation, etc.)
        2. Determine relevant columns to use
        3. Specify any parameters needed
        4. Consider the user's intent and mentioned columns

        Provide a clear analysis plan that addresses the user's request effectively.
        """
        return prompt

    def create_visualization_prompt(self, command: str, context: Dict[str, Any]) -> str:
        """Create prompt for visualization agent"""
        prompt = f"""
        You are a data visualization expert. Create appropriate visualizations for the user's request.

        User Command: "{command}"

        Dataset Context:
        - Shape: {context['data_shape'][0]} rows, {context['data_shape'][1]} columns
        - Numeric columns: {', '.join(context['numeric_columns'][:5])}
        - Categorical columns: {', '.join(context['categorical_columns'][:5])}
        - Date columns: {', '.join(context['date_columns'])}
        - User intent: {context.get('intent', 'general')}
        - Mentioned columns: {', '.join(context.get('mentioned_columns', []))}

        Recommend the most appropriate visualization(s):
        1. Consider the data types and user intent
        2. Choose suitable chart types (bar, line, scatter, heatmap, etc.)
        3. Determine appropriate x and y axes
        4. Consider color coding and grouping options
        5. Suggest interactive features if beneficial

        Focus on creating clear, informative visualizations that answer the user's question.
        """
        return prompt

    def create_code_prompt(self, command: str, context: Dict[str, Any]) -> str:
        """Create prompt for code execution agent"""
        prompt = f"""
        You are a Python code generation expert specializing in data analysis and visualization.

        User Command: "{command}"

        Dataset Context:
        - Shape: {context['data_shape'][0]} rows, {context['data_shape'][1]} columns
        - Numeric columns: {', '.join(context['numeric_columns'][:5])}
        - Categorical columns: {', '.join(context['categorical_columns'][:5])}
        - Available as 'df' variable in the execution environment

        Generate Python code that:
        1. Addresses the user's request effectively
        2. Uses appropriate libraries (pandas, plotly, numpy, etc.)
        3. Includes error handling
        4. Creates meaningful visualizations if requested
        5. Returns or displays results appropriately

        Make the code clean, efficient, and well-commented.
        """
        return prompt

    def create_general_prompt(self, command: str, context: Dict[str, Any]) -> str:
        """Create general purpose prompt"""
        prompt = f"""
        Analyze the following data-related request and provide helpful insights.

        User Request: "{command}"

        Dataset Information:
        - {context['data_shape'][0]} rows and {context['data_shape'][1]} columns
        - Column types: {len(context['numeric_columns'])} numeric, {len(context['categorical_columns'])} categorical

        Provide a comprehensive response that addresses the user's needs and suggests next steps.
        """
        return prompt

    def generate_suggestions(self, df: pd.DataFrame) -> List[str]:
        """Generate analysis suggestions based on data characteristics"""
        if df is None:
            return []

        suggestions = []

        # Basic suggestions based on data types
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        date_cols = df.select_dtypes(include=['datetime64']).columns

        # Numeric data suggestions
        if len(numeric_cols) >= 2:
            suggestions.append(f"Show correlation between {numeric_cols[0]} and {numeric_cols[1]}")
            suggestions.append(f"Compare distribution of {numeric_cols[0]} across different groups")

        if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
            suggestions.append(f"Group {numeric_cols[0]} by {categorical_cols[0]}")
            suggestions.append(f"Show top 10 {categorical_cols[0]} by {numeric_cols[0]}")

        # Time series suggestions
        if len(date_cols) >= 1 and len(numeric_cols) >= 1:
            suggestions.append(f"Show {numeric_cols[0]} trend over time")
            suggestions.append(f"Analyze seasonality in {numeric_cols[0]}")

        # General suggestions
        suggestions.extend([
            "Show summary statistics for all numeric columns",
            "Find missing values and data quality issues",
            "Display value counts for categorical variables"
        ])

        return suggestions[:6]  # Return top 6 suggestions
