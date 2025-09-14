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

            # Add more specific business context
            context_info = f"Top {n} records by {column}"
            if pd.api.types.is_numeric_dtype(df[column]):
                max_val = top_data[column].max()
                min_val = top_data[column].min()
                context_info += f" (range: {min_val:.1f} to {max_val:.1f})"

                # Add quarterly/time context if date columns exist
                date_cols = df.select_dtypes(include=['datetime64']).columns
                if len(date_cols) > 0:
                    date_col = date_cols[0]
                    if date_col in top_data.columns:
                        # Get time period info
                        try:
                            latest_date = top_data[date_col].max()
                            earliest_date = top_data[date_col].min()
                            context_info += f" (time period: {earliest_date.strftime('%Y-%m') if hasattr(earliest_date, 'strftime') else str(earliest_date)} to {latest_date.strftime('%Y-%m') if hasattr(latest_date, 'strftime') else str(latest_date)})"
                        except:
                            pass

            return {
                'data': top_data,
                'operation_details': context_info
            }

        return {'data': df.head(n), 'operation_details': f"Top {n} records"}

    def correlation_analysis(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform detailed correlation analysis with specific insights"""
        numeric_df = df.select_dtypes(include=['number'])

        if len(numeric_df.columns) >= 2:
            correlation_matrix = numeric_df.corr()

            # Find strongest correlations
            strongest_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    col1 = correlation_matrix.columns[i]
                    col2 = correlation_matrix.columns[j]
                    corr_val = correlation_matrix.iloc[i, j]
                    if abs(corr_val) > 0.5:  # Strong correlation threshold
                        strongest_correlations.append(f"{col1} vs {col2}: {corr_val:.3f}")

            correlation_details = f"Analyzed {len(numeric_df.columns)} numeric columns"
            if strongest_correlations:
                correlation_details += f". Strong relationships found: {'; '.join(strongest_correlations[:3])}"
            else:
                correlation_details += ". No strong correlations (>0.5) detected"

            return {
                'data': correlation_matrix,
                'operation_details': correlation_details
            }

        return {
            'data': pd.DataFrame({'message': ['Not enough numeric columns for correlation']}),
            'operation_details': f"Need at least 2 numeric columns. Found: {list(numeric_df.columns)}"
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
        """Generate detailed human-readable explanation with specific column impacts"""
        op_type = operation.get('type', 'unknown')
        details = result.get('operation_details', '')
        data = result.get('data')

        # Get column names and specific insights
        column_specific_info = ""
        if data is not None and not data.empty:
            key_columns = list(data.columns)[:3]  # Focus on first 3 columns

            # Add specific column information
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = data.select_dtypes(include=['object', 'string']).columns.tolist()

            if numeric_cols:
                top_numeric = numeric_cols[0]
                try:
                    if len(data) > 0:
                        max_val = data[top_numeric].max()
                        min_val = data[top_numeric].min()
                        column_specific_info = f" The key numeric column '{top_numeric}' ranges from {min_val:.1f} to {max_val:.1f}."
                except:
                    column_specific_info = f" Focusing on numeric column '{top_numeric}'."

            if categorical_cols and len(categorical_cols) > 0:
                top_categorical = categorical_cols[0]
                try:
                    if len(data) > 0:
                        unique_vals = data[top_categorical].nunique()
                        top_category = data[top_categorical].value_counts().index[0] if len(data[top_categorical].value_counts()) > 0 else "N/A"
                        column_specific_info += f" The categorical column '{top_categorical}' has {unique_vals} unique values, with '{top_category}' being most common."
                except:
                    column_specific_info += f" Analyzing categorical column '{top_categorical}'."

        enhanced_explanations = {
            'filter': f"I filtered the data based on your criteria ({details}), resulting in {len(data) if data is not None else 0} matching records.{column_specific_info}",
            'sort': f"I sorted the data by priority ({details}), arranging {len(data) if data is not None else 0} records to show the most important first.{column_specific_info}",
            'group': f"I grouped the data for aggregated analysis ({details}), creating {len(data) if data is not None else 0} summary groups.{column_specific_info}",
            'top': f"I identified the top-performing records ({details}), showing {len(data) if data is not None else 0} highest-ranking entries.{column_specific_info}",
            'correlation': f"I analyzed relationships between numeric variables ({details}), examining {len(data.columns) if data is not None else 0} correlation patterns.{column_specific_info}",
            'seasonality': f"I analyzed time-based patterns ({details}), identifying {len(data) if data is not None else 0} seasonal data points.{column_specific_info}",
            'statistics': f"I computed comprehensive statistical analysis ({details}), summarizing {len(data) if data is not None else 0} data points.{column_specific_info}"
        }

        return enhanced_explanations.get(op_type, f"I performed a detailed {op_type} analysis on your data ({details}), processing {len(data) if data is not None else 0} records.{column_specific_info}")
