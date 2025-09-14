# Code Execution Agent
from .base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import pandas as pd
import io
import sys
import subprocess
import tempfile
import os
import re
import traceback
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

class CodeExecutionAgent(BaseAgent):
    """Agent responsible for executing Python code in a sandboxed environment"""

    def __init__(self):
        super().__init__("CodeExecutionAgent", "gpt-3.5-turbo")
        self.allowed_imports = {
            'pandas': 'pd',
            'numpy': 'np', 
            'plotly.express': 'px',
            'plotly.graph_objects': 'go',
            'plotly.subplots': 'make_subplots',
            'matplotlib.pyplot': 'plt',
            'seaborn': 'sns',
            'scipy': 'scipy',
            'sklearn': 'sklearn',
            'datetime': 'datetime',
            'math': 'math',
            'statistics': 'statistics',
            're': 're',
            'json': 'json'
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process code execution request"""
        code = input_data.get('code', '')
        df = input_data.get('dataframe')
        command = input_data.get('command', '')

        if not code:
            # Generate code if not provided
            code = self.generate_code(command, df)

        if not code:
            return {'error': 'No code to execute'}

        try:
            result = self.execute_code_safely(code, df)
            return {
                'success': result['success'],
                'output': result.get('output', ''),
                'error': result.get('error', ''),
                'charts': result.get('charts', []),
                'data': result.get('data'),
                'code_used': code
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'code_used': code
            }

    def generate_code(self, command: str, df: pd.DataFrame) -> str:
        """Generate Python code based on natural language command"""
        if not command or df is None:
            return ""

        # Analyze data structure
        data_info = self.analyze_dataframe(df)

        # Create context-aware prompt
        prompt = f"""
        Generate Python code to analyze the following dataset based on the user's request.

        User Request: "{command}"

        Dataset Info:
        - Shape: {data_info['shape']}
        - Columns: {', '.join(data_info['columns'][:10])}
        - Numeric columns: {', '.join([col for col in data_info['columns'] if col in df.select_dtypes(include=['number']).columns][:5])}
        - Categorical columns: {', '.join([col for col in data_info['columns'] if col in df.select_dtypes(include=['object']).columns][:5])}

        Requirements:
        1. The dataframe is available as 'df'
        2. Use appropriate libraries (pandas, plotly, numpy)
        3. Create visualizations if requested
        4. Include error handling
        5. Print or return meaningful results
        6. Use plotly for charts (available as px and go)

        Generate clean, executable Python code:
        """

        try:
            response = self.generate_response(prompt, max_tokens=1500)

            # Extract code from response
            code_match = re.search(r'```python\n(.*?)```', response, re.DOTALL)
            if code_match:
                return code_match.group(1).strip()

            # Try to find code without markdown
            lines = response.split('\n')
            code_lines = []
            in_code = False

            for line in lines:
                if line.strip().startswith(('import ', 'from ', 'df', 'print', 'fig', '#', 'result')):
                    in_code = True
                if in_code:
                    code_lines.append(line)

            if code_lines:
                return '\n'.join(code_lines)

        except Exception as e:
            print(f"Error generating code: {e}")

        return ""

    def execute_code_safely(self, code: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Execute code in a controlled environment"""
        if not self.validate_code(code):
            return {
                'success': False,
                'error': 'Code contains potentially unsafe operations'
            }

        # Capture output
        output_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output_buffer

        # Prepare execution environment
        exec_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'type': type,
                'isinstance': isinstance,
                'hasattr': hasattr,
                'getattr': getattr,
                'min': min,
                'max': max,
                'sum': sum,
                'abs': abs,
                'round': round,
                'sorted': sorted
            },
            'df': df.copy() if df is not None else None,
            'pd': pd,
            'np': np,
            'px': px,
            'go': go,
            'make_subplots': __import__('plotly.subplots', fromlist=['make_subplots']).make_subplots
        }

        exec_locals = {}
        charts = []
        result_data = None

        try:
            # Execute the code
            exec(code, exec_globals, exec_locals)

            # Capture any plotly figures created
            for var_name, var_value in exec_locals.items():
                if isinstance(var_value, (go.Figure, go.FigureWidget)):
                    charts.append(var_value)
                elif isinstance(var_value, pd.DataFrame) and var_name in ['result', 'output', 'final']:
                    result_data = var_value

            # Also check if 'fig' was created in globals
            if 'fig' in exec_locals and isinstance(exec_locals['fig'], (go.Figure, go.FigureWidget)):
                if exec_locals['fig'] not in charts:
                    charts.append(exec_locals['fig'])

        except Exception as e:
            sys.stdout = old_stdout
            return {
                'success': False,
                'error': f"Execution error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            }
        finally:
            sys.stdout = old_stdout

        output = output_buffer.getvalue()

        return {
            'success': True,
            'output': output,
            'charts': charts,
            'data': result_data
        }

    def validate_code(self, code: str) -> bool:
        """Validate code for safety"""
        # List of dangerous operations
        dangerous_patterns = [
            r'\bopen\s*\(',
            r'\bfile\s*\(',
            r'\bexec\s*\(',
            r'\beval\s*\(',
            r'\b__import__\s*\(',
            r'\bsubprocess\s*\.',
            r'\bos\s*\.',
            r'\bsys\s*\.',
            r'\bimport\s+os\b',
            r'\bimport\s+sys\b',
            r'\bimport\s+subprocess\b',
            r'\bfrom\s+os\s+import',
            r'\bfrom\s+sys\s+import',
            r'\bfrom\s+subprocess\s+import',
            r'\brm\s+',
            r'\bdel\s+',
            r'\b__.*__\b',
            r'\bgetattr\s*\(',
            r'\bsetattr\s*\(',
            r'\bdelattr\s*\(',
            r'\bglobals\s*\(',
            r'\blocals\s*\(',
            r'\bvars\s*\(',
        ]

        # Check for dangerous patterns
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False

        # Check for allowed imports only
        import_pattern = r'import\s+([\w\.]+)|from\s+([\w\.]+)\s+import'
        imports = re.findall(import_pattern, code)

        for imp in imports:
            module = imp[0] or imp[1]
            if module and module not in self.allowed_imports and not any(module.startswith(allowed) for allowed in self.allowed_imports):
                return False

        return True

    def create_sample_code_templates(self, df: pd.DataFrame) -> Dict[str, str]:
        """Create sample code templates based on data"""
        templates = {}

        if df is None:
            return templates

        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        # Basic statistics template
        templates['statistics'] = """
# Basic statistics
print("Dataset Shape:", df.shape)
print("\nSummary Statistics:")
print(df.describe())

# Missing values
print("\nMissing Values:")
print(df.isnull().sum())
"""

        # Visualization templates
        if len(numeric_cols) >= 2:
            templates['scatter_plot'] = f"""
# Scatter plot
import plotly.express as px

fig = px.scatter(df, x='{numeric_cols[0]}', y='{numeric_cols[1]}', 
                 title='{numeric_cols[1]} vs {numeric_cols[0]}')
fig.show()
"""

        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            templates['bar_chart'] = f"""
# Bar chart
import plotly.express as px

# Group data
grouped = df.groupby('{categorical_cols[0]}')['{numeric_cols[0]}'].mean().reset_index()

fig = px.bar(grouped, x='{categorical_cols[0]}', y='{numeric_cols[0]}',
             title='Average {numeric_cols[0]} by {categorical_cols[0]}')
fig.show()
"""

        if len(numeric_cols) >= 1:
            templates['histogram'] = f"""
# Histogram
import plotly.express as px

fig = px.histogram(df, x='{numeric_cols[0]}', title='Distribution of {numeric_cols[0]}')
fig.show()
"""

        # Correlation template
        if len(numeric_cols) >= 3:
            templates['correlation'] = """
# Correlation matrix
import plotly.express as px

numeric_df = df.select_dtypes(include=['number'])
corr_matrix = numeric_df.corr()

fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", 
                title="Correlation Matrix")
fig.show()
"""

        return templates

    def get_code_suggestions(self, command: str, df: pd.DataFrame) -> List[str]:
        """Get code suggestions based on command and data"""
        suggestions = []

        if df is None:
            return suggestions

        templates = self.create_sample_code_templates(df)
        command_lower = command.lower()

        # Suggest based on command keywords
        if any(word in command_lower for word in ['statistics', 'summary', 'describe']):
            suggestions.append(templates.get('statistics', ''))

        if any(word in command_lower for word in ['scatter', 'relationship', 'correlation']):
            if 'scatter_plot' in templates:
                suggestions.append(templates['scatter_plot'])
            if 'correlation' in templates:
                suggestions.append(templates['correlation'])

        if any(word in command_lower for word in ['bar', 'group', 'category']):
            if 'bar_chart' in templates:
                suggestions.append(templates['bar_chart'])

        if any(word in command_lower for word in ['distribution', 'histogram']):
            if 'histogram' in templates:
                suggestions.append(templates['histogram'])

        return [s for s in suggestions if s]  # Remove empty strings
