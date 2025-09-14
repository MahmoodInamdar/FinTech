# Data Analytics Software with Multi-Agent Framework
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
import json
import io
import base64
import tempfile
import subprocess
import sys
import os
from dataclasses import dataclass
from enum import Enum
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our custom agents (will be created)
from agents.data_agent import DataAnalysisAgent
from agents.meta_prompt_agent import MetaPromptAgent
from agents.visualization_agent import VisualizationAgent
from agents.code_execution_agent import CodeExecutionAgent
from agents.coordinator import AgentCoordinator

# Page configuration
st.set_page_config(
    page_title="Data Explorer with Natural Commands",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown('''
<style>
.main-header {
    font-size: 2.5rem;
    color: #1E88E5;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #1E88E5;
}
.suggestion-button {
    background-color: #e3f2fd;
    border: 1px solid #1976d2;
    border-radius: 8px;
    padding: 0.5rem;
    margin: 0.2rem 0;
    transition: all 0.2s;
}
.suggestion-button:hover {
    background-color: #bbdefb;
    transform: translateY(-1px);
}
.operation-explain {
    background-color: #fff3e0;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #ff9800;
}
.ai-insights {
    background-color: #f3e5f5;
    padding: 1.5rem;
    border-radius: 12px;
    border-left: 4px solid #9c27b0;
    margin: 1rem 0;
    font-size: 1.05em;
    line-height: 1.6;
}
.viz-option-card {
    background-color: #f8f9fa;
    border: 2px solid #dee2e6;
    border-radius: 12px;
    padding: 1rem;
    margin: 0.5rem 0;
    transition: all 0.3s;
}
.viz-option-card:hover {
    border-color: #1E88E5;
    box-shadow: 0 2px 8px rgba(30, 136, 229, 0.2);
}
.recommendation-card {
    background-color: #e8f5e8;
    border-left: 4px solid #4caf50;
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
}
.column-selector {
    background-color: #fff3e0;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #ff9800;
    margin: 1rem 0;
}
</style>
''', unsafe_allow_html=True)

class DataApp:
    def __init__(self):
        self.coordinator = None
        self.current_data = None
        self.current_operation = ""
        self.suggestions = []

    def initialize_agents(self, openai_api_key: str):
        """Initialize the multi-agent system"""
        self.coordinator = AgentCoordinator(openai_api_key)

    def render_header(self):
        """Render the main header"""
        st.markdown('<h1 class="main-header">🔍 Data Explorer with Natural Commands</h1>', unsafe_allow_html=True)
        st.markdown("**Talk, don't tool:** Describe your data needs in everyday language and get useful insights!")

    def render_sidebar(self):
        """Render the sidebar with configuration"""
        with st.sidebar:
            st.header("⚙️ Configuration")

            # API Key input - check environment first
            env_api_key = os.getenv("OPENAI_API_KEY")

            if env_api_key:
                st.success("🔑 Using OpenAI API key from environment")
                api_key = env_api_key
            else:
                api_key = st.text_input("OpenAI API Key", type="password",
                                       help="Enter your OpenAI API key or set OPENAI_API_KEY in .env file")

            if api_key and not self.coordinator:
                try:
                    self.initialize_agents(api_key)
                    st.success("✅ Agents initialized!")
                except Exception as e:
                    st.error(f"❌ Failed to initialize agents: {e}")
                    st.info("💡 Make sure your OpenAI API key is valid and has credits")

            st.divider()

            # File upload
            st.header("📁 Data Upload")
            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type=['csv'],
                help="Upload your dataset to start analysis"
            )

            if uploaded_file:
                self.load_data(uploaded_file)

            # Sample data option
            if st.button("🎲 Load Sample Data"):
                self.load_sample_data()

            return uploaded_file

    def load_data(self, uploaded_file):
        """Load data from uploaded file"""
        try:
            self.current_data = pd.read_csv(uploaded_file)
            # Clean data for Arrow compatibility
            self.current_data = self.clean_dataframe_for_display(self.current_data)
            st.session_state.data = self.current_data
            st.sidebar.success(f"✅ Data loaded: {len(self.current_data)} rows, {len(self.current_data.columns)} columns")
        except Exception as e:
            st.sidebar.error(f"❌ Error loading data: {e}")

    def clean_dataframe_for_display(self, df):
        """Clean dataframe to avoid Arrow serialization issues"""
        df_clean = df.copy()

        for col in df_clean.columns:
            # Handle mixed types by converting to string if needed
            if df_clean[col].dtype == 'object':
                # Check if column has mixed types
                try:
                    # Try to convert to numeric first
                    pd.to_numeric(df_clean[col])
                except (ValueError, TypeError):
                    # If not numeric, convert all values to strings
                    df_clean[col] = df_clean[col].astype(str)

            # Handle any remaining problematic columns
            if df_clean[col].dtype == 'object':
                # Ensure all values are strings
                df_clean[col] = df_clean[col].fillna('').astype(str)

        return df_clean

    def load_sample_data(self):
        """Load sample data for demonstration"""
        import numpy as np

        # Generate sample sales data
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
        regions = ['North', 'South', 'East', 'West']
        products = ['Product A', 'Product B', 'Product C', 'Product D']

        n_records = 1000
        sample_data = pd.DataFrame({
            'Date': np.random.choice(dates, n_records),
            'Region': np.random.choice(regions, n_records),
            'Product': np.random.choice(products, n_records),
            'Sales': np.random.randint(100, 1000, n_records),
            'Units': np.random.randint(1, 50, n_records),
            'Customer_Age': np.random.randint(18, 70, n_records),
            'Discount': np.random.uniform(0, 0.3, n_records)
        })

        self.current_data = self.clean_dataframe_for_display(sample_data)
        st.session_state.data = self.current_data
        st.sidebar.success(f"✅ Sample data loaded: {len(self.current_data)} rows, {len(self.current_data.columns)} columns")

    def render_data_preview(self):
        """Render data preview section"""
        if self.current_data is not None:
            st.header("📋 Data Preview")

            # Quick stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Rows", len(self.current_data))
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Columns", len(self.current_data.columns))
                st.markdown('</div>', unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                numeric_cols = len(self.current_data.select_dtypes(include=['number']).columns)
                st.metric("Numeric Columns", numeric_cols)
                st.markdown('</div>', unsafe_allow_html=True)
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                missing_values = self.current_data.isnull().sum().sum()
                st.metric("Missing Values", missing_values)
                st.markdown('</div>', unsafe_allow_html=True)

            # Data preview table
            st.subheader("Sample Data")
            st.dataframe(self.current_data.head(10), width='stretch')

            # Column information
            with st.expander("📊 Column Information"):
                col_info = pd.DataFrame({
                    'Column': self.current_data.columns,
                    'Type': self.current_data.dtypes.astype(str),  # Convert dtypes to strings
                    'Non-Null Count': self.current_data.count(),
                    'Unique Values': [self.current_data[col].nunique() for col in self.current_data.columns]
                })
                st.dataframe(col_info, width='stretch')

    def render_command_interface(self):
        """Render the natural language command interface"""
        st.header("💬 Natural Language Commands")

        # Generate and display suggestions first
        if self.coordinator:
            try:
                suggestions = self.coordinator.generate_suggestions(self.current_data)
                if suggestions:
                    st.markdown("**💡 Quick suggestions (click to use):**")

                    # Create clickable buttons for suggestions in a grid
                    cols = st.columns(2)
                    for i, suggestion in enumerate(suggestions[:6]):  # Show up to 6 suggestions
                        with cols[i % 2]:
                            if st.button(f"📊 {suggestion}", key=f"suggestion_{i}", width='stretch'):
                                # Process the suggestion directly
                                self.process_command(suggestion)
                                st.rerun()

                    st.markdown("---")
            except Exception as e:
                st.info("💡 Upload data to see smart suggestions")

        # Command input
        user_command = st.text_area(
            "Or describe what you want to explore:",
            placeholder="e.g., 'show seasonality by region', 'top 5 products this quarter', 'correlation between sales and discount'",
            height=80
        )

        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🔍 Analyze Data", type="primary", width='stretch'):
                if user_command and self.coordinator:
                    self.process_command(user_command)
                elif not user_command:
                    st.warning("Please enter a command or click a suggestion above")
                elif not self.coordinator:
                    st.warning("Please enter OpenAI API key first")

        with col2:
            if st.button("🗑️ Clear Results", width='stretch'):
                self.clear_results()

    def process_command(self, command: str):
        """Process natural language command through agents"""
        try:
            with st.spinner("🤖 Agents are analyzing your request..."):
                result = self.coordinator.process_command(command, self.current_data)

                if result:
                    # Store result in session state
                    st.session_state.last_result = result

                    # Debug: Show what we got
                    if 'error' in result:
                        st.error(f"❌ Analysis Error: {result['error']}")
                        if 'explanation' in result:
                            st.info(f"💡 Details: {result['explanation']}")
                    else:
                        # Success - display results
                        self.display_results(result)
                        st.success("✅ Analysis completed successfully!")
                else:
                    st.error("Sorry, I couldn't process your command. Please try rephrasing it.")

        except Exception as e:
            st.error(f"Error processing command: {e}")
            import traceback
            st.error(f"Debug: {traceback.format_exc()[:200]}")

    def display_results(self, result: Dict[str, Any]):
        """Display analysis results"""
        st.divider()
        st.header("📊 Analysis Results")

        # Debug info
        st.write(f"**Debug:** Result keys: {list(result.keys())}")

        # Operation explanation
        if 'explanation' in result and result['explanation']:
            st.markdown(f'<div class="operation-explain"><strong>🔍 What I did:</strong> {result["explanation"]}</div>',
                       unsafe_allow_html=True)
        else:
            st.info("No explanation provided")

        # AI-powered insights
        if 'ai_insights' in result and result['ai_insights']:
            st.markdown("### 🧠 AI Analysis & Insights")
            st.markdown(f'<div class="ai-insights">{result["ai_insights"]}</div>',
                       unsafe_allow_html=True)

        # Interactive Visualizations
        if 'interactive_options' in result:
            self.render_interactive_viz_options(result['interactive_options'])
        elif 'charts' in result and result['charts']:
            st.header("📈 Visualizations")
            st.write(f"**Found {len(result['charts'])} charts**")
            for i, chart in enumerate(result['charts']):
                st.plotly_chart(chart, width='stretch', key=f"chart_{i}")
        else:
            st.info("No visualizations generated")

            # Try to create a simple fallback visualization
            if 'data' in result and result['data'] is not None:
                fallback_chart = self.create_fallback_visualization(result)
                if fallback_chart:
                    st.header("📈 Quick Visualization")
                    st.plotly_chart(fallback_chart, width='stretch', key="fallback_chart")

        # Data tables
        if 'data' in result and result['data'] is not None:
            st.header("📋 Filtered/Processed Data")
            st.write(f"**Data shape:** {result['data'].shape}")
            # Clean the result data for display
            clean_data = self.clean_dataframe_for_display(result['data'])
            st.dataframe(clean_data, width='stretch')

            # Export option
            csv_data = result['data'].to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv_data,
                file_name=f"analysis_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

        # Code snippet if generated
        if 'code' in result:
            with st.expander("🐍 Generated Python Code"):
                st.code(result['code'], language='python')

    def create_fallback_visualization(self, result: Dict[str, Any]):
        """Create a simple fallback visualization when the main viz agent fails"""
        try:
            data = result.get('data')
            operation = result.get('operation', {})
            op_type = operation.get('type', '')

            if data is None or data.empty:
                return None

            # Simple correlation heatmap for correlation analysis
            if op_type == 'correlation':
                numeric_data = data.select_dtypes(include=['number'])
                if len(numeric_data.columns) >= 2:
                    import plotly.graph_objects as go

                    # Create simple correlation heatmap
                    fig = go.Figure(data=go.Heatmap(
                        z=numeric_data.values,
                        x=numeric_data.columns,
                        y=numeric_data.index,
                        colorscale='RdBu_r',
                        hovertemplate='%{x} vs %{y}<br>Value: %{z:.2f}<extra></extra>'
                    ))

                    fig.update_layout(
                        title="Correlation Matrix",
                        xaxis_title="Variables",
                        yaxis_title="Variables"
                    )
                    return fig

            # Simple bar chart for top/group operations
            elif op_type in ['top', 'group']:
                if len(data.columns) >= 2:
                    import plotly.express as px

                    # Use first text column for x and first numeric for y
                    text_cols = data.select_dtypes(include=['object', 'string']).columns
                    numeric_cols = data.select_dtypes(include=['number']).columns

                    if len(text_cols) > 0 and len(numeric_cols) > 0:
                        x_col = text_cols[0]
                        y_col = numeric_cols[0]

                        fig = px.bar(
                            data.head(10),  # Limit to top 10 for readability
                            x=x_col,
                            y=y_col,
                            title=f"{op_type.title()} Analysis: {y_col} by {x_col}"
                        )
                        return fig

            # Simple table view for other operations
            else:
                return None

        except Exception as e:
            print(f"⚠️ Fallback visualization error: {e}")
            return None

    def render_interactive_viz_options(self, viz_options: Dict[str, Any]):
        """Render interactive visualization options for user selection"""
        st.header("📈 Interactive Visualization Options")

        # Show recommendations first
        recommendations = viz_options.get('recommendations', [])
        if recommendations:
            st.subheader("💡 Smart Recommendations")

            for i, rec in enumerate(recommendations):
                priority_color = {"high": "🔥", "medium": "⭐", "low": "💡"}
                priority_icon = priority_color.get(rec.get('priority', 'medium'), "💡")

                st.markdown(f"""
                <div class="recommendation-card">
                    <strong>{priority_icon} {rec['chart_type']}</strong><br>
                    <em>{rec['reason']}</em>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(f"Create {rec['chart_type']}", key=f"rec_{i}", type="primary"):
                        self.create_custom_visualization(rec['chart_type'], rec.get('suggested_config', {}))
                with col2:
                    if st.button("Customize", key=f"custom_rec_{i}"):
                        st.session_state[f'customize_{rec["chart_type"]}'] = True
                        st.rerun()

        # Show all available chart types
        st.subheader("📊 All Chart Types")

        available_charts = viz_options.get('available_charts', {})
        column_info = viz_options.get('column_info', {})

        # Create chart type selector in columns
        chart_names = list(available_charts.keys())
        cols = st.columns(3)

        for i, chart_name in enumerate(chart_names):
            chart_info = available_charts[chart_name]

            with cols[i % 3]:
                if chart_info.get('suitable', False):
                    if st.button(f"📊 {chart_name}", key=f"chart_{i}", width='stretch'):
                        st.session_state['selected_chart'] = chart_name
                        st.session_state['show_config'] = True
                        st.rerun()

                    st.markdown(f"<small>{chart_info['description']}</small>", unsafe_allow_html=True)
                else:
                    st.button(f"❌ {chart_name}", key=f"chart_disabled_{i}", disabled=True, width='stretch', help="Not suitable for your data")

        # Show configuration interface if chart is selected
        if st.session_state.get('show_config', False) and 'selected_chart' in st.session_state:
            self.render_chart_configuration(st.session_state['selected_chart'], column_info, available_charts)

    def render_chart_configuration(self, chart_name: str, column_info: Dict[str, Any], available_charts: Dict[str, Any]):
        """Render chart configuration interface"""
        st.subheader(f"⚙️ Configure {chart_name}")

        chart_info = available_charts.get(chart_name, {})

        with st.form(f"config_form_{chart_name}"):
            st.markdown(f"<div class='column-selector'><strong>📋 Select your data columns:</strong></div>", unsafe_allow_html=True)

            config = {}

            # Get column options
            numeric_cols = column_info.get('numeric_columns', [])
            categorical_cols = column_info.get('categorical_columns', [])
            date_cols = column_info.get('date_columns', [])
            all_cols = column_info.get('all_columns', [])

            # Chart-specific configuration
            if chart_name in ['Bar Chart', 'Box Plot']:
                config['x'] = st.selectbox('X-axis (Categories)', categorical_cols + numeric_cols, key=f'x_{chart_name}')
                config['y'] = st.selectbox('Y-axis (Values)', numeric_cols, key=f'y_{chart_name}')
                if categorical_cols:
                    config['color'] = st.selectbox('Color by (Optional)', ['None'] + categorical_cols, key=f'color_{chart_name}')

            elif chart_name == 'Line Chart':
                config['x'] = st.selectbox('X-axis', date_cols + numeric_cols, key=f'x_{chart_name}')
                config['y'] = st.selectbox('Y-axis', numeric_cols, key=f'y_{chart_name}')
                if categorical_cols:
                    config['color'] = st.selectbox('Group by (Optional)', ['None'] + categorical_cols, key=f'color_{chart_name}')

            elif chart_name == 'Scatter Plot':
                config['x'] = st.selectbox('X-axis', numeric_cols, key=f'x_{chart_name}')
                config['y'] = st.selectbox('Y-axis', [col for col in numeric_cols if col != config.get('x')], key=f'y_{chart_name}')
                if categorical_cols:
                    config['color'] = st.selectbox('Color by (Optional)', ['None'] + categorical_cols, key=f'color_{chart_name}')
                config['size'] = st.selectbox('Size by (Optional)', ['None'] + numeric_cols, key=f'size_{chart_name}')

            elif chart_name == 'Histogram':
                config['x'] = st.selectbox('Column to analyze', numeric_cols, key=f'x_{chart_name}')
                config['bins'] = st.slider('Number of bins', 10, 100, 30, key=f'bins_{chart_name}')
                if categorical_cols:
                    config['color'] = st.selectbox('Group by (Optional)', ['None'] + categorical_cols, key=f'color_{chart_name}')

            elif chart_name == 'Pie Chart':
                config['values'] = st.selectbox('Categories', categorical_cols, key=f'values_{chart_name}')
                config['max_categories'] = st.slider('Max categories to show', 5, 20, 10, key=f'max_{chart_name}')

            elif chart_name == 'Heatmap':
                if len(numeric_cols) >= 2:
                    selected_cols = st.multiselect('Select numeric columns', numeric_cols, default=numeric_cols[:5], key=f'cols_{chart_name}')
                    config['columns'] = selected_cols

            # Chart customization options
            st.markdown("### 🎨 Customization")
            config['title'] = st.text_input('Chart Title (Optional)', key=f'title_{chart_name}')
            config['height'] = st.slider('Chart Height', 300, 800, 500, key=f'height_{chart_name}')

            # Submit button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.form_submit_button("📊 Create Chart", type="primary"):
                    self.create_custom_visualization(chart_name, config)
            with col2:
                if st.form_submit_button("🔄 Reset"):
                    st.session_state['show_config'] = False
                    if 'selected_chart' in st.session_state:
                        del st.session_state['selected_chart']
                    st.rerun()
            with col3:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state['show_config'] = False
                    if 'selected_chart' in st.session_state:
                        del st.session_state['selected_chart']
                    st.rerun()

    def create_custom_visualization(self, chart_type: str, config: Dict[str, Any]):
        """Create a custom visualization based on user configuration"""
        if self.current_data is None:
            st.error("No data available for visualization")
            return

        try:
            # Initialize visualization agent
            viz_agent = VisualizationAgent()
            if self.coordinator:
                viz_agent.initialize_model(os.getenv("OPENAI_API_KEY"))

            # Clean config (remove None values)
            clean_config = {k: v for k, v in config.items() if v and v != 'None'}
            clean_config['chart_type'] = chart_type

            # Create the chart
            chart = viz_agent.create_chart_from_config(self.current_data, clean_config)

            if chart:
                st.header("📈 Your Custom Visualization")
                st.plotly_chart(chart, width='stretch')

                # Store in session state for persistence
                if 'custom_charts' not in st.session_state:
                    st.session_state.custom_charts = []
                st.session_state.custom_charts.append({
                    'chart': chart,
                    'type': chart_type,
                    'config': clean_config,
                    'timestamp': pd.Timestamp.now()
                })

                st.success(f"✅ {chart_type} created successfully!")

                # Reset form state
                st.session_state['show_config'] = False
                if 'selected_chart' in st.session_state:
                    del st.session_state['selected_chart']
            else:
                st.error("Failed to create visualization. Please try different settings.")

        except Exception as e:
            st.error(f"Error creating visualization: {str(e)}")

    def clear_results(self):
        """Clear analysis results"""
        st.session_state.last_result = None
        st.rerun()

    # Sandbox section removed - using agentic workflow only

    def run(self):
        """Main application runner"""
        self.render_header()

        # Initialize session state
        if 'data' not in st.session_state:
            st.session_state.data = None
        if 'last_result' not in st.session_state:
            st.session_state.last_result = None
        if 'custom_charts' not in st.session_state:
            st.session_state.custom_charts = []
        if 'show_config' not in st.session_state:
            st.session_state.show_config = False

        # Get current data from session state
        self.current_data = st.session_state.data

        # Render sidebar
        self.render_sidebar()

        # Main content
        if self.current_data is not None:
            self.render_data_preview()
            self.render_command_interface()

            # Display any stored results
            if st.session_state.last_result is not None:
                self.display_results(st.session_state.last_result)
            # Sandbox section removed - using agentic workflow only
        else:
            st.info("👆 Please upload a CSV file or load sample data from the sidebar to get started!")

        # Footer
        st.divider()
        st.markdown("Built with ❤️ using Streamlit, Plotly, and OpenAI")

# Run the app
if __name__ == "__main__":
    app = DataApp()
    app.run()
