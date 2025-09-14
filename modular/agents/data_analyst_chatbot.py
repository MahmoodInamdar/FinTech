# Model 1: Data Analyst Chatbot
from .base_agent import BaseAgent
from .visualization_agent import VisualizationAgent
from typing import Dict, Any, List
import pandas as pd
import numpy as np

class DataAnalystChatbot(BaseAgent):
    """
    Model 1: Acts as a senior data analyst chatbot for stakeholders
    Receives dynamic system prompt from Model 2 and has direct access to data
    Provides conversational analysis with visualizations
    """

    def __init__(self):
        super().__init__("DataAnalystChatbot", "gpt-4")  # Using GPT-4 for better analysis
        self.conversation_history = []
        self.current_data = None
        self.context_prompt = ""
        self.viz_agent = VisualizationAgent()

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Required abstract method implementation - delegates to chat method"""
        user_message = input_data.get('message', input_data.get('command', ''))
        if not user_message:
            return {'error': 'No message provided'}

        try:
            chat_result = self.chat(user_message)
            return chat_result
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': 'Failed to process message'
            }

    def set_context_and_data(self, system_prompt: str, data: pd.DataFrame, api_key: str):
        """Set the dynamic context from Model 2 and data access"""
        self.context_prompt = system_prompt
        self.current_data = data
        self.initialize_model(api_key)
        if self.viz_agent:
            self.viz_agent.initialize_model(api_key)

        print("💬 Model 1: Data Analyst Chatbot initialized with context")

    def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Main chat method - responds like a data analyst to stakeholder questions
        """
        print(f"💬 Model 1: Processing stakeholder question: '{user_message}'")

        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": user_message})

            # Analyze the question to determine response strategy
            response_strategy = self.analyze_question_intent(user_message)

            # Generate analytical response
            analytical_response = self.generate_analyst_response(user_message, response_strategy)

            # Generate visualizations if appropriate
            visualizations = self.generate_visualizations(user_message, response_strategy)

            # Add assistant response to history
            self.conversation_history.append({"role": "assistant", "content": analytical_response})

            return {
                'success': True,
                'response': analytical_response,
                'visualizations': visualizations,
                'follow_up_suggestions': self.generate_follow_up_questions(response_strategy),
                'strategy': response_strategy
            }

        except Exception as e:
            error_response = f"I apologize, but I encountered an issue analyzing your question. Let me try to help with the data I have available. Could you rephrase your question or ask about a specific aspect of the data?"

            return {
                'success': False,
                'response': error_response,
                'error': str(e),
                'visualizations': []
            }

    def analyze_question_intent(self, question: str) -> Dict[str, Any]:
        """Analyze user question to determine the best response strategy"""
        question_lower = question.lower()

        strategy = {
            'type': 'general_analysis',
            'focus_columns': [],
            'analysis_type': 'descriptive',
            'time_based': False,
            'comparison': False,
            'visualization_needed': True
        }

        # Detect question type
        if any(word in question_lower for word in ['trend', 'over time', 'seasonal', 'quarter', 'month', 'year']):
            strategy['type'] = 'time_analysis'
            strategy['time_based'] = True
            strategy['analysis_type'] = 'trend'

        elif any(word in question_lower for word in ['compare', 'vs', 'versus', 'difference', 'between']):
            strategy['type'] = 'comparative_analysis'
            strategy['comparison'] = True
            strategy['analysis_type'] = 'comparative'

        elif any(word in question_lower for word in ['top', 'best', 'highest', 'maximum', 'bottom', 'worst', 'lowest']):
            strategy['type'] = 'performance_analysis'
            strategy['analysis_type'] = 'ranking'

        elif any(word in question_lower for word in ['correlation', 'relationship', 'related', 'connected']):
            strategy['type'] = 'correlation_analysis'
            strategy['analysis_type'] = 'relationship'

        elif any(word in question_lower for word in ['summary', 'overview', 'general', 'what is', 'tell me about']):
            strategy['type'] = 'overview_analysis'
            strategy['analysis_type'] = 'descriptive'

        # Detect column focus
        if self.current_data is not None:
            for column in self.current_data.columns:
                if column.lower() in question_lower:
                    strategy['focus_columns'].append(column)

        return strategy

    def generate_analyst_response(self, question: str, strategy: Dict[str, Any]) -> str:
        """Generate analytical response using the dynamic context"""

        # Build conversation context with dynamic system prompt
        messages = [{"role": "system", "content": self.context_prompt}]

        # Add recent conversation history (last 4 messages for context)
        recent_history = self.conversation_history[-4:] if len(self.conversation_history) > 4 else self.conversation_history
        messages.extend(recent_history)

        # Add current question with analysis guidance
        analysis_guidance = self.get_analysis_guidance(strategy)

        guided_question = f"""
        {question}

        Analysis Guidance:
        - Question Type: {strategy['type']}
        - Focus: {strategy['analysis_type']}
        - Key Columns: {', '.join(strategy['focus_columns']) if strategy['focus_columns'] else 'Auto-detect'}

        {analysis_guidance}

        Provide specific insights with actual data values, column names, and business recommendations.
        """

        messages.append({"role": "user", "content": guided_question})

        # Generate response
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=600,
                temperature=0.1
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return self.generate_fallback_response(question, strategy)

    def get_analysis_guidance(self, strategy: Dict[str, Any]) -> str:
        """Provide specific analysis guidance based on question type"""

        guidance_map = {
            'time_analysis': "Focus on time-based trends, seasonal patterns, growth rates, and period-over-period comparisons. Identify specific time periods with notable changes.",

            'comparative_analysis': "Compare different segments, categories, or groups. Show specific differences in metrics and explain what drives the variations.",

            'performance_analysis': "Identify top and bottom performers with specific rankings and values. Explain what makes the best performers successful.",

            'correlation_analysis': "Find and explain relationships between variables. Use correlation coefficients and explain business implications.",

            'overview_analysis': "Provide a comprehensive summary of key metrics, distributions, and overall health of the business.",

            'general_analysis': "Analyze the data comprehensively and provide actionable insights relevant to the business context."
        }

        return guidance_map.get(strategy['type'], guidance_map['general_analysis'])

    def generate_visualizations(self, question: str, strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate appropriate visualizations based on the question"""

        if not self.viz_agent or self.current_data is None:
            print("⚠️ No visualization agent or data available")
            return []

        try:
            # Always generate visualizations for most questions - be more aggressive
            question_lower = question.lower()

            # Don't skip visualization for most questions - always try to show charts
            should_visualize = True  # Always try to visualize unless it's a very basic question

            # Only skip for very basic greeting-like questions
            basic_questions = ['hello', 'hi', 'thanks', 'thank you', 'bye', 'goodbye']
            if any(basic in question_lower for basic in basic_questions) and len(question.split()) <= 3:
                should_visualize = False

            if not should_visualize:
                return []

            print(f"🎨 Generating visualization for question: {question}")

            # Determine visualization type based on strategy
            viz_request = self.build_visualization_request(question, strategy)
            print(f"📊 Visualization request: {viz_request}")

            # Use visualization agent to create charts
            viz_input = {
                'command': viz_request,
                'dataframe': self.current_data,
                'interactive_mode': False  # Direct visualization for chatbot
            }

            viz_result = self.viz_agent.process(viz_input)
            print(f"🔍 Visualization result success: {viz_result.get('success')}")

            if viz_result.get('success'):
                charts = viz_result.get('charts', [])
                print(f"📈 Generated {len(charts)} charts")

                if charts:
                    return [{
                        'chart': chart,
                        'type': strategy['type'],
                        'description': f"Visualization for {question}"
                    } for chart in charts]

            # Always try to create a fallback chart if the main process fails or produces no charts
            print("🔄 Creating fallback visualization...")
            fallback_chart = self.create_simple_comparison_chart(question)
            if fallback_chart:
                return [{
                    'chart': fallback_chart,
                    'type': 'fallback_comparison',
                    'description': f"Data visualization for {question}"
                }]

            # If all else fails, create a basic chart
            basic_chart = self.create_basic_data_chart()
            if basic_chart:
                return [{
                    'chart': basic_chart,
                    'type': 'basic_overview',
                    'description': f"Data overview chart"
                }]

        except Exception as e:
            print(f"⚠️ Visualization generation failed: {e}")
            import traceback
            print(f"🔍 Traceback: {traceback.format_exc()[:200]}")

        return []

    def build_visualization_request(self, question: str, strategy: Dict[str, Any]) -> str:
        """Build appropriate visualization request based on analysis strategy"""
        question_lower = question.lower()

        # Specific visualization requests based on question type
        if any(word in question_lower for word in ['region', 'area', 'territory']) and any(word in question_lower for word in ['revenue', 'sales', 'income']):
            return "compare revenue by regions with bar chart"

        elif any(word in question_lower for word in ['product', 'item']) and any(word in question_lower for word in ['revenue', 'sales']):
            return "compare sales by products with bar chart"

        elif any(word in question_lower for word in ['time', 'trend', 'over time', 'quarter', 'month']):
            return "show sales trends over time with line chart"

        elif any(word in question_lower for word in ['compare', 'comparison', 'vs', 'versus']):
            return "comparative analysis with bar chart"

        elif any(word in question_lower for word in ['top', 'best', 'highest', 'most']):
            return "show top performers with bar chart"

        # Default strategy-based requests
        viz_requests = {
            'time_analysis': "show trend over time with line chart",
            'comparative_analysis': "compare categories with bar chart",
            'performance_analysis': "show top performers with bar chart",
            'correlation_analysis': "correlation analysis with heatmap",
            'overview_analysis': "summary visualization with multiple charts",
            'general_analysis': "create relevant bar chart for comparison"
        }

        base_request = viz_requests.get(strategy['type'], 'create bar chart visualization')

        # Add column focus if available
        if strategy['focus_columns']:
            focus_cols = ', '.join(strategy['focus_columns'])
            base_request += f" focusing on {focus_cols}"

        return base_request

    def create_simple_comparison_chart(self, question: str):
        """Create a simple fallback comparison chart"""
        try:
            import plotly.express as px
            import plotly.graph_objects as go

            question_lower = question.lower()

            # Find appropriate columns based on question
            numeric_cols = self.current_data.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = self.current_data.select_dtypes(include=['object']).columns.tolist()

            # Revenue/sales column
            revenue_col = None
            for col in numeric_cols:
                if any(keyword in col.lower() for keyword in ['revenue', 'sales', 'amount', 'value', 'income', 'profit']):
                    revenue_col = col
                    break

            if not revenue_col and numeric_cols:
                revenue_col = numeric_cols[0]

            # Category column based on question
            category_col = None
            if 'region' in question_lower:
                for col in categorical_cols:
                    if 'region' in col.lower():
                        category_col = col
                        break
            elif 'product' in question_lower:
                for col in categorical_cols:
                    if 'product' in col.lower():
                        category_col = col
                        break

            if not category_col and categorical_cols:
                category_col = categorical_cols[0]

            if revenue_col and category_col:
                # Create comparison chart
                grouped_data = self.current_data.groupby(category_col)[revenue_col].sum().sort_values(ascending=False)

                fig = px.bar(
                    x=grouped_data.index,
                    y=grouped_data.values,
                    title=f"📊 {revenue_col} by {category_col}",
                    labels={'x': category_col, 'y': revenue_col},
                    template="plotly_white"
                )

                fig.update_traces(
                    hovertemplate=f'<b>{category_col}</b>: %{{x}}<br><b>{revenue_col}</b>: %{{y:,.0f}}<extra></extra>'
                )

                fig.update_layout(
                    height=400,
                    showlegend=False
                )

                return fig

        except Exception as e:
            print(f"⚠️ Fallback chart creation failed: {e}")

        return None

    def create_basic_data_chart(self):
        """Create a basic overview chart when all else fails"""
        try:
            import plotly.express as px
            import plotly.graph_objects as go

            if self.current_data is None or self.current_data.empty:
                return None

            # Find the best columns for a basic chart
            numeric_cols = self.current_data.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = self.current_data.select_dtypes(include=['object']).columns.tolist()

            if len(numeric_cols) >= 1:
                # Create a histogram of the first numeric column
                col = numeric_cols[0]
                fig = px.histogram(
                    self.current_data,
                    x=col,
                    title=f"📊 Distribution of {col}",
                    template="plotly_white",
                    nbins=20
                )

                fig.update_traces(
                    hovertemplate=f'<b>{col}</b>: %{{x}}<br><b>Count</b>: %{{y}}<extra></extra>'
                )

                fig.update_layout(height=400)
                return fig

            elif len(categorical_cols) >= 1:
                # Create a bar chart showing the count of categories
                col = categorical_cols[0]
                value_counts = self.current_data[col].value_counts().head(10)

                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"📊 Count by {col}",
                    labels={'x': col, 'y': 'Count'},
                    template="plotly_white"
                )

                fig.update_traces(
                    hovertemplate=f'<b>{col}</b>: %{{x}}<br><b>Count</b>: %{{y}}<extra></extra>'
                )

                fig.update_layout(height=400)
                return fig

        except Exception as e:
            print(f"⚠️ Basic chart creation failed: {e}")

        return None

    def generate_follow_up_questions(self, strategy: Dict[str, Any]) -> List[str]:
        """Generate relevant follow-up questions for stakeholders"""

        if not self.current_data is not None:
            return []

        follow_ups = {
            'time_analysis': [
                "Would you like to see this broken down by specific time periods?",
                "Should we analyze what drove these trends?",
                "How does this compare to the same period last year?"
            ],
            'comparative_analysis': [
                "Would you like to drill down into the top/bottom performers?",
                "Should we analyze what causes these differences?",
                "How do these comparisons look over different time periods?"
            ],
            'performance_analysis': [
                "What factors contributed to the top performers' success?",
                "Should we analyze the bottom performers to understand challenges?",
                "How consistent is this performance over time?"
            ],
            'correlation_analysis': [
                "Should we explore what drives these relationships?",
                "Would you like to see how these correlations vary by segment?",
                "Are there other variables we should include in this analysis?"
            ],
            'overview_analysis': [
                "Which specific area would you like to dive deeper into?",
                "Should we focus on any particular time period or segment?",
                "What business questions are you trying to answer?"
            ]
        }

        base_questions = follow_ups.get(strategy['type'], [
            "What specific aspect would you like to explore further?",
            "Should we look at this from a different angle?",
            "Are there other related questions you'd like to analyze?"
        ])

        return base_questions[:3]  # Return top 3 suggestions

    def generate_fallback_response(self, question: str, strategy: Dict[str, Any]) -> str:
        """Generate a fallback response when AI generation fails"""

        if self.current_data is None:
            return "I don't have access to data right now. Please make sure the data is loaded properly."

        # Provide basic data summary
        numeric_cols = self.current_data.select_dtypes(include=['number']).columns
        categorical_cols = self.current_data.select_dtypes(include=['object']).columns

        response = f"""I understand you're asking about: "{question}"

        Based on our {strategy['type']}, here's what I can tell you about the data:

        **Dataset Overview:**
        - Total records: {len(self.current_data):,}
        - Key metrics: {', '.join(numeric_cols[:5])}
        - Categories: {', '.join(categorical_cols[:3])}

        **Quick Insights:**"""

        if len(numeric_cols) > 0:
            top_metric = numeric_cols[0]
            avg_val = self.current_data[top_metric].mean()
            max_val = self.current_data[top_metric].max()
            response += f"\n        - {top_metric} averages {avg_val:.1f} with peak of {max_val:.1f}"

        response += "\n\n        Could you rephrase your question or ask about a specific metric? I'm here to help analyze the data for you."

        return response

    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        print("💬 Model 1: Conversation history reset")