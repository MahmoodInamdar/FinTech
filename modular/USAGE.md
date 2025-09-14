# Usage Guide

## Quick Start

1. **Install and Run**
```bash
pip install -r requirements.txt
python run.py
```

2. **Configure API Key**
   - Enter your OpenAI API key in the sidebar
   - Or set the `OPENAI_API_KEY` environment variable

3. **Load Data**
   - Upload a CSV file using the file uploader
   - Or click "Load Sample Data" for demonstration

4. **Start Exploring**
   - Type natural language commands in the text area
   - Click "Analyze Data" to process your request
   - View interactive visualizations and results

## Natural Language Commands

### Data Exploration Commands

**Basic Statistics**
- "Show summary statistics"
- "Describe the dataset"
- "Find missing values"
- "Show data types and columns"

**Filtering and Selection**
- "Filter data where sales > 1000"
- "Show records for North region"
- "Find customers aged between 25 and 35"
- "Select data from last quarter"

**Aggregation and Grouping**
- "Group sales by region"
- "Sum revenue by product category"
- "Average age by department"
- "Count orders by month"

**Top/Bottom Analysis**
- "Top 10 customers by revenue"
- "Bottom 5 products by profit"
- "Highest performing employees"
- "Lowest scoring regions"

### Visualization Commands

**Trend Analysis**
- "Show sales trends over time"
- "Display monthly revenue chart"
- "Plot quarterly growth"
- "Revenue timeline by region"

**Distribution Analysis**
- "Show age distribution"
- "Histogram of salaries"
- "Price distribution by category"
- "Customer segment breakdown"

**Relationship Analysis**
- "Correlation between price and sales"
- "Scatter plot of age vs income"
- "Relationship between experience and salary"
- "Compare discount vs revenue"

**Comparative Analysis**
- "Compare sales across regions"
- "Revenue by product category"
- "Performance by department"
- "Channel comparison analysis"

### Advanced Analysis

**Seasonal Patterns**
- "Show seasonality in sales"
- "Quarterly performance analysis"
- "Monthly trends by category"
- "Seasonal customer behavior"

**Statistical Analysis**
- "Correlation matrix for numeric columns"
- "Statistical summary by group"
- "Outlier detection in sales"
- "Performance benchmarking"

## Features Guide

### 1. Multi-Agent System

The application uses four specialized agents:

- **Data Analysis Agent**: Processes data operations (filter, sort, group, aggregate)
- **Meta-Prompt Agent**: Creates contextual prompts for other agents
- **Visualization Agent**: Generates appropriate charts and visualizations
- **Code Execution Agent**: Executes Python code in a safe environment

### 2. Interactive Visualizations

**Chart Types Available:**
- Bar charts for categorical comparisons
- Line charts for trends over time
- Scatter plots for relationships
- Histograms for distributions
- Heatmaps for correlation matrices
- Box plots for distribution analysis
- Pie charts for proportions
- Treemaps for hierarchical data

**Interactive Features:**
- Hover for detailed information
- Zoom and pan capabilities
- Filter by clicking legend items
- Export charts as images

### 3. Data Operations

**Supported Operations:**
- Filtering with conditions
- Sorting by columns
- Grouping and aggregation
- Pivot table creation
- Statistical calculations
- Missing value analysis
- Data type conversions

### 4. Code Sandbox

**Write Custom Python Code:**
```python
# Example: Custom analysis
import plotly.express as px

# Your data is available as 'df'
fig = px.scatter(df, x='column1', y='column2', 
                 color='category', size='value')
fig.show()
```

**Security Features:**
- Sandboxed execution environment
- Limited library imports
- Input validation
- Safe operation patterns

### 5. Export and Sharing

- Download processed data as CSV
- Export visualizations as images
- Save analysis results
- Copy generated Python code

## Best Practices

### Command Writing Tips

1. **Be Specific**: "Show top 5 products by revenue this quarter" vs "show top products"
2. **Use Column Names**: Reference actual column names from your data
3. **Specify Criteria**: Include filtering conditions when needed
4. **Ask for Context**: Request explanations of results

### Data Upload Guidelines

1. **CSV Format**: Use standard CSV files with headers
2. **Clean Data**: Remove or handle missing values appropriately
3. **Reasonable Size**: Keep files under 100MB for best performance
4. **Proper Encoding**: Use UTF-8 encoding for special characters

### Performance Tips

1. **Sample Large Datasets**: Use representative samples for exploration
2. **Clear Commands**: Specific commands get better results
3. **Iterative Analysis**: Build complex analysis step by step
4. **Use Suggestions**: Try generated suggestions for ideas

## Troubleshooting

### Common Issues

**API Key Problems**
- Ensure your OpenAI API key is valid and active
- Check API quotas and limits
- Verify network connectivity

**Data Loading Issues**
- Check CSV format and encoding
- Ensure file size is reasonable
- Verify column headers are present

**Command Understanding**
- Try rephrasing commands
- Use more specific language
- Reference actual column names
- Check for typos

**Performance Issues**
- Reduce data size for testing
- Clear browser cache
- Restart the application
- Check system resources

### Error Messages

**"No dataframe provided"**
- Upload data first before running commands

**"Command parsing failed"**
- Rephrase your command more clearly
- Use simpler language

**"Execution timeout"**
- Reduce data size or simplify operation
- Break complex analysis into steps

## Advanced Usage

### Custom Code Examples

**Data Cleaning**
```python
# Remove outliers
Q1 = df['column'].quantile(0.25)
Q3 = df['column'].quantile(0.75)
IQR = Q3 - Q1
df_clean = df[~((df['column'] < (Q1 - 1.5 * IQR)) | 
                (df['column'] > (Q3 + 1.5 * IQR)))]
print(f"Removed {len(df) - len(df_clean)} outliers")
```

**Custom Visualization**
```python
# Create custom dashboard
from plotly.subplots import make_subplots

fig = make_subplots(rows=2, cols=2, 
                   subplot_titles=['Chart 1', 'Chart 2', 'Chart 3', 'Chart 4'])

# Add your custom charts
fig.add_trace(go.Bar(x=df['x'], y=df['y']), row=1, col=1)
fig.add_trace(go.Scatter(x=df['x'], y=df['z']), row=1, col=2)

fig.show()
```

**Statistical Analysis**
```python
# Advanced statistical testing
from scipy import stats

# Correlation analysis
correlation, p_value = stats.pearsonr(df['x'], df['y'])
print(f"Correlation: {correlation:.3f}, P-value: {p_value:.3f}")

# T-test comparison
group1 = df[df['category'] == 'A']['value']
group2 = df[df['category'] == 'B']['value']
t_stat, p_val = stats.ttest_ind(group1, group2)
print(f"T-test result: t={t_stat:.3f}, p={p_val:.3f}")
```

### Integration Examples

**API Integration**
```python
# Example: Fetch external data (if enabled)
import requests
import json

# Note: External requests may be restricted in sandbox
# This is for demonstration only
```

**Custom Functions**
```python
def custom_analysis(dataframe):
    """Custom analysis function"""
    results = {}

    # Your custom logic here
    results['summary'] = dataframe.describe()
    results['missing'] = dataframe.isnull().sum()

    return results

# Use your function
analysis_results = custom_analysis(df)
print(analysis_results)
```

## Support and Community

- **Documentation**: Check README.md for technical details
- **Issues**: Report bugs and feature requests on GitHub
- **Contributions**: Fork the repository and submit pull requests
- **Questions**: Use the discussion forums or community channels

Remember: The AI agents learn from context, so providing clear, specific commands with relevant details will give you better results!
