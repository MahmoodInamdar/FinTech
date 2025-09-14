# Visualization Agent
from .base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff

class VisualizationAgent(BaseAgent):
    """Agent responsible for creating data visualizations"""

    def __init__(self):
        super().__init__("VisualizationAgent", "gpt-3.5-turbo")
        self.chart_types = {
            'bar': self.create_bar_chart,
            'line': self.create_line_chart,
            'scatter': self.create_scatter_plot,
            'histogram': self.create_histogram,
            'box': self.create_box_plot,
            'heatmap': self.create_heatmap,
            'pie': self.create_pie_chart,
            'treemap': self.create_treemap,
            'correlation': self.create_correlation_matrix
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process visualization request with interactive options"""
        command = input_data.get('command', '')
        df = input_data.get('dataframe')
        analysis_result = input_data.get('analysis_result', {})
        interactive_mode = input_data.get('interactive_mode', True)

        if df is None:
            return {'error': 'No dataframe provided'}

        try:
            if interactive_mode:
                # Generate visualization options for user selection
                viz_options = self.generate_viz_options(command, df, analysis_result)
                return {
                    'success': True,
                    'interactive_options': viz_options,
                    'explanation': "I found several visualization options. Please select what you'd like to see."
                }
            else:
                # Original automatic visualization logic
                viz_plan = self.plan_visualizations(command, df, analysis_result)
                charts = []
                for plan in viz_plan:
                    chart = self.create_visualization(plan, df, analysis_result)
                    if chart:
                        charts.append(chart)

                return {
                    'success': True,
                    'charts': charts,
                    'viz_plan': viz_plan,
                    'explanation': self.generate_viz_explanation(viz_plan)
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': "Failed to create visualizations"
            }

    def plan_visualizations(self, command: str, df: pd.DataFrame, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan appropriate visualizations based on command and data"""
        command_lower = command.lower()
        plans = []

        # Get data characteristics
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

        # Determine visualization based on command keywords
        if any(word in command_lower for word in ['correlation', 'relationship']):
            if len(numeric_cols) >= 2:
                plans.append({
                    'type': 'correlation',
                    'data_source': 'original'
                })
                plans.append({
                    'type': 'scatter',
                    'x': numeric_cols[0],
                    'y': numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0],
                    'data_source': 'original'
                })

        elif any(word in command_lower for word in ['trend', 'over time', 'seasonality', 'seasonal']):
            if len(date_cols) >= 1 and len(numeric_cols) >= 1:
                plans.append({
                    'type': 'line',
                    'x': date_cols[0],
                    'y': numeric_cols[0],
                    'data_source': 'analysis' if 'data' in analysis_result else 'original'
                })

        elif any(word in command_lower for word in ['top', 'bottom', 'highest', 'lowest']):
            if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                plans.append({
                    'type': 'bar',
                    'x': categorical_cols[0],
                    'y': numeric_cols[0],
                    'data_source': 'analysis' if 'data' in analysis_result else 'original'
                })

        elif any(word in command_lower for word in ['distribution', 'histogram']):
            if len(numeric_cols) >= 1:
                plans.append({
                    'type': 'histogram',
                    'x': numeric_cols[0],
                    'data_source': 'original'
                })

        elif any(word in command_lower for word in ['group', 'by', 'breakdown']):
            if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                plans.append({
                    'type': 'bar',
                    'x': categorical_cols[0],
                    'y': numeric_cols[0],
                    'data_source': 'analysis' if 'data' in analysis_result else 'original'
                })

        elif any(word in command_lower for word in ['heatmap', 'heat map']):
            plans.append({
                'type': 'heatmap',
                'data_source': 'analysis' if 'data' in analysis_result else 'original'
            })

        # Default visualizations if no specific type detected
        if not plans:
            if len(numeric_cols) >= 2:
                # Scatter plot for numeric relationships
                plans.append({
                    'type': 'scatter',
                    'x': numeric_cols[0],
                    'y': numeric_cols[1],
                    'data_source': 'analysis' if 'data' in analysis_result else 'original'
                })

            if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                # Bar chart for categorical vs numeric
                plans.append({
                    'type': 'bar',
                    'x': categorical_cols[0],
                    'y': numeric_cols[0],
                    'data_source': 'analysis' if 'data' in analysis_result else 'original'
                })

        return plans[:3]  # Limit to 3 charts maximum

    def generate_viz_options(self, command: str, df: pd.DataFrame, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate interactive visualization options for user selection"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        all_cols = df.columns.tolist()

        # Generate smart recommendations based on command and data
        recommendations = self.get_smart_recommendations(command, numeric_cols, categorical_cols, date_cols)

        return {
            'available_charts': {
                'Bar Chart': {
                    'description': 'Compare categories or show rankings',
                    'best_for': 'Categorical vs Numeric data',
                    'requires': {'x': 'categorical or numeric', 'y': 'numeric'},
                    'suitable': len(categorical_cols) > 0 and len(numeric_cols) > 0
                },
                'Line Chart': {
                    'description': 'Show trends over time or sequences',
                    'best_for': 'Time series or sequential data',
                    'requires': {'x': 'date or numeric', 'y': 'numeric'},
                    'suitable': len(date_cols) > 0 or len(numeric_cols) >= 2
                },
                'Scatter Plot': {
                    'description': 'Explore relationships between two variables',
                    'best_for': 'Numeric correlations and patterns',
                    'requires': {'x': 'numeric', 'y': 'numeric'},
                    'suitable': len(numeric_cols) >= 2
                },
                'Histogram': {
                    'description': 'Show distribution of a single variable',
                    'best_for': 'Understanding data distributions',
                    'requires': {'x': 'numeric'},
                    'suitable': len(numeric_cols) > 0
                },
                'Box Plot': {
                    'description': 'Show statistical distribution by categories',
                    'best_for': 'Comparing distributions across groups',
                    'requires': {'x': 'categorical', 'y': 'numeric'},
                    'suitable': len(categorical_cols) > 0 and len(numeric_cols) > 0
                },
                'Heatmap': {
                    'description': 'Visualize correlations or patterns in data',
                    'best_for': 'Correlation analysis',
                    'requires': {'data': 'multiple numeric columns'},
                    'suitable': len(numeric_cols) >= 2
                },
                'Pie Chart': {
                    'description': 'Show proportions of a whole',
                    'best_for': 'Category distribution (≤10 categories)',
                    'requires': {'values': 'categorical'},
                    'suitable': len(categorical_cols) > 0
                }
            },
            'column_info': {
                'numeric_columns': numeric_cols,
                'categorical_columns': categorical_cols,
                'date_columns': date_cols,
                'all_columns': all_cols
            },
            'recommendations': recommendations,
            'data_summary': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'numeric_cols_count': len(numeric_cols),
                'categorical_cols_count': len(categorical_cols),
                'date_cols_count': len(date_cols)
            }
        }

    def get_smart_recommendations(self, command: str, numeric_cols: List[str], categorical_cols: List[str], date_cols: List[str]) -> List[Dict[str, Any]]:
        """Generate smart chart recommendations based on command and data structure"""
        command_lower = command.lower()
        recommendations = []

        # Command-based recommendations
        if any(word in command_lower for word in ['trend', 'over time', 'seasonal']):
            if date_cols and numeric_cols:
                recommendations.append({
                    'chart_type': 'Line Chart',
                    'reason': 'Perfect for showing trends over time',
                    'suggested_config': {
                        'x': date_cols[0],
                        'y': numeric_cols[0]
                    },
                    'priority': 'high'
                })

        if any(word in command_lower for word in ['compare', 'top', 'ranking', 'best']):
            if categorical_cols and numeric_cols:
                recommendations.append({
                    'chart_type': 'Bar Chart',
                    'reason': 'Great for comparing categories',
                    'suggested_config': {
                        'x': categorical_cols[0],
                        'y': numeric_cols[0]
                    },
                    'priority': 'high'
                })

        if any(word in command_lower for word in ['correlation', 'relationship']):
            if len(numeric_cols) >= 2:
                recommendations.append({
                    'chart_type': 'Scatter Plot',
                    'reason': 'Shows relationships between variables',
                    'suggested_config': {
                        'x': numeric_cols[0],
                        'y': numeric_cols[1]
                    },
                    'priority': 'high'
                })
                recommendations.append({
                    'chart_type': 'Heatmap',
                    'reason': 'Correlation matrix for all numeric variables',
                    'suggested_config': {},
                    'priority': 'medium'
                })

        if any(word in command_lower for word in ['distribution', 'spread', 'histogram']):
            if numeric_cols:
                recommendations.append({
                    'chart_type': 'Histogram',
                    'reason': 'Shows data distribution',
                    'suggested_config': {
                        'x': numeric_cols[0]
                    },
                    'priority': 'high'
                })

        # Data structure-based recommendations (fallback)
        if not recommendations:
            if len(numeric_cols) >= 2:
                recommendations.append({
                    'chart_type': 'Scatter Plot',
                    'reason': 'Explore relationships in your numeric data',
                    'suggested_config': {
                        'x': numeric_cols[0],
                        'y': numeric_cols[1]
                    },
                    'priority': 'medium'
                })

            if categorical_cols and numeric_cols:
                recommendations.append({
                    'chart_type': 'Bar Chart',
                    'reason': 'Compare your categories',
                    'suggested_config': {
                        'x': categorical_cols[0],
                        'y': numeric_cols[0]
                    },
                    'priority': 'medium'
                })

        return recommendations[:3]  # Top 3 recommendations

    def create_chart_from_config(self, df: pd.DataFrame, chart_config: Dict[str, Any]) -> Optional[go.Figure]:
        """Create chart from user-selected configuration"""
        chart_type = chart_config.get('chart_type', '').lower().replace(' ', '_')

        # Map display names to internal methods
        chart_mapping = {
            'bar_chart': 'bar',
            'line_chart': 'line',
            'scatter_plot': 'scatter',
            'histogram': 'histogram',
            'box_plot': 'box',
            'heatmap': 'heatmap',
            'pie_chart': 'pie'
        }

        chart_method = chart_mapping.get(chart_type, chart_type)

        if chart_method in self.chart_types:
            return self.chart_types[chart_method](df, chart_config)
        else:
            return self.create_default_chart(df, chart_config)

    def create_visualization(self, plan: Dict[str, Any], df: pd.DataFrame, analysis_result: Dict[str, Any]) -> Optional[go.Figure]:
        """Create visualization based on plan"""
        chart_type = plan.get('type')
        data_source = plan.get('data_source', 'original')

        # Select data source
        if data_source == 'analysis' and 'data' in analysis_result:
            data = analysis_result['data']
        else:
            data = df

        if data is None or data.empty:
            return None

        # Create chart based on type
        if chart_type in self.chart_types:
            return self.chart_types[chart_type](data, plan)
        else:
            return self.create_default_chart(data, plan)

    def create_bar_chart(self, df: pd.DataFrame, plan: Dict[str, Any]) -> go.Figure:
        """Create bar chart"""
        x_col = plan.get('x')
        y_col = plan.get('y')

        # Auto-select columns if not specified
        if not x_col:
            categorical_cols = df.select_dtypes(include=['object']).columns
            x_col = categorical_cols[0] if len(categorical_cols) > 0 else df.columns[0]

        if not y_col:
            numeric_cols = df.select_dtypes(include=['number']).columns
            y_col = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[1] if len(df.columns) > 1 else df.columns[0]

        # Aggregate data if needed
        if pd.api.types.is_numeric_dtype(df[y_col]):
            if df[x_col].duplicated().any():
                chart_data = df.groupby(x_col)[y_col].agg(['sum', 'count', 'mean']).reset_index()
                y_col = 'sum'  # Use sum by default
            else:
                chart_data = df
        else:
            chart_data = df[x_col].value_counts().reset_index()
            x_col = 'index'
            y_col = x_col.replace('index', 'count')

        fig = px.bar(
            chart_data,
            x=x_col,
            y=y_col,
            title=f"{y_col.title()} by {x_col.title()}",
            template="plotly_white"
        )

        fig.update_traces(
            hovertemplate=f"<b>{x_col}</b>: %{{x}}<br><b>{y_col}</b>: %{{y:,.0f}}<extra></extra>"
        )

        return fig

    def create_line_chart(self, df: pd.DataFrame, plan: Dict[str, Any]) -> go.Figure:
        """Create enhanced line chart with trend analysis"""
        x_col = plan.get('x')
        y_col = plan.get('y')

        # Auto-select columns with better logic
        if not x_col:
            date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

            # Try to detect date columns that aren't properly typed
            if not date_cols:
                for col in df.columns:
                    if any(keyword in col.lower() for keyword in ['date', 'time', 'year', 'month']):
                        try:
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                            if not df[col].isna().all():
                                date_cols.append(col)
                                break
                        except:
                            continue

            if date_cols:
                x_col = date_cols[0]
            else:
                numeric_cols = df.select_dtypes(include=['number']).columns
                x_col = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[0]

        if not y_col:
            # Prioritize sales/revenue columns
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            sales_cols = [col for col in numeric_cols if any(keyword in col.lower() for keyword in ['sales', 'revenue', 'amount', 'value', 'income', 'profit'])]

            if sales_cols:
                y_col = sales_cols[0]
            elif numeric_cols:
                y_col = numeric_cols[0]
            else:
                y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]

        # Prepare data for visualization
        if pd.api.types.is_datetime64_any_dtype(df[x_col]):
            df_sorted = df.sort_values(x_col)

            # Add time-based aggregation if too many data points
            if len(df_sorted) > 100:
                df_sorted = df_sorted.set_index(x_col).resample('M')[y_col].sum().reset_index()
        else:
            df_sorted = df.sort_values(x_col) if x_col in df.columns else df

        # Create the line chart
        fig = px.line(
            df_sorted,
            x=x_col,
            y=y_col,
            title=f"📈 {y_col.title()} Trends over {x_col.title()}",
            template="plotly_white",
            markers=True
        )

        # Enhanced styling
        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=6),
            hovertemplate=f"<b>{x_col}</b>: %{{x}}<br><b>{y_col}</b>: %{{y:,.0f}}<extra></extra>"
        )

        # Add trend line if it's a time series
        if pd.api.types.is_datetime64_any_dtype(df_sorted[x_col]) and len(df_sorted) > 5:
            # Add simple trend line
            from sklearn.linear_model import LinearRegression
            import numpy as np

            try:
                X = np.arange(len(df_sorted)).reshape(-1, 1)
                y = df_sorted[y_col].values
                lr = LinearRegression().fit(X, y)
                trend = lr.predict(X)

                fig.add_trace(go.Scatter(
                    x=df_sorted[x_col],
                    y=trend,
                    mode='lines',
                    name='Trend',
                    line=dict(dash='dash', color='red', width=2),
                    hovertemplate='<b>Trend</b>: %{y:,.0f}<extra></extra>'
                ))
            except:
                pass  # Skip trend line if error

        fig.update_layout(
            height=400,
            hovermode='x unified',
            showlegend=True if 'Trend' in [trace.name for trace in fig.data] else False
        )

        return fig

    def create_scatter_plot(self, df: pd.DataFrame, plan: Dict[str, Any]) -> go.Figure:
        """Create scatter plot"""
        x_col = plan.get('x')
        y_col = plan.get('y')

        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        if not x_col and len(numeric_cols) > 0:
            x_col = numeric_cols[0]
        if not y_col and len(numeric_cols) > 1:
            y_col = numeric_cols[1]
        elif not y_col:
            y_col = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[0]

        # Add color coding if categorical column exists
        color_col = None
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            color_col = categorical_cols[0]

        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=f"{y_col.title()} vs {x_col.title()}",
            template="plotly_white",
            opacity=0.7
        )

        # Add trendline if both columns are numeric
        if pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col]):
            fig.add_traces(
                px.scatter(df, x=x_col, y=y_col, trendline="ols", template="plotly_white").data[1:]
            )

        fig.update_traces(
            hovertemplate=f"<b>{x_col}</b>: %{{x}}<br><b>{y_col}</b>: %{{y}}<extra></extra>"
        )

        return fig

    def create_histogram(self, df: pd.DataFrame, plan: Dict[str, Any]) -> go.Figure:
        """Create histogram"""
        x_col = plan.get('x')

        if not x_col:
            numeric_cols = df.select_dtypes(include=['number']).columns
            x_col = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[0]

        fig = px.histogram(
            df,
            x=x_col,
            title=f"Distribution of {x_col.title()}",
            template="plotly_white",
            nbins=30
        )

        fig.update_traces(
            hovertemplate=f"<b>{x_col}</b>: %{{x}}<br><b>Count</b>: %{{y}}<extra></extra>"
        )

        return fig

    def create_box_plot(self, df: pd.DataFrame, plan: Dict[str, Any]) -> go.Figure:
        """Create box plot"""
        y_col = plan.get('y')
        x_col = plan.get('x')

        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns

        if not y_col and len(numeric_cols) > 0:
            y_col = numeric_cols[0]
        if not x_col and len(categorical_cols) > 0:
            x_col = categorical_cols[0]

        if x_col and x_col in df.columns:
            fig = px.box(
                df,
                x=x_col,
                y=y_col,
                title=f"Distribution of {y_col.title()} by {x_col.title()}",
                template="plotly_white"
            )
        else:
            fig = px.box(
                df,
                y=y_col,
                title=f"Distribution of {y_col.title()}",
                template="plotly_white"
            )

        return fig

    def create_heatmap(self, df: pd.DataFrame, plan: Dict[str, Any]) -> go.Figure:
        """Create heatmap"""
        numeric_df = df.select_dtypes(include=['number'])

        if len(numeric_df.columns) >= 2:
            # Correlation heatmap
            corr_matrix = numeric_df.corr()

            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                title="Correlation Heatmap",
                template="plotly_white",
                color_continuous_scale="RdBu_r"
            )
        else:
            # Pivot table heatmap if possible
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) >= 2 and len(numeric_df.columns) >= 1:
                pivot_table = df.pivot_table(
                    values=numeric_df.columns[0],
                    index=categorical_cols[0],
                    columns=categorical_cols[1] if len(categorical_cols) > 1 else categorical_cols[0],
                    aggfunc='mean',
                    fill_value=0
                )

                fig = px.imshow(
                    pivot_table,
                    text_auto=True,
                    aspect="auto",
                    title=f"Heatmap: {numeric_df.columns[0]} by {categorical_cols[0]} and {categorical_cols[1]}",
                    template="plotly_white"
                )
            else:
                return None

        return fig

    def create_pie_chart(self, df: pd.DataFrame, plan: Dict[str, Any]) -> go.Figure:
        """Create pie chart"""
        x_col = plan.get('x')

        if not x_col:
            categorical_cols = df.select_dtypes(include=['object']).columns
            x_col = categorical_cols[0] if len(categorical_cols) > 0 else df.columns[0]

        # Get value counts
        value_counts = df[x_col].value_counts().head(10)  # Top 10 categories

        fig = px.pie(
            values=value_counts.values,
            names=value_counts.index,
            title=f"Distribution of {x_col.title()}",
            template="plotly_white"
        )

        return fig

    def create_treemap(self, df: pd.DataFrame, plan: Dict[str, Any]) -> go.Figure:
        """Create treemap"""
        categorical_cols = df.select_dtypes(include=['object']).columns
        numeric_cols = df.select_dtypes(include=['number']).columns

        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            # Aggregate data
            treemap_data = df.groupby(categorical_cols[0])[numeric_cols[0]].sum().reset_index()

            fig = px.treemap(
                treemap_data,
                path=[categorical_cols[0]],
                values=numeric_cols[0],
                title=f"Treemap: {numeric_cols[0]} by {categorical_cols[0]}",
                template="plotly_white"
            )

            return fig

        return None

    def create_correlation_matrix(self, df: pd.DataFrame, plan: Dict[str, Any]) -> go.Figure:
        """Create correlation matrix visualization"""
        numeric_df = df.select_dtypes(include=['number'])

        if len(numeric_df.columns) >= 2:
            corr_matrix = numeric_df.corr()

            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu_r',
                zmid=0,
                text=corr_matrix.round(2).values,
                texttemplate="%{text}",
                textfont={"size": 10},
                hovertemplate="<b>%{x}</b><br><b>%{y}</b><br>Correlation: %{z:.3f}<extra></extra>"
            ))

            fig.update_layout(
                title="Correlation Matrix",
                template="plotly_white",
                width=600,
                height=500
            )

            return fig

        return None

    def create_default_chart(self, df: pd.DataFrame, plan: Dict[str, Any]) -> go.Figure:
        """Create default chart when type is not specified"""
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns

        # Choose appropriate default based on data types
        if len(numeric_cols) >= 2:
            return self.create_scatter_plot(df, {})
        elif len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            return self.create_bar_chart(df, {})
        elif len(numeric_cols) >= 1:
            return self.create_histogram(df, {})
        else:
            return None

    def generate_viz_explanation(self, viz_plan: List[Dict[str, Any]]) -> str:
        """Generate explanation of visualizations created"""
        if not viz_plan:
            return "No visualizations were created."

        explanations = []
        for plan in viz_plan:
            chart_type = plan.get('type', 'unknown')

            if chart_type == 'bar':
                explanations.append("I created a bar chart to show the relationship between categories and values.")
            elif chart_type == 'line':
                explanations.append("I created a line chart to show trends over time or sequential data.")
            elif chart_type == 'scatter':
                explanations.append("I created a scatter plot to explore the relationship between two numeric variables.")
            elif chart_type == 'histogram':
                explanations.append("I created a histogram to show the distribution of values.")
            elif chart_type == 'correlation':
                explanations.append("I created a correlation matrix to show relationships between all numeric variables.")
            elif chart_type == 'heatmap':
                explanations.append("I created a heatmap to visualize patterns in the data.")
            else:
                explanations.append(f"I created a {chart_type} chart to visualize your data.")

        return " ".join(explanations)
