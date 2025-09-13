"""
Data Analysis Prompt Generator

This module provides functionality to generate contextual prompts for data exploration
and analysis tasks using AI assistants.
"""

import pandas as pd
from typing import Optional


def generate_prompt(df: pd.DataFrame, user_query: str, sample_rows: int = 3) -> str:
    """
    Generate a structured prompt for data analysis tasks.
    
    Args:
        df (pd.DataFrame): The dataset to analyze
        user_query (str): The user's data exploration question
        sample_rows (int): Number of sample rows to include (default: 3)
    
    Returns:
        str: Formatted prompt string for AI assistant
    """
    num_rows = len(df)
    num_columns = len(df.columns)
    column_list = ", ".join(df.columns.tolist())
    sample_data = df.head(sample_rows).to_string(index=False)
    
    prompt = f"""You are a helpful AI assistant specialized in data exploration and analysis.

Dataset context:
- The dataset contains {num_rows} rows and {num_columns} columns.
- The columns are: {column_list}.
- Here are some example rows from the dataset:
{sample_data}

User query:
"{user_query}"

Instructions:
- Understand the user's query in the context of the dataset.
- Provide clear, concise answers to their data exploration request.
- Suggest data operations such as filtering, grouping, sorting, aggregations, or visualizations when appropriate.
- Explain your reasoning or steps in simple language.
- If the query is ambiguous, suggest possible clarifications or options.
- Use the vocabulary and phrasing natural to data analysis.
- Keep the response relevant and helpful.

Answer:"""
    return prompt


def generate_enhanced_prompt(df: pd.DataFrame, user_query: str, 
                           sample_rows: int = 3, include_dtypes: bool = True,
                           include_stats: bool = True) -> str:
    """
    Generate an enhanced prompt with additional dataset information.
    
    Args:
        df (pd.DataFrame): The dataset to analyze
        user_query (str): The user's data exploration question
        sample_rows (int): Number of sample rows to include (default: 3)
        include_dtypes (bool): Include column data types (default: True)
        include_stats (bool): Include basic statistics (default: True)
    
    Returns:
        str: Enhanced formatted prompt string for AI assistant
    """
    num_rows = len(df)
    num_columns = len(df.columns)
    column_list = ", ".join(df.columns.tolist())
    sample_data = df.head(sample_rows).to_string(index=False)
    
    # Additional context
    context_sections = []
    
    if include_dtypes:
        dtype_info = df.dtypes.to_dict()
        dtype_str = ", ".join([f"{col}: {dtype}" for col, dtype in dtype_info.items()])
        context_sections.append(f"- Column data types: {dtype_str}")
    
    if include_stats:
        # Basic statistics for numerical columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            stats_info = []
            for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
                stats_info.append(f"{col} (mean: {df[col].mean():.2f}, std: {df[col].std():.2f})")
            if stats_info:
                context_sections.append(f"- Numerical column statistics: {', '.join(stats_info)}")
    
    additional_context = "\n".join(context_sections)
    
    prompt = f"""You are a helpful AI assistant specialized in data exploration and analysis.

Dataset context:
- The dataset contains {num_rows} rows and {num_columns} columns.
- The columns are: {column_list}.
{additional_context}
- Here are some example rows from the dataset:
{sample_data}

User query:
"{user_query}"

Instructions:
- Understand the user's query in the context of the dataset.
- Provide clear, concise answers to their data exploration request.
- Suggest data operations such as filtering, grouping, sorting, aggregations, or visualizations when appropriate.
- Explain your reasoning or steps in simple language.
- If the query is ambiguous, suggest possible clarifications or options.
- Use the vocabulary and phrasing natural to data analysis.
- Keep the response relevant and helpful.
- Consider the data types and statistical properties when making recommendations.

Answer:"""
    return prompt


def analyze_dataset_structure(df: pd.DataFrame) -> dict:
    """
    Analyze the structure of a dataset for prompt generation.
    
    Args:
        df (pd.DataFrame): The dataset to analyze
    
    Returns:
        dict: Dictionary containing dataset structure information
    """
    analysis = {
        'num_rows': len(df),
        'num_columns': len(df.columns),
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist(),
        'datetime_columns': df.select_dtypes(include=['datetime']).columns.tolist()
    }
    
    # Add basic statistics for numeric columns
    if analysis['numeric_columns']:
        analysis['numeric_stats'] = df[analysis['numeric_columns']].describe().to_dict()
    
    return analysis


if __name__ == "__main__":
    # Example usage
    import numpy as np
    
    # Create sample dataset
    np.random.seed(42)
    sample_df = pd.DataFrame({
        'customer_id': range(1, 101),
        'age': np.random.randint(18, 80, 100),
        'income': np.random.normal(50000, 15000, 100),
        'transaction_amount': np.random.exponential(100, 100),
        'category': np.random.choice(['Food', 'Entertainment', 'Shopping', 'Travel'], 100),
        'date': pd.date_range('2023-01-01', periods=100, freq='D')
    })
    
    # Example query
    example_query = "What is the average transaction amount by category?"
    
    # Generate basic prompt
    basic_prompt = generate_prompt(sample_df, example_query)
    print("Basic Prompt:")
    print(basic_prompt)
    print("\n" + "="*80 + "\n")
    
    # Generate enhanced prompt
    enhanced_prompt = generate_enhanced_prompt(sample_df, example_query)
    print("Enhanced Prompt:")
    print(enhanced_prompt)
    print("\n" + "="*80 + "\n")
    
    # Analyze dataset structure
    structure = analyze_dataset_structure(sample_df)
    print("Dataset Structure Analysis:")
    for key, value in structure.items():
        print(f"{key}: {value}")