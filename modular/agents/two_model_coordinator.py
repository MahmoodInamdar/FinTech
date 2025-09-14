# Two-Model System Coordinator
from typing import Dict, Any, List
import pandas as pd
from .data_context_analyzer import DataContextAnalyzer  # Model 2
from .data_analyst_chatbot import DataAnalystChatbot      # Model 1

class TwoModelCoordinator:
    """
    Coordinates the 2-model workflow:
    1. Model 2 (Data Context Analyzer) - Analyzes data and creates system prompt
    2. Model 1 (Data Analyst Chatbot) - Acts as stakeholder-facing analyst with dynamic context
    """

    def __init__(self, openai_api_key: str):
        self.api_key = openai_api_key
        self.current_data = None
        self.data_context_ready = False

        # Initialize the two models
        print("🚀 Initializing 2-Model System...")
        self.model_2_context_analyzer = DataContextAnalyzer()  # Model 2: Data Context
        self.model_1_analyst_chatbot = DataAnalystChatbot()    # Model 1: Chatbot Analyst

        # Initialize both models with API key
        self.model_2_context_analyzer.initialize_model(openai_api_key)

        print("✅ 2-Model System initialized successfully")

    def load_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Load new data and trigger the 2-model workflow:
        1. Model 2 analyzes data and generates context
        2. Model 1 receives the context and becomes ready for stakeholder questions
        """
        try:
            print("📊 Loading new data into 2-Model System...")
            self.current_data = df

            # STEP 1: Model 2 analyzes data and generates context
            print("🔍 Step 1: Model 2 analyzing data and generating context...")
            system_prompt = self.model_2_context_analyzer.analyze_data_and_generate_context(df)

            # STEP 2: Model 1 receives context and data access
            print("💬 Step 2: Configuring Model 1 with generated context...")
            self.model_1_analyst_chatbot.set_context_and_data(system_prompt, df, self.api_key)

            self.data_context_ready = True

            print("✅ 2-Model System ready for stakeholder conversations")

            return {
                'success': True,
                'message': 'Data analyzed and chatbot prepared for stakeholder questions',
                'data_shape': f"{len(df)} rows × {len(df.columns)} columns",
                'system_prompt_preview': system_prompt[:200] + "..." if len(system_prompt) > 200 else system_prompt
            }

        except Exception as e:
            print(f"❌ Error in data loading workflow: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to initialize 2-model system with data'
            }

    def chat_with_analyst(self, user_message: str) -> Dict[str, Any]:
        """
        Handle stakeholder conversation with Model 1 (Data Analyst Chatbot)
        """
        if not self.data_context_ready:
            return {
                'success': False,
                'response': "Please upload data first so I can analyze it and provide insights.",
                'visualizations': []
            }

        try:
            print(f"💬 Stakeholder Question: '{user_message}'")

            # Model 1 handles the conversation with full context
            chat_result = self.model_1_analyst_chatbot.chat(user_message)

            if chat_result['success']:
                print("✅ Model 1 provided analytical response")

                return {
                    'success': True,
                    'response': chat_result['response'],
                    'visualizations': chat_result.get('visualizations', []),
                    'follow_up_suggestions': chat_result.get('follow_up_suggestions', []),
                    'conversation_ready': True
                }
            else:
                print("⚠️ Model 1 encountered an issue")
                return chat_result

        except Exception as e:
            print(f"❌ Error in chat workflow: {e}")
            return {
                'success': False,
                'response': "I apologize, but I encountered an issue. Please try rephrasing your question.",
                'error': str(e),
                'visualizations': []
            }

    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of current data for display purposes"""
        if self.current_data is None:
            return {'message': 'No data loaded'}

        numeric_cols = self.current_data.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = self.current_data.select_dtypes(include=['object']).columns.tolist()

        return {
            'total_rows': len(self.current_data),
            'total_columns': len(self.current_data.columns),
            'numeric_columns': numeric_cols,
            'categorical_columns': categorical_cols,
            'sample_data': self.current_data.head().to_dict('records')
        }

    def suggest_initial_questions(self) -> List[str]:
        """Generate initial question suggestions for stakeholders"""
        if not self.data_context_ready or self.current_data is None:
            return ["Please upload your data first."]

        # Analyze data to suggest relevant questions
        numeric_cols = self.current_data.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = self.current_data.select_dtypes(include=['object']).columns.tolist()
        date_cols = self.current_data.select_dtypes(include=['datetime64']).columns.tolist()

        suggestions = []

        # Revenue/sales related questions
        revenue_cols = [col for col in numeric_cols if any(keyword in col.lower() for keyword in ['revenue', 'sales', 'profit', 'income'])]
        if revenue_cols:
            suggestions.append(f"How has {revenue_cols[0]} performed over time?")
            suggestions.append(f"What are the top performers in {revenue_cols[0]}?")

        # Product/category questions
        product_cols = [col for col in categorical_cols if any(keyword in col.lower() for keyword in ['product', 'category', 'type'])]
        if product_cols and revenue_cols:
            suggestions.append(f"Compare {revenue_cols[0]} across different {product_cols[0]}s")

        # Regional questions
        region_cols = [col for col in categorical_cols if any(keyword in col.lower() for keyword in ['region', 'location', 'area', 'territory'])]
        if region_cols:
            suggestions.append(f"Show performance breakdown by {region_cols[0]}")

        # Time-based questions
        if date_cols:
            suggestions.append(f"What are the seasonal trends in the data?")
            suggestions.append(f"How did performance change over different time periods?")

        # General questions
        if not suggestions:
            suggestions.extend([
                "Give me an overview of the key insights in this data",
                "What are the most important trends I should know about?",
                "Show me the top-performing segments in the data"
            ])

        return suggestions[:5]  # Return top 5 suggestions

    def reset_conversation(self):
        """Reset the conversation history"""
        if self.model_1_analyst_chatbot:
            self.model_1_analyst_chatbot.reset_conversation()
            print("🔄 Conversation history reset")

    def get_system_status(self) -> Dict[str, bool]:
        """Get status of both models"""
        return {
            'model_2_context_analyzer': hasattr(self.model_2_context_analyzer, 'client') and self.model_2_context_analyzer.client is not None,
            'model_1_analyst_chatbot': hasattr(self.model_1_analyst_chatbot, 'client') and self.model_1_analyst_chatbot.client is not None,
            'data_context_ready': self.data_context_ready,
            'data_loaded': self.current_data is not None
        }