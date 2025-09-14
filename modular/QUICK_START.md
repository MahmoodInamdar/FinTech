# 🚀 Quick Start - Your Agentic Data App

## Ready to Go! ✅

Your `.env` file is set up with your OpenAI API key. Just run these commands:

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Start the App
```bash
python run.py
```

**That's it!** Your agentic workflow will automatically:
- 🔑 Load your API key from `.env`
- 🤖 Initialize all 4 AI agents
- 📊 Ready to process natural language commands

## Try These Commands:

**Data Exploration:**
- "Show top 5 products by sales"
- "Group revenue by region"
- "Show correlation between sales and units"

**Time Analysis:**
- "Show seasonality by region"
- "Analyze trends over time"

**Filtering:**
- "Filter by region North"
- "Show products with sales > 1000"

## How It Works:

1. **You speak naturally** → "show top products"
2. **MetaPrompt Agent** → Understands intent: "comparison"
3. **Data Agent** → Executes: `top_data(n=5)`
4. **Viz Agent** → Creates: Bar chart
5. **You get** → Table + Chart + Explanation

🎉 **Your sophisticated agentic system is ready to use!**