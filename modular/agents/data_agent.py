# Data Analysis Agent
from .base_agent import BaseAgent
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import json
import re

class DataAnalysisAgent(BaseAgent):
    """Agent responsible for data analysis and filtering operations"""

    def __init__(self):
        super().__init__("DataAnalysisAgent", "gpt-3.5-turbo")
        self.supported_operations = [
            "filter", "sort", "group", "aggregate", "pivot", 
            "correlation", "statistics", "top", "bottom", "seasonality"
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data analysis request"""
        command = input_data.get('command', '')
        df = input_data.get('dataframe')

        if df is None:
            return {'error': 'No dataframe provided'}

        # Analyze the command to determine operation type
        operation = self.parse_command(command)

        try:
            result = self.execute_operation(operation, df)
            return {
                'success': True,
                'operation': operation,
                'result': result,
                'explanation': self.generate_explanation(operation, result)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Failed to execute operation: {operation['type']}"
            }

    def parse_command(self, command: str) -> Dict[str, Any]:
        """Parse natural language command into structured operation"""
        command_lower = command.lower()

        operation = {
            'type': 'unknown',
            'parameters': {}
        }

        # Define patterns for different operations
        patterns = {
            'filter': [
                r'filter.*by.*(\w+)',
                r'where.*(\w+)',
                r'show.*(\w+).*equal.*(\w+)',
                r'(\w+).*greater than.*(\d+)',
                r'(\w+).*less than.*(\d+)'
            ],
            'sort': [
                r'sort.*by.*(\w+)',
                r'order.*by.*(\w+)',
                r'arrange.*by.*(\w+)'
            ],
            'group': [
                r'group.*by.*(\w+)',
                r'grouped.*by.*(\w+)',
                r'break.*down.*by.*(\w+)'
            ],
            'top': [
                r'top.*(\d+).*(\w+)',
                r'highest.*(\d+).*(\w+)',
                r'largest.*(\d+).*(\w+)'
            ],
            'correlation': [
                r'correlation.*between.*(\w+).*and.*(\w+)',
                r'relationship.*between.*(\w+).*and.*(\w+)',
                r'corr.*(\w+).*(\w+)'
            ],
            'seasonality': [
                r'seasonality.*by.*(\w+)',
                r'seasonal.*pattern.*(\w+)',
                r'trend.*over.*time.*(\w+)'
            ],
            'statistics': [
                r'statistics.*(\w+)',
                r'summary.*(\w+)',
                r'stats.*(\w+)',
                r'describe.*(\w+)'
            ]
        }

        # Match patterns
        for op_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, command_lower)
                if match:
                    operation['type'] = op_type
                    operation['parameters']['matches'] = match.groups()
                    break
            if operation['type'] != 'unknown':
                break

        # If no pattern matched, use LLM to parse
        if operation['type'] == 'unknown':
            operation = self.parse_with_llm(command)

        return operation

    def parse_with_llm(self, command: str) -> Dict[str, Any]:
        """Use LLM to parse complex commands with fallback to rule-based parsing"""
        prompt = f"""
        Parse this data analysis command into a structured operation:
        Command: "{command}"

        Return ONLY a JSON object with:
        - type: one of [filter, sort, group, aggregate, top, correlation, seasonality, statistics]
        - parameters: relevant parameters for the operation

        Example:
        {{
            "type": "top",
            "parameters": {{
                "n": 5,
                "column": "sales",
                "criteria": "highest"
            }}
        }}
        """

        try:
            response = self.generate_response(prompt, max_tokens=200)

            # Check for LLM error
            if response.startswith("LLM_ERROR:") or response.startswith("Error:"):
                print(f"⚠️ LLM parsing failed, using fallback: {response[:50]}...")
                return self.fallback_parse(command)

            # Extract JSON from response
            json_match = re.search(r'\{[^{}]*\}', response)
            if json_match:
                parsed = json.loads(json_match.group())
                # Validate the parsed result
                if 'type' in parsed and parsed['type'] != 'unknown':
                    return parsed

            print("⚠️ LLM returned invalid JSON, using fallback")
            return self.fallback_parse(command)

        except Exception as e:
            print(f"⚠️ LLM parsing exception: {e}, using fallback")
            return self.fallback_parse(command)

    def fallback_parse(self, command: str) -> Dict[str, Any]:
        """Fallback rule-based parsing when LLM fails"""
        command_lower = command.lower()

        # Enhanced fallback patterns
        if any(word in command_lower for word in ['top', 'highest', 'best', 'largest']):
            return {'type': 'top', 'parameters': {'n': 5}}
        elif any(word in command_lower for word in ['group', 'by', 'breakdown']):
            return {'type': 'group', 'parameters': {}}
        elif any(word in command_lower for word in ['sort', 'order', 'arrange']):
            return {'type': 'sort', 'parameters': {}}
        elif any(word in command_lower for word in ['filter', 'where', 'show']):
            return {'type': 'filter', 'parameters': {}}
        elif any(word in command_lower for word in ['correlation', 'relationship']):
            return {'type': 'correlation', 'parameters': {}}
        elif any(word in command_lower for word in ['seasonal', 'trend', 'time']):
            return {'type': 'seasonality', 'parameters': {}}
        elif any(word in command_lower for word in ['stats', 'statistics', 'summary', 'describe']):
            return {'type': 'statistics', 'parameters': {}}
        else:
            return {'type': 'statistics', 'parameters': {}}  # Default to statistics

    def execute_operation(self, operation: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        """Execute the parsed operation on dataframe"""
        op_type = operation['type']
        params = operation['parameters']

        if op_type == 'filter':
            return self.filter_data(df, params)
        elif op_type == 'sort':
            return self.sort_data(df, params)
        elif op_type == 'group':
            return self.group_data(df, params)
        elif op_type == 'top':
            return self.top_data(df, params)
        elif op_type == 'correlation':
            return self.correlation_analysis(df, params)
        elif op_type == 'seasonality':
            return self.seasonality_analysis(df, params)
        elif op_type == 'statistics':
            return self.statistics_analysis(df, params)
        else:
            # Default: return basic statistics
            return self.statistics_analysis(df, {})

    def filter_data(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
        """Filter dataframe based on parameters"""
        filtered_df = df.copy()

        # Simple filtering logic - can be enhanced
        if 'matches' in params and len(params['matches']) >= 2:
            column = params['matches'][0]
            value = params['matches'][1]

            if column in df.columns:
                if pd.api.types.is_numeric_dtype(df[column]):
                    try:
                        numeric_value = float(value)
                        filtered_df = df[df[column] == numeric_value]
                    except:
                        filtered_df = df[df[column].astype(str).str.contains(value, case=False, na=False)]
                else:
                    filtered_df = df[df[column].astype(str).str.contains(value, case=False, na=False)]

        return {
            'data': filtered_df,
            'operation_details': f"Filtered by {params}"
        }

    def sort_data(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sort dataframe"""
        if 'matches' in params and len(params['matches']) > 0:
            column = params['matches'][0]
            if column in df.columns:
                sorted_df = df.sort_values(by=column, ascending=False)
                return {
                    'data': sorted_df,
                    'operation_details': f"Sorted by {column} (descending)"
                }

        # Default sort by first numeric column
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            sorted_df = df.sort_values(by=numeric_cols[0], ascending=False)
            return {
                'data': sorted_df,
                'operation_details': f"Sorted by {numeric_cols[0]} (descending)"
            }

        return {'data': df, 'operation_details': "No sorting applied"}

    def group_data(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
        """Group dataframe"""
        if 'matches' in params and len(params['matches']) > 0:
            group_column = params['matches'][0]
            if group_column in df.columns:
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    grouped = df.groupby(group_column)[numeric_cols].agg(['count', 'mean', 'sum']).round(2)
                    grouped = grouped.reset_index()
                    return {
                        'data': grouped,
                        'operation_details': f"Grouped by {group_column}"
                    }

        return {'data': df.head(10), 'operation_details': "No grouping applied"}

    def top_data(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get top N records"""
        n = 5  # default
        column = None

        if 'matches' in params:
            matches = params['matches']
            if len(matches) >= 2:
                try:
                    n = int(matches[0])
                    column = matches[1]
                except:
                    column = matches[0] if matches[0] in df.columns else None
            elif len(matches) == 1:
                if matches[0].isdigit():
                    n = int(matches[0])
                else:
                    column = matches[0] if matches[0] in df.columns else None

        # If no column specified, use first numeric column
        if column is None:
            numeric_cols = df.select_dtypes(include=['number']).columns
            column = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[0]

        if column in df.columns:
            if pd.api.types.is_numeric_dtype(df[column]):
                top_data = df.nlargest(n, column)
            else:
                # For non-numeric, get top by frequency
                top_values = df[column].value_counts().head(n)
                top_data = df[df[column].isin(top_values.index)]

            return {
                'data': top_data,
                'operation_details': f"Top {n} records by {column}"
            }

        return {'data': df.head(n), 'operation_details': f"Top {n} records"}

    def correlation_analysis(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform correlation analysis"""
        numeric_df = df.select_dtypes(include=['number'])

        if len(numeric_df.columns) >= 2:
            correlation_matrix = numeric_df.corr()
            return {
                'data': correlation_matrix,
                'operation_details': "Correlation analysis of numeric columns"
            }

        return {
            'data': pd.DataFrame({'message': ['Not enough numeric columns for correlation']}),
            'operation_details': "Insufficient numeric data"
        }

    def seasonality_analysis(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze seasonal patterns"""
        # Look for date columns
        date_cols = df.select_dtypes(include=['datetime64']).columns
        if len(date_cols) == 0:
            # Try to find date-like columns
            for col in df.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    try:
                        df[col] = pd.to_datetime(df[col])
                        date_cols = [col]
                        break
                    except:
                        continue

        if len(date_cols) > 0 and len(df.select_dtypes(include=['number']).columns) > 0:
            date_col = date_cols[0]
            numeric_col = df.select_dtypes(include=['number']).columns[0]

            # Extract time components
            df_seasonal = df.copy()
            df_seasonal['month'] = pd.to_datetime(df_seasonal[date_col]).dt.month
            df_seasonal['quarter'] = pd.to_datetime(df_seasonal[date_col]).dt.quarter
            df_seasonal['year'] = pd.to_datetime(df_seasonal[date_col]).dt.year

            seasonal_data = df_seasonal.groupby(['year', 'month'])[numeric_col].sum().reset_index()

            return {
                'data': seasonal_data,
                'operation_details': f"Seasonal analysis of {numeric_col} over time"
            }

        return {
            'data': df.head(),
            'operation_details': "No date columns found for seasonal analysis"
        }

    def statistics_analysis(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statistical analysis"""
        numeric_df = df.select_dtypes(include=['number'])

        if len(numeric_df.columns) > 0:
            stats = numeric_df.describe()
            return {
                'data': stats.transpose(),
                'operation_details': "Statistical summary of numeric columns"
            }

        # For non-numeric data, show value counts
        categorical_stats = {}
        for col in df.select_dtypes(include=['object']).columns[:3]:  # First 3 categorical columns
            categorical_stats[col] = df[col].value_counts().head(10)

        if categorical_stats:
            stats_df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in categorical_stats.items()]))
            return {
                'data': stats_df,
                'operation_details': "Value counts for categorical columns"
            }

        return {
            'data': df.head(),
            'operation_details': "Basic data preview"
        }

    def generate_explanation(self, operation: Dict[str, Any], result: Dict[str, Any]) -> str:
        """Generate human-readable explanation of the operation"""
        op_type = operation.get('type', 'unknown')
        details = result.get('operation_details', '')

        explanations = {
            'filter': f"I filtered the data based on your criteria. {details}",
            'sort': f"I sorted the data to show you the ordered results. {details}",
            'group': f"I grouped the data to show aggregated insights. {details}",
            'top': f"I found the top records based on your request. {details}",
            'correlation': f"I calculated correlations between numeric variables. {details}",
            'seasonality': f"I analyzed seasonal patterns in your data. {details}",
            'statistics': f"I computed statistical summaries of your data. {details}"
        }

        return explanations.get(op_type, f"I performed a {op_type} operation on your data. {details}")
