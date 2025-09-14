# Model 2: Data Context Analyzer
from .base_agent import BaseAgent
from typing import Dict, Any, List
import pandas as pd
import numpy as np

class DataContextAnalyzer(BaseAgent):
    """
    Model 2: Analyzes data and creates contextual system prompts for the Data Analyst Chatbot
    This model understands the data structure, patterns, and insights to help Model 1 be better prepared
    """

    def __init__(self):
        super().__init__("DataContextAnalyzer", "gpt-3.5-turbo")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Required abstract method implementation - delegates to analyze_data_and_generate_context"""
        df = input_data.get('dataframe')
        if df is None:
            return {'error': 'No dataframe provided'}

        try:
            system_prompt = self.analyze_data_and_generate_context(df)
            return {
                'success': True,
                'system_prompt': system_prompt,
                'explanation': 'Data context analyzed and system prompt generated'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': 'Failed to analyze data context'
            }

    def analyze_data_and_generate_context(self, df: pd.DataFrame) -> str:
        """
        Main method: Analyzes uploaded data and generates contextual system prompt for Model 1
        """
        print("🔍 Model 2: Analyzing data structure and generating context...")

        # Step 1: Analyze data structure
        data_profile = self.analyze_data_structure(df)

        # Step 2: Identify key insights and patterns
        key_insights = self.extract_key_insights(df)

        # Step 3: Detect business context
        business_context = self.detect_business_context(df)

        # Step 4: Generate dynamic system prompt for Model 1
        system_prompt = self.generate_system_prompt(data_profile, key_insights, business_context)

        print("✅ Model 2: Context analysis complete, system prompt generated")
        return system_prompt

    def analyze_data_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze basic data structure and characteristics"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

        # Try to detect date columns that aren't properly typed
        potential_date_cols = []
        for col in categorical_cols:
            if any(keyword in col.lower() for keyword in ['date', 'time', 'year', 'month']):
                # Sample a few values to check if they look like dates
                sample_vals = df[col].dropna().head(3).astype(str).tolist()
                if any(self.looks_like_date(val) for val in sample_vals):
                    potential_date_cols.append(col)

        # Analyze numeric columns
        numeric_analysis = {}
        for col in numeric_cols:
            numeric_analysis[col] = {
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'missing_pct': float(df[col].isnull().sum() / len(df) * 100)
            }

        # Analyze categorical columns
        categorical_analysis = {}
        for col in categorical_cols:
            top_values = df[col].value_counts().head(5)
            categorical_analysis[col] = {
                'unique_count': df[col].nunique(),
                'top_values': top_values.to_dict(),
                'missing_pct': float(df[col].isnull().sum() / len(df) * 100)
            }

        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': numeric_cols,
            'categorical_columns': categorical_cols,
            'date_columns': date_cols + potential_date_cols,
            'numeric_analysis': numeric_analysis,
            'categorical_analysis': categorical_analysis
        }

    def extract_key_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract key patterns and insights from the data"""
        insights = {}

        # Find potential target variables (revenue, sales, profit, etc.)
        target_candidates = []
        numeric_cols = df.select_dtypes(include=['number']).columns

        for col in numeric_cols:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['revenue', 'sales', 'profit', 'income', 'amount', 'value', 'price']):
                target_candidates.append(col)

        insights['potential_targets'] = target_candidates

        # Find correlations between numeric variables
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            strong_correlations = []

            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    col1, col2 = numeric_cols[i], numeric_cols[j]
                    corr_val = corr_matrix.loc[col1, col2]
                    if abs(corr_val) > 0.5:
                        strong_correlations.append({
                            'columns': [col1, col2],
                            'correlation': float(corr_val),
                            'strength': 'strong' if abs(corr_val) > 0.7 else 'moderate'
                        })

            insights['correlations'] = strong_correlations

        # Analyze trends if date columns exist
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        if date_cols and target_candidates:
            date_col = date_cols[0]
            target_col = target_candidates[0]

            # Simple trend analysis
            df_sorted = df.sort_values(date_col)
            recent_trend = 'stable'

            if len(df_sorted) > 10:
                first_half_avg = df_sorted[target_col].head(len(df_sorted)//2).mean()
                second_half_avg = df_sorted[target_col].tail(len(df_sorted)//2).mean()
                change_pct = (second_half_avg - first_half_avg) / first_half_avg * 100

                if change_pct > 5:
                    recent_trend = 'increasing'
                elif change_pct < -5:
                    recent_trend = 'decreasing'

            insights['time_trends'] = {
                'date_column': date_col,
                'target_column': target_col,
                'trend': recent_trend,
                'time_span': f"{df_sorted[date_col].min()} to {df_sorted[date_col].max()}"
            }

        return insights

    def detect_business_context(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect business domain and context from column names and data"""
        context = {
            'domain': 'general',
            'entities': [],
            'metrics': [],
            'dimensions': []
        }

        all_columns = df.columns.str.lower().tolist()

        # Detect business domain
        if any(keyword in ' '.join(all_columns) for keyword in ['sales', 'revenue', 'customer', 'product', 'order']):
            context['domain'] = 'sales_commerce'
        elif any(keyword in ' '.join(all_columns) for keyword in ['patient', 'treatment', 'medical', 'diagnosis']):
            context['domain'] = 'healthcare'
        elif any(keyword in ' '.join(all_columns) for keyword in ['student', 'grade', 'course', 'education']):
            context['domain'] = 'education'
        elif any(keyword in ' '.join(all_columns) for keyword in ['employee', 'salary', 'department', 'hr']):
            context['domain'] = 'hr_finance'

        # Identify business entities
        entity_keywords = {
            'products': ['product', 'item', 'sku', 'category'],
            'customers': ['customer', 'client', 'user', 'buyer'],
            'locations': ['region', 'city', 'state', 'country', 'location'],
            'time_periods': ['date', 'time', 'year', 'month', 'quarter'],
            'transactions': ['order', 'transaction', 'purchase', 'sale']
        }

        for entity, keywords in entity_keywords.items():
            if any(any(keyword in col for keyword in keywords) for col in all_columns):
                context['entities'].append(entity)

        # Identify metrics and dimensions
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns

        context['metrics'] = numeric_cols.tolist()
        context['dimensions'] = categorical_cols.tolist()

        return context

    def generate_system_prompt(self, data_profile: Dict, insights: Dict, business_context: Dict) -> str:
        """Generate dynamic system prompt for Model 1 (Data Analyst Chatbot)"""

        # Build comprehensive system prompt
        system_prompt = f"""You are a senior data analyst chatbot speaking to business stakeholders. You have access to a dataset and should act as their trusted advisor for data-driven insights.

## DATASET CONTEXT:
You are analyzing a {business_context['domain']} dataset with {data_profile['total_rows']} rows and {data_profile['total_columns']} columns.

### DATA STRUCTURE:
- **Numeric Columns ({len(data_profile['numeric_columns'])})**: {', '.join(data_profile['numeric_columns'])}
- **Categorical Columns ({len(data_profile['categorical_columns'])})**: {', '.join(data_profile['categorical_columns'])}
- **Date Columns ({len(data_profile['date_columns'])})**: {', '.join(data_profile['date_columns'])}

### KEY BUSINESS ENTITIES:
Business entities detected: {', '.join(business_context['entities'])}
Primary metrics: {', '.join(business_context['metrics'][:5])}
Key dimensions: {', '.join(business_context['dimensions'][:5])}

### IMPORTANT INSIGHTS TO REMEMBER:"""

        # Add numeric insights
        if data_profile['numeric_analysis']:
            system_prompt += "\n**Numeric Data Insights:**\n"
            for col, stats in list(data_profile['numeric_analysis'].items())[:3]:
                system_prompt += f"- **{col}**: Range {stats['min']:.1f} to {stats['max']:.1f} (avg: {stats['mean']:.1f})\n"

        # Add correlation insights
        if insights.get('correlations'):
            system_prompt += "\n**Key Relationships:**\n"
            for corr in insights['correlations'][:3]:
                system_prompt += f"- **{corr['columns'][0]}** and **{corr['columns'][1]}** are {corr['strength']}ly correlated ({corr['correlation']:.3f})\n"

        # Add trend insights
        if insights.get('time_trends'):
            trend_info = insights['time_trends']
            system_prompt += f"\n**Time Trends:**\n- **{trend_info['target_column']}** is {trend_info['trend']} over time ({trend_info['time_span']})\n"

        # Add categorical insights
        if data_profile['categorical_analysis']:
            system_prompt += "\n**Categorical Data Insights:**\n"
            for col, info in list(data_profile['categorical_analysis'].items())[:2]:
                top_val = list(info['top_values'].keys())[0] if info['top_values'] else 'N/A'
                system_prompt += f"- **{col}**: {info['unique_count']} categories, most common is '{top_val}'\n"

        # Add behavioral instructions
        system_prompt += f"""

## YOUR ROLE & BEHAVIOR:
1. **Data Analyst Persona**: Speak like a senior data analyst presenting to stakeholders
2. **Proactive Insights**: Always provide specific insights with actual column names and values
3. **Auto-Visualization**: AUTOMATICALLY provide visualizations with your analysis - don't ask permission
4. **Business Context**: Frame everything in business terms, not just statistics
5. **Stakeholder Communication**: Use clear, non-technical language with actionable recommendations

## RESPONSE FORMAT:
For every analysis, provide:
- **Key Findings**: Specific insights with column names and values
- **Business Impact**: What this means for the business
- **Recommendations**: Actionable next steps
- **Analysis**: Deep insights based on the data patterns

## CRITICAL INSTRUCTIONS:
- NEVER ask "Would you like me to create this chart?" - Just provide the analysis
- NEVER say "A line chart would be the most suitable" - Charts will be created automatically
- Focus on DATA INSIGHTS and BUSINESS IMPLICATIONS, not visualization suggestions
- Provide specific numbers, trends, and actionable recommendations

## CONVERSATION STYLE:
- Start responses with insights, not methodology
- Use specific numbers and column names
- Explain "why" something is important for the business
- Offer to drill deeper into interesting findings
- Suggest next questions stakeholders should ask

Remember: You have full access to this {business_context['domain']} dataset and should confidently answer questions about {', '.join(business_context['entities'])} performance and trends."""

        return system_prompt

    def looks_like_date(self, value: str) -> bool:
        """Simple heuristic to check if a string looks like a date"""
        date_patterns = ['-', '/', '2019', '2020', '2021', '2022', '2023', '2024']
        return any(pattern in str(value) for pattern in date_patterns)