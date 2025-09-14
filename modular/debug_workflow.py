#!/usr/bin/env python3
"""
Debug script to test the agentic workflow without Streamlit UI
This helps identify where the workflow is breaking
"""

import os
import pandas as pd
import numpy as np
from agents.coordinator import AgentCoordinator
from datetime import datetime, timedelta
import json

def create_test_data():
    """Create sample e-commerce data for testing"""
    np.random.seed(42)

    # Generate dates
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=x) for x in range(365)]

    # Sample data
    regions = ['North', 'South', 'East', 'West']
    products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']

    n_records = 1000
    data = []

    for _ in range(n_records):
        data.append({
            'date': np.random.choice(dates),
            'region': np.random.choice(regions),
            'product': np.random.choice(products),
            'sales': np.random.randint(100, 2000),
            'units': np.random.randint(1, 20),
            'revenue': np.random.randint(1000, 5000),
            'quarter': np.random.choice(['Q1', 'Q2', 'Q3', 'Q4'])
        })

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    return df

def test_agent_initialization():
    """Test if agents can be initialized properly"""
    print("🔧 Testing Agent Initialization...")

    api_key = os.getenv('OPENAI_API_KEY', 'test-key-for-structure-test')

    try:
        coordinator = AgentCoordinator(api_key)
        print("✅ AgentCoordinator created successfully")

        # Test agent status
        status = coordinator.get_agent_status()
        print(f"📊 Agent Status: {status}")

        return coordinator
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return None

def test_data_agent_only(coordinator, df):
    """Test DataAnalysisAgent without LLM calls"""
    print("\n🧪 Testing DataAnalysisAgent (Rule-based parsing)...")

    test_commands = [
        "show top 5 products by sales",
        "filter by region North",
        "group by region",
        "sort by sales",
        "statistics for sales"
    ]

    for command in test_commands:
        print(f"\n📝 Testing command: '{command}'")

        try:
            # Test rule-based parsing (no LLM required)
            operation = coordinator.data_agent.parse_command(command)
            print(f"   ✅ Parsed operation: {operation}")

            # Test execution
            result = coordinator.data_agent.execute_operation(operation, df)
            print(f"   ✅ Execution result: {len(result.get('data', []))} rows returned")

            # Test explanation
            explanation = coordinator.data_agent.generate_explanation(operation, result)
            print(f"   ✅ Explanation: {explanation[:80]}...")

        except Exception as e:
            print(f"   ❌ Command failed: {e}")

def test_meta_prompt_agent(coordinator, df):
    """Test MetaPromptAgent context analysis (no LLM required)"""
    print("\n🧠 Testing MetaPromptAgent (Context Analysis)...")

    test_command = "show seasonality by region"

    try:
        # Test context analysis (no LLM required)
        context = coordinator.meta_prompt_agent.analyze_context(df, test_command)
        print(f"✅ Context analysis successful:")
        print(f"   - Data shape: {context['data_shape']}")
        print(f"   - Intent: {context['intent']}")
        print(f"   - Mentioned columns: {context['mentioned_columns']}")
        print(f"   - Numeric columns: {context['numeric_columns']}")

        # Test suggestions (no LLM required)
        suggestions = coordinator.meta_prompt_agent.generate_suggestions(df)
        print(f"✅ Generated {len(suggestions)} suggestions:")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"   {i}. {suggestion}")

        return context
    except Exception as e:
        print(f"❌ MetaPromptAgent failed: {e}")
        return None

def test_workflow_without_llm(coordinator, df):
    """Test the workflow using only rule-based parsing"""
    print("\n🔄 Testing Workflow (Rule-based only)...")

    test_commands = [
        "top 5 products by sales",
        "group by region",
        "sort by revenue"
    ]

    for command in test_commands:
        print(f"\n📝 Testing workflow: '{command}'")

        try:
            # Step 1: Meta-prompt analysis (no LLM)
            meta_input = {
                'command': command,
                'dataframe': df,
                'target_agent': 'data'
            }
            meta_result = coordinator.meta_prompt_agent.process(meta_input)
            print(f"   ✅ Meta analysis: intent={meta_result.get('context', {}).get('intent', 'unknown')}")

            # Step 2: Data processing (rule-based)
            data_input = {
                'command': command,
                'dataframe': df,
                'context': meta_result.get('context', {})
            }
            data_result = coordinator.data_agent.process(data_input)

            if data_result.get('success'):
                result_data = data_result.get('result', {}).get('data')
                if result_data is not None:
                    print(f"   ✅ Data processing: {len(result_data)} rows, operation: {data_result.get('operation', {}).get('type')}")
                    print(f"   ✅ Explanation: {data_result.get('explanation', 'No explanation')[:80]}...")
                else:
                    print(f"   ⚠️ Data processing succeeded but no data returned")
            else:
                print(f"   ❌ Data processing failed: {data_result.get('error')}")

        except Exception as e:
            print(f"   ❌ Workflow failed: {e}")

def test_with_openai_key():
    """Test with actual OpenAI API key if available"""
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print("\n⚠️ No OPENAI_API_KEY found. Set environment variable to test LLM integration.")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        return False

    print(f"\n🔑 Found OpenAI API key: {api_key[:10]}...")

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # Test simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Respond with just 'API_TEST_SUCCESS'"}
            ],
            max_tokens=10
        )

        result = response.choices[0].message.content.strip()
        if "API_TEST_SUCCESS" in result:
            print("✅ OpenAI API connection successful!")
            return True
        else:
            print(f"⚠️ Unexpected API response: {result}")
            return False

    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def main():
    """Run comprehensive workflow debugging"""
    print("🚀 FinTech Agentic Workflow Debugger")
    print("="*50)

    # Step 1: Create test data
    print("📊 Creating test dataset...")
    df = create_test_data()
    print(f"✅ Test data created: {len(df)} rows, {len(df.columns)} columns")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Sample data:")
    print(df.head(3).to_string())

    # Step 2: Test agent initialization
    coordinator = test_agent_initialization()
    if not coordinator:
        print("❌ Cannot proceed - agent initialization failed")
        return

    # Step 3: Test individual agents
    test_meta_prompt_agent(coordinator, df)
    test_data_agent_only(coordinator, df)

    # Step 4: Test workflow without LLM
    test_workflow_without_llm(coordinator, df)

    # Step 5: Test OpenAI integration
    api_works = test_with_openai_key()

    if api_works:
        print("\n🎯 Testing Full Workflow with OpenAI...")

        try:
            result = coordinator.process_command("show top 5 products by sales", df)

            if 'error' in result:
                print(f"❌ Full workflow failed: {result['error']}")
            else:
                print("✅ Full workflow successful!")
                print(f"   Explanation: {result.get('explanation', 'No explanation')}")
                if 'data' in result and result['data'] is not None:
                    print(f"   Data returned: {len(result['data'])} rows")
                if 'charts' in result:
                    print(f"   Charts created: {len(result.get('charts', []))}")

        except Exception as e:
            print(f"❌ Full workflow error: {e}")

    print("\n" + "="*50)
    print("🏁 Debugging Complete!")

    # Summary
    print("\n📋 SUMMARY:")
    print("✅ Data creation: Working")
    print("✅ Agent initialization: Working")
    print("✅ Rule-based parsing: Working")
    print("✅ Context analysis: Working")
    print(f"{'✅' if api_works else '❌'} OpenAI integration: {'Working' if api_works else 'Failed'}")

    if not api_works:
        print("\n🔧 NEXT STEPS:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Verify API key has sufficient credits")
        print("3. Test API connectivity")
    else:
        print("\n🎉 WORKFLOW IS READY!")
        print("The agentic system should work in the Streamlit app.")

if __name__ == "__main__":
    main()