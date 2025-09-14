# 🤖 Agentic Workflow Analysis & Visualization

## 📊 **Workflow Architecture Overview**

```mermaid
graph TD
    A[User Input: "Show top 5 products by sales"] --> B[AgentCoordinator.process_command]

    B --> C[Step 1: MetaPromptAgent]
    C --> C1[analyze_context]
    C1 --> C2[classify_intent: 'top']
    C2 --> C3[extract_column_mentions: sales, products]
    C3 --> C4[create_contextual_prompt]

    C --> D[Step 2: DataAnalysisAgent]
    D --> D1[parse_command with context]
    D1 --> D2[execute_operation: top_data]
    D2 --> D3[Return filtered DataFrame]

    D --> E[Step 3: VisualizationAgent]
    E --> E1[Analyze data + user intent]
    E1 --> E2[Create appropriate charts]
    E2 --> E3[Return Plotly visualizations]

    E --> F[Step 4: Combine Results]
    F --> G[Return: {explanation, charts, data, operation}]
```

## 🧠 **How Meta Prompt Agent Works**

### **Core Intelligence Process:**

1. **Context Analysis** (`analyze_context()`)
   ```python
   # Analyzes DataFrame structure
   context = {
       'data_shape': df.shape,
       'columns': list(df.columns),
       'numeric_columns': ['sales', 'revenue', 'profit'],
       'categorical_columns': ['product', 'region'],
       'intent': 'comparison',  # Classified from user command
       'mentioned_columns': ['sales', 'products']
   }
   ```

2. **Intent Classification** (`classify_intent()`)
   ```python
   intent_patterns = {
       'visualization': ['show', 'plot', 'chart'],
       'comparison': ['top', 'bottom', 'best', 'worst'],
       'analysis': ['analyze', 'correlation', 'relationship'],
       'filtering': ['filter', 'where', 'select'],
       # ... more patterns
   }
   ```

3. **Dynamic Prompt Generation** (`create_contextual_prompt()`)
   ```python
   # Creates specialized prompts for each agent type
   prompt = f"""
   You are a data analysis expert.

   User Command: "{command}"
   Dataset Context:
   - Shape: {context['data_shape']}
   - Numeric columns: {context['numeric_columns']}
   - User intent: {context['intent']}
   - Mentioned columns: {context['mentioned_columns']}

   Determine the best operation: top_data with n=5, column=sales
   """
   ```

## 🔄 **Agent Workflow Execution**

### **Step-by-Step Process:**

**INPUT:** `"Show top 5 products by sales"`

**Step 1: MetaPromptAgent Analysis**
```json
{
  "context": {
    "intent": "comparison",
    "mentioned_columns": ["sales", "products"],
    "data_shape": [1000, 8],
    "numeric_columns": ["sales", "revenue", "units"]
  },
  "prompt": "Analyze this top N request with sales focus..."
}
```

**Step 2: DataAnalysisAgent Processing**
```python
# parse_command() output
operation = {
    "type": "top",
    "parameters": {
        "n": 5,
        "column": "sales",
        "criteria": "highest"
    }
}

# execute_operation() result
result = {
    "data": top_5_products_dataframe,
    "operation_details": "Top 5 records by sales"
}
```

**Step 3: VisualizationAgent Creation**
```python
# Receives data + context, creates appropriate chart
viz_result = {
    "charts": [plotly_bar_chart],
    "success": True,
    "explanation": "Created bar chart showing top 5 products"
}
```

**Final Output:**
```json
{
    "explanation": "I found the top 5 products by sales",
    "charts": [plotly_visualization],
    "data": filtered_dataframe,
    "operation": {"type": "top", "parameters": {...}},
    "viz_explanation": "Created bar chart visualization"
}
```

## 🎯 **Agent Specialization**

### **MetaPromptAgent: The Intelligence Layer**
- **Purpose**: Context understanding and prompt engineering
- **Key Methods**:
  - `analyze_context()`: Extracts DataFrame characteristics
  - `classify_intent()`: Determines user's analytical goal
  - `create_contextual_prompt()`: Generates specialized instructions
  - `generate_suggestions()`: Recommends relevant analyses

