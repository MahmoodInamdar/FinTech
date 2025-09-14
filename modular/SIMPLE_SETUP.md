# 🚀 Simple Setup Guide

Your agentic workflow is already working! Just need 2 quick steps:

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Get OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Set environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## Step 3: Run the App
```bash
python run.py
```

## How It Works (Already Built!)

### Your Agents:
1. **MetaPromptAgent** - Understands what you want
2. **DataAnalysisAgent** - Does the data work
3. **VisualizationAgent** - Makes charts
4. **Coordinator** - Connects everything

### Example Flow:
```
You: "show top 5 products by sales"
├─ MetaPrompt: "Intent: comparison, Column: sales"
├─ DataAgent: "Operation: top_data(n=5, column=sales)"
├─ VizAgent: "Chart: bar chart of top products"
└─ Result: Table + Chart + "I found the top 5 products"
```

### What You Get:
- Natural language → Data operations ✅
- Smart suggestions based on your data ✅
- Clear explanations of what happened ✅
- Automatic visualizations ✅
- CSV export ✅

**That's it! Your agentic workflow is ready to go.**