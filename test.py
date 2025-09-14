import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import traceback
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
import google.generativeai as genai
from typing import TypedDict, List, Any

# Configure Gemini API (use Streamlit secrets or env for production)
GEMINI_API_KEY = "AIzaSyCZ3XGzKPYWP8cjWWwVv2AzmuE7a2Arw50"
genai.configure(api_key=GEMINI_API_KEY)

# Models: Two Gemini instances
meta_model = genai.GenerativeModel('gemini-1.5-pro')  # Use pro for more complexity handling
main_model = genai.GenerativeModel('gemini-1.5-pro')

# Enhanced LangGraph State
class AgentState(TypedDict):
    query: str
    data_schema: str
    df: pd.DataFrame
    system_prompt: str
    suggestions: List[str]
    explanation: str
    result_df: pd.DataFrame
    chart_fig: Any  # Plotly figure
    code: str
    history: List[dict]  # Query history: {'query': str, 'explanation': str}
    error: str

# Meta Prompter Agent: Enhanced with vagueness detection and better prompt generation
def meta_prompter_agent(state: AgentState):
    try:
        data_schema = (
            f"Columns: {state['df'].columns.tolist()}\n"
            f"Types: {state['df'].dtypes.to_dict()}\n"
            f"Sample rows: {state['df'].head(5).to_json(orient='records')}\n"
            f"Stats: {state['df'].describe().to_json()}"
        )
        state['data_schema'] = data_schema

        # Enhanced meta prompt for better context and vagueness handling
        meta_prompt = f"""
        You are an advanced meta prompter for a data analytics agent.
        User query: '{state['query']}'
        Data schema and stats: {data_schema}

        Tasks:
        1. Analyze if the query is vague or ambiguous. If yes, generate 2-3 alternative interpretations as a list.
           Examples of vagueness: unclear terms, multiple possible groupings, unspecified metrics.
        2. Generate a highly tailored system prompt for the main data analyst model.
           - Include detailed instructions on Pandas operations: filter (e.g., df.query), sort (sort_values), group (groupby), aggregate (agg), pivot (pivot_table).
           - Visualization: Generate Plotly code for interactive, colorful charts (use themes like 'plotly_dark', 'seaborn'; add hover_data, animations if suitable).
           - Handle refinements: Consider previous history if provided.
           - Make it capable of handling mid-sized data efficiently (avoid loops, use vectorized ops).
           - Add creativity: Suggest additional insights or related queries.
        3. If history exists, incorporate it for context-aware prompting.

        Output JSON: {{
            'suggestions': ['interp1', 'interp2', 'interp3'] or [],
            'system_prompt': 'full detailed prompt here'
        }}
        """
        if 'history' in state and state['history']:
            meta_prompt += f"\nPrevious query history: {json.dumps(state['history'][-3:])}"  # Last 3 for context

        response = meta_model.generate_content(meta_prompt)
        response_text = response.text.strip()
        # Strip Markdown fences
        if response_text.startswith('```json'):
            response_text = response_text[7:].strip()  # Remove '```json'
        if response_text.endswith('```'):
            response_text = response_text[:-3].strip()  # Remove trailing '```'
        try:
            output = json.loads(response_text)
        except json.JSONDecodeError as e:
            state['error'] = f"Failed to parse meta prompter response: {str(e)}. Raw response: {response_text}"
            return state
        state['suggestions'] = output.get('suggestions', [])
        state['system_prompt'] = output['system_prompt']
        state['error'] = ""
    except Exception as e:
        state['error'] = f"Meta prompter error: {str(e)}"
    return state