### **DataAnalysisAgent: The Processing Engine**
- **Purpose**: Execute data operations and transformations
- **Key Methods**:
  - `parse_command()`: NLP → structured operations
  - `execute_operation()`: Perform DataFrame manipulations
  - `parse_with_llm()`: Handle complex commands via LLM

### **VisualizationAgent: The Presentation Layer**
- **Purpose**: Create meaningful data visualizations
- **Receives**: Processed data + user intent
- **Outputs**: Plotly charts + explanations

### **CodeExecutionAgent: The Flexibility Layer**
- **Purpose**: Execute custom Python code safely
- **Features**: Sandboxed execution with security validation

## 🚀 **Why This is True Agentic Workflow**

### **1. Agent Autonomy**
- Each agent makes independent decisions within its domain
- MetaPrompt creates specialized instructions for other agents
- Data agent chooses appropriate operations based on analysis

### **2. Collaborative Intelligence**
- Agents share context and build upon each other's work
- MetaPrompt's analysis guides downstream agent behavior
- Results are combined into cohesive final output

### **3. Adaptive Behavior**
- System adapts to different data types and user intents
- Dynamic prompt generation based on actual data characteristics
- Fallback mechanisms when primary methods fail

### **4. Emergent Capabilities**
- Combined agent abilities exceed individual capabilities
- Complex queries broken down into specialized sub-tasks
- Context preservation across agent handoffs

## ⚠️ **Current Issues & Solutions**

### **Problem 1: LLM Integration Not Working**
**Root Cause:** OpenAI client calls may not be properly configured
**Solution:**
```python
# In base_agent.py - verify this pattern works:
response = self.client.chat.completions.create(
    model=self.model_name,
    messages=[{"role": "user", "content": prompt}],
    max_tokens=max_tokens
)
return response.choices[0].message.content
```

### **Problem 2: Agent Coordination Failures**
**Root Cause:** Error handling in coordinator may mask agent failures
**Solution:** Add detailed logging and agent status verification

### **Problem 3: Context Loss Between Agents**
**Current State:** ✅ Good - Context properly passed through coordinator
**Evidence:** `meta_result.get('context', {})` passed to data agent

## 🔧 **Recommended Improvements**

### **1. Enhanced Error Handling**
```python
# Add to coordinator.py
def validate_agent_responses(self):
    """Verify all agents are responding correctly"""
    for agent_name, agent in self.agents.items():
        try:
            test_response = agent.generate_response("test")
            if not test_response or "error" in test_response.lower():
                raise Exception(f"{agent_name} not responding properly")
        except Exception as e:
            return {"error": f"Agent {agent_name} failed: {e}"}
```

### **2. Visualization Enhancement**
```python
# Add workflow visualization to main.py
def show_workflow_diagram(self):
    """Display the agent workflow process"""
    st.markdown("""
    ### 🤖 How the AI Agents Work Together:
    1. **MetaPrompt Agent** analyzes your request
    2. **Data Agent** processes the data
    3. **Visualization Agent** creates charts
    4. **Coordinator** combines results
    """)
```

### **3. Agent Performance Monitoring**
```python
# Add to coordinator.py
def get_workflow_metrics(self):
    """Track agent performance and execution times"""
    return {
        "meta_prompt_time": self.meta_execution_time,
        "data_processing_time": self.data_execution_time,
        "visualization_time": self.viz_execution_time,
        "total_workflow_time": self.total_time
    }
```

## ✅ **Conclusion**

This codebase **DOES implement a true agentic workflow** with:

- **Specialized agents** with distinct capabilities
- **Intelligent coordination** through MetaPromptAgent
- **Context-aware processing** with dynamic prompt generation
- **Collaborative problem-solving** where agents build on each other's work

The MetaPromptAgent acts as the "intelligence layer" that understands user intent and data characteristics, then creates specialized prompts for other agents. This is sophisticated prompt engineering that enables emergent collaborative behavior.

**Next Steps:** Fix the OpenAI integration and add performance monitoring to get the full system working.