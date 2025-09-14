# Agent Coordinator
from typing import Dict, Any, List, Optional
import pandas as pd
from .data_agent import DataAnalysisAgent
from .meta_prompt_agent import MetaPromptAgent
from .visualization_agent import VisualizationAgent
from .code_execution_agent import CodeExecutionAgent

class AgentCoordinator:
    """Coordinates communication between different agents"""

    def __init__(self, openai_api_key: str):
        self.api_key = openai_api_key

        # Initialize agents
        self.data_agent = DataAnalysisAgent()
        self.meta_prompt_agent = MetaPromptAgent()
        self.visualization_agent = VisualizationAgent()
        self.code_execution_agent = CodeExecutionAgent()

        # Initialize all agents with API key
        for agent in [self.data_agent, self.meta_prompt_agent, self.visualization_agent, self.code_execution_agent]:
            agent.initialize_model(openai_api_key)

    def process_command(self, command: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Process user command through multi-agent workflow with enhanced error handling"""
        print(f"🔄 Processing command: '{command}'")

        try:
            # Step 1: Meta-prompt agent analyzes context and creates prompts
            print("📋 Step 1: Meta-prompt analysis...")
            meta_input = {
                'command': command,
                'dataframe': df,
                'target_agent': 'data'
            }
            meta_result = self.meta_prompt_agent.process(meta_input)
            print(f"✅ Meta analysis complete. Intent: {meta_result.get('context', {}).get('intent', 'unknown')}")

            # Step 2: Data analysis agent processes the command
            print("🔍 Step 2: Data analysis...")
            data_input = {
                'command': command,
                'dataframe': df,
                'context': meta_result.get('context', {})
            }
            data_result = self.data_agent.process(data_input)

            if not data_result.get('success', False):
                error_msg = data_result.get('error', 'Data analysis failed')
                print(f"❌ Data analysis failed: {error_msg}")
                return {
                    'error': error_msg,
                    'explanation': data_result.get('explanation', 'Data processing encountered an error')
                }

            print(f"✅ Data analysis complete. Operation: {data_result.get('operation', {}).get('type', 'unknown')}")

            # Step 3: Visualization agent creates interactive options or charts
            print("📊 Step 3: Creating visualizations...")
            viz_result = {'success': False, 'charts': [], 'explanation': ''}

            try:
                # Check if user wants direct visualization or interactive options
                viz_keywords = ['chart', 'graph', 'plot', 'visualize', 'show me']
                wants_direct_viz = any(keyword in command.lower() for keyword in viz_keywords)

                viz_input = {
                    'command': command,
                    'dataframe': df,
                    'analysis_result': data_result.get('result', {}),
                    'interactive_mode': not wants_direct_viz  # Interactive by default unless specific viz requested
                }
                viz_result = self.visualization_agent.process(viz_input)

                if viz_result.get('success'):
                    if 'interactive_options' in viz_result:
                        print("✅ Interactive visualization options generated")
                    else:
                        print(f"✅ Visualization complete. Charts: {len(viz_result.get('charts', []))}")
                else:
                    print("⚠️ Visualization failed, continuing without charts")
            except Exception as viz_error:
                print(f"⚠️ Visualization error: {viz_error}, continuing without charts")

            # Step 4: Generate AI insights
            print("🧠 Step 4: Generating AI insights...")
            ai_insights = self.generate_ai_insights(command, data_result, df)

            # Step 5: Combine results
            print("🔗 Step 5: Combining results...")
            result_data = data_result.get('result', {}).get('data')
            final_result = {
                'explanation': data_result.get('explanation', 'Analysis completed successfully'),
                'ai_insights': ai_insights,
                'data': result_data,
                'operation': data_result.get('operation', {}),
                'workflow_success': True
            }

            # Add visualization results (either interactive options or direct charts)
            if viz_result.get('success'):
                if 'interactive_options' in viz_result:
                    final_result['interactive_options'] = viz_result['interactive_options']
                    final_result['viz_explanation'] = viz_result.get('explanation', 'Interactive visualization options available')
                else:
                    final_result['charts'] = viz_result.get('charts', [])
                    final_result['viz_explanation'] = viz_result.get('explanation', '')
            else:
                final_result['charts'] = []
                final_result['viz_explanation'] = 'No visualization created'

            if result_data is not None:
                print(f"✅ Workflow complete! Returned {len(result_data)} rows")
            else:
                print("⚠️ Workflow complete but no data returned")

            return final_result

        except Exception as e:
            error_msg = f"Workflow coordination error: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            print(f"🔍 Traceback: {traceback.format_exc()[:200]}...")
            return {
                'error': error_msg,
                'explanation': 'The agentic workflow encountered an unexpected error',
                'workflow_success': False
            }

    def execute_code(self, code: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Execute code through code execution agent"""
        code_input = {
            'code': code,
            'dataframe': df
        }

        return self.code_execution_agent.process(code_input)

    def generate_ai_insights(self, command: str, data_result: Dict[str, Any], original_df: pd.DataFrame) -> str:
        """Generate AI-powered insights about the analysis results"""
        try:
            result_data = data_result.get('result', {}).get('data')
            operation = data_result.get('operation', {})
            op_type = operation.get('type', 'unknown')

            # Prepare data summary for AI analysis
            if result_data is not None and not result_data.empty:
                data_summary = {
                    'shape': result_data.shape,
                    'columns': list(result_data.columns),
                    'sample_values': result_data.head(3).to_dict('records') if len(result_data) > 0 else [],
                    'numeric_summary': {}
                }

                # Add numeric summaries
                numeric_cols = result_data.select_dtypes(include=['number']).columns
                for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                    if not result_data[col].empty:
                        data_summary['numeric_summary'][col] = {
                            'min': float(result_data[col].min()) if not pd.isna(result_data[col].min()) else 0,
                            'max': float(result_data[col].max()) if not pd.isna(result_data[col].max()) else 0,
                            'mean': float(result_data[col].mean()) if not pd.isna(result_data[col].mean()) else 0
                        }
            else:
                data_summary = {'message': 'No specific data returned from analysis'}

            # Create AI insight prompt
            insight_prompt = f"""
            You are a data analyst AI. Analyze the following data analysis results and provide clear, actionable insights in simple English.

            User's Question: "{command}"
            Analysis Type: {op_type}
            Original Dataset: {original_df.shape[0]} rows, {original_df.shape[1]} columns

            Results Summary: {data_summary}

            Provide insights that include:
            1. What the data shows (key findings)
            2. What this means in business/practical terms
            3. Any interesting patterns or outliers
            4. Actionable recommendations

            Keep your response conversational and under 200 words. Focus on insights that would be valuable to a business user.
            """

            # Generate AI insights
            ai_response = self.data_agent.generate_response(insight_prompt, max_tokens=300)

            if ai_response.startswith("LLM_ERROR:") or ai_response.startswith("Error:"):
                return self.generate_fallback_insights(command, data_result, original_df)

            return ai_response.strip()

        except Exception as e:
            print(f"⚠️ AI insights generation failed: {e}")
            return self.generate_fallback_insights(command, data_result, original_df)

    def generate_fallback_insights(self, command: str, data_result: Dict[str, Any], original_df: pd.DataFrame) -> str:
        """Generate simple fallback insights when AI fails"""
        result_data = data_result.get('result', {}).get('data')
        operation = data_result.get('operation', {})
        op_type = operation.get('type', 'analysis')

        if result_data is not None and not result_data.empty:
            insights = f"""
**Key Findings from {op_type.title()} Analysis:**

📊 **Data Overview:** Found {len(result_data)} records from your {op_type} analysis of {len(original_df)} total records.

📈 **What This Shows:** The {op_type} operation revealed patterns in your data that can help you understand {'relationships between variables' if op_type == 'correlation' else 'the distribution and trends' if op_type == 'statistics' else 'the top performers' if op_type == 'top' else 'how your data groups'}.

💡 **Next Steps:** Consider exploring related metrics or diving deeper into specific segments that show interesting patterns.
            """
        else:
            insights = f"Completed {op_type} analysis on your dataset. The operation processed {len(original_df)} records successfully."

        return insights.strip()

    def generate_suggestions(self, df: pd.DataFrame) -> List[str]:
        """Generate analysis suggestions"""
        try:
            return self.meta_prompt_agent.generate_suggestions(df)
        except Exception:
            return [
                "Show summary statistics for numeric columns",
                "Display value counts for categorical variables", 
                "Create correlation matrix for numeric data",
                "Analyze missing values in the dataset",
                "Show top 10 records by first numeric column"
            ]

    def get_agent_status(self) -> Dict[str, bool]:
        """Get status of all agents"""
        return {
            'data_agent': hasattr(self.data_agent, 'client') and self.data_agent.client is not None,
            'meta_prompt_agent': hasattr(self.meta_prompt_agent, 'client') and self.meta_prompt_agent.client is not None,
            'visualization_agent': hasattr(self.visualization_agent, 'client') and self.visualization_agent.client is not None,
            'code_execution_agent': hasattr(self.code_execution_agent, 'client') and self.code_execution_agent.client is not None
        }