# Main Agent: Enhanced code generation with error checking and creativity
def main_agent(state: AgentState):
    if state['error']:
        return state
    try:
        # Full prompt with history for refinement
        full_prompt = f"""
        {state['system_prompt']}

        Current user query: {state['query']}
        Data schema: {state['data_schema']}
        If applicable, build on previous history: {json.dumps(state.get('history', [])[-2:])}

        Generate:
        1. Python code snippet:
           - Start with: import pandas as pd; import plotly.express as px;
           - Use 'df' as input DataFrame.
           - Compute 'result_df' with operations.
           - Create 'fig' as Plotly figure (interactive, colorful, e.g., px.line with template='ggplot2').
           - Handle errors gracefully in code.
           - Add creative elements: e.g., if seasonality, use trend lines.
        2. Human-readable explanation (short, with steps).
        3. Optional: Suggested follow-up queries (list of 2-3).

        Output JSON: {{
            'code': 'full code string',
            'explanation': 'text',
            'followups': ['query1', 'query2']
        }}
        """
        response = main_model.generate_content(full_prompt)
        response_text = response.text.strip()
        # Strip Markdown fences
        if response_text.startswith('```json'):
            response_text = response_text[7:].strip()
        if response_text.endswith('```'):
            response_text = response_text[:-3].strip()
        try:
            output = json.loads(response_text)
        except json.JSONDecodeError as e:
            state['error'] = f"Failed to parse main agent response: {str(e)}. Raw response: {response_text}"
            return state
        state['code'] = output['code']
        state['explanation'] = output['explanation']
        state['followups'] = output.get('followups', [])
    except Exception as e:
        state['error'] = f"Main agent error: {str(e)}"
    return state

# Executor Agent: Safe sandbox with AST parsing for security, full error handling
import ast
def executor_agent(state: AgentState):
    if state['error'] or not state['code']:
        return state
    code = state['code']
    # Basic AST check for safety: Disallow imports beyond allowed, no exec/eval
    tree = ast.parse(code)
    allowed_imports = {'pandas', 'plotly.express', 'numpy'}  # Add if needed
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            for alias in (node.names if isinstance(node, ast.Import) else [node]):
                module_name = alias.name if isinstance(alias, ast.alias) else alias
                if isinstance(module_name, str) and module_name not in allowed_imports:
                    state['error'] = f"Unsafe import: {module_name}"
                    return state
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {'exec', 'eval', 'os.system'}:
                state['error'] = f"Unsafe call: {node.func.id}"
                return state

    # Sandbox namespace
    local_namespace = {
        'pd': pd,
        'px': px,
        'np': pd.np,  # For numpy if needed
        'df': state['df'].copy(),  # Copy to avoid modifying original
    }
    try:
        exec(code, {'__builtins__': {}}, local_namespace)  # Restricted builtins
        state['result_df'] = local_namespace.get('result_df', state['df'])
        state['chart_fig'] = local_namespace.get('fig', None)
        # Append to history
        if 'history' not in state:
            state['history'] = []
        state['history'].append({'query': state['query'], 'explanation': state['explanation']})
    except Exception as e:
        state['error'] = f"Execution error: {traceback.format_exc()}"
        state['explanation'] += f"\nError details: {str(e)}"
    return state

# Build Enhanced LangGraph with conditional edges for suggestions
from langgraph.graph import START
workflow = StateGraph(AgentState)
workflow.add_node("meta_prompter", meta_prompter_agent)
workflow.add_node("main", main_agent)
workflow.add_node("executor", executor_agent)

workflow.add_edge(START, "meta_prompter")
workflow.add_edge("meta_prompter", "main")
workflow.add_edge("main", "executor")
workflow.add_edge("executor", END)

# Conditional for looping on suggestions (but since Streamlit is interactive, handle in UI)
app_graph = workflow.compile()

# Streamlit App: Enhanced UI with sidebar, history, etc.
st.set_page_config(page_title="Advanced Data Explorer", layout="wide")
st.title("Data Explorer with Natural Commands 🚀")

# Sidebar for configs
with st.sidebar:
    st.header("Settings")
    vis_theme = st.selectbox("Visualization Theme", ['plotly', 'plotly_dark', 'ggplot2', 'seaborn', 'simple_white'])
    max_rows = st.number_input("Max Rows for Preview", value=1000, min_value=100)
    if st.button("Reset Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]

# CSV Uploader and Persistence
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state['df'] = df
    st.session_state['original_df'] = df.copy()
else:
    if 'df' not in st.session_state:
        st.session_state['df'] = pd.DataFrame()

df = st.session_state['df']

if not df.empty:
    # Table Preview with pagination
    st.subheader("Data Preview")
    st.dataframe(df.head(max_rows), use_container_width=True)

    # Feature Selection Visualization: Enhanced with chart type choice
    st.subheader("Quick Feature Visualization")
    selected_cols = st.multiselect("Select columns", df.columns)
    chart_type = st.selectbox("Chart Type", ['scatter', 'line', 'bar', 'histogram', 'heatmap', 'box'])
    if selected_cols and len(selected_cols) >= 1:
        try:
            if chart_type == 'scatter' and len(selected_cols) >= 2:
                fig = px.scatter(df, x=selected_cols[0], y=selected_cols[1], color=selected_cols[2] if len(selected_cols)>2 else None, template=vis_theme)
            elif chart_type == 'line':
                fig = px.line(df, x=selected_cols[0], y=selected_cols[1:], template=vis_theme)
            elif chart_type == 'bar':
                fig = px.bar(df, x=selected_cols[0], y=selected_cols[1:], template=vis_theme)
            elif chart_type == 'histogram':
                fig = px.histogram(df, x=selected_cols[0], color=selected_cols[1] if len(selected_cols)>1 else None, template=vis_theme)
            elif chart_type == 'heatmap':
                corr = df[selected_cols].corr()
                fig = px.imshow(corr, text_auto=True, template=vis_theme)
            elif chart_type == 'box':
                fig = px.box(df, y=selected_cols, template=vis_theme)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Visualization error: {str(e)}")

    # NL Command Section
    st.subheader("Natural Language Query")
    query = st.text_area("Enter query (e.g., 'top 5 products by sales this quarter, pivot by region')")
    if st.button("Process Query") and query:
        initial_state = {
            "query": query,
            "df": df,
            "suggestions": [],
            "explanation": "",
            "result_df": df,
            "chart_fig": None,
            "history": st.session_state.get('history', []),
            "error": ""
        }
        final_state = app_graph.invoke(initial_state)

        # Handle Error
        if final_state['error']:
            st.error(final_state['error'])

        # Suggestions if vague
        if final_state['suggestions']:
            st.subheader("Clarify Your Query")
            selected_interp = st.radio("Select interpretation:", final_state['suggestions'])
            if st.button("Apply Selected Interpretation"):
                initial_state['query'] = selected_interp
                final_state = app_graph.invoke(initial_state)
                st.session_state['last_state'] = final_state  # For refinement

        # Display Results
        if not final_state['error']:
            # Chart
            if final_state['chart_fig']:
                st.subheader("Interactive Visualization 📊")
                st.plotly_chart(final_state['chart_fig'], use_container_width=True)

            # Explanation with emojis for engagement
            st.subheader("Operation Explanation ℹ️")
            st.markdown(final_state['explanation'])

            # Current View
            st.subheader("Result Data")
            st.dataframe(final_state['result_df'], use_container_width=True)

            # Export
            csv = final_state['result_df'].to_csv(index=False).encode('utf-8')
            st.download_button("Export Result as CSV", csv, "result.csv", "text/csv")

            # Follow-up Suggestions
            if 'followups' in final_state and final_state['followups']:
                st.subheader("Suggested Follow-ups 🔍")
                for followup in final_state['followups']:
                    if st.button(followup):
                        st.session_state['query'] = followup  # Set for next process

            # Update session
            st.session_state['df'] = final_state['result_df']  # Chain refinements
            st.session_state['history'] = final_state['history']

    # Query History
    if 'history' in st.session_state and st.session_state['history']:
        with st.expander("Query History"):
            for idx, hist in enumerate(st.session_state['history']):
                st.write(f"#{idx+1}: {hist['query']} - {hist['explanation'][:100]}...")

    # JSON Persistence
    col_save, col_load = st.columns(2)
    with col_save:
        if st.button("Save State to JSON"):
            state_dict = {
                "df": df.to_json(orient='split'),
                "history": st.session_state.get('history', [])
            }
            with open("data_state.json", "w") as f:
                json.dump(state_dict, f)
            st.success("State Saved!")
    with col_load:
        if os.path.exists("data_state.json") and st.button("Load State from JSON"):
            with open("data_state.json", "r") as f:
                state_dict = json.load(f)
            st.session_state['df'] = pd.read_json(state_dict["df"], orient='split')
            st.session_state['history'] = state_dict["history"]
            st.success("State Loaded!")

    # Reset to Original Data
    if st.button("Reset to Original Data"):
        if 'original_df' in st.session_state:
            st.session_state['df'] = st.session_state['original_df'].copy()
            st.session_state['history'] = []
            st.success("Reset complete!")

else:
    st.info("Please upload a CSV file to begin exploring your data.")