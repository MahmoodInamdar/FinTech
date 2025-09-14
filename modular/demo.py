#!/usr/bin/env python3
"""
Demo script to showcase Data Analytics AI capabilities
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def create_sample_datasets():
    """Create sample datasets for demonstration"""

    # E-commerce Sales Dataset
    np.random.seed(42)

    # Generate date range
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # Sample data parameters
    n_records = 2000
    products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones', 'Webcam', 'Tablet', 'Phone']
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East']
    categories = ['Electronics', 'Accessories', 'Computing', 'Mobile']
    channels = ['Online', 'Retail', 'Partner', 'Direct']

    # Generate sales data
    sales_data = []
    for _ in range(n_records):
        product = np.random.choice(products)
        region = np.random.choice(regions)
        category = np.random.choice(categories)
        channel = np.random.choice(channels)
        date = np.random.choice(dates)

        # Price based on product
        base_prices = {
            'Laptop': 800, 'Mouse': 25, 'Keyboard': 50, 'Monitor': 300,
            'Headphones': 80, 'Webcam': 60, 'Tablet': 400, 'Phone': 600
        }

        base_price = base_prices.get(product, 100)
        price = base_price * np.random.uniform(0.8, 1.3)

        # Quantity and calculations
        quantity = np.random.randint(1, 10)
        discount = np.random.uniform(0, 0.25) if np.random.random() < 0.3 else 0

        revenue = price * quantity * (1 - discount)
        cost = revenue * np.random.uniform(0.4, 0.7)
        profit = revenue - cost

        # Customer data
        customer_age = np.random.randint(18, 70)
        customer_segment = np.random.choice(['Premium', 'Standard', 'Budget'])

        sales_data.append({
            'Date': date,
            'Product': product,
            'Category': category,
            'Region': region,
            'Channel': channel,
            'Quantity': quantity,
            'Unit_Price': round(price, 2),
            'Discount': round(discount, 3),
            'Revenue': round(revenue, 2),
            'Cost': round(cost, 2),
            'Profit': round(profit, 2),
            'Customer_Age': customer_age,
            'Customer_Segment': customer_segment,
            'Month': date.strftime('%Y-%m'),
            'Quarter': f"Q{date.quarter}-{date.year}",
            'Season': get_season(date.month)
        })

    sales_df = pd.DataFrame(sales_data)

    # HR Analytics Dataset
    hr_data = []
    departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']
    positions = ['Junior', 'Senior', 'Lead', 'Manager', 'Director']
    locations = ['New York', 'San Francisco', 'London', 'Berlin', 'Tokyo', 'Remote']

    for _ in range(500):
        department = np.random.choice(departments)
        position = np.random.choice(positions)
        location = np.random.choice(locations)

        # Salary based on department and position
        base_salaries = {
            ('Engineering', 'Junior'): 75000, ('Engineering', 'Senior'): 110000,
            ('Sales', 'Junior'): 55000, ('Sales', 'Senior'): 85000,
            ('Marketing', 'Junior'): 50000, ('Marketing', 'Senior'): 80000,
            ('HR', 'Junior'): 45000, ('HR', 'Senior'): 70000,
            ('Finance', 'Junior'): 60000, ('Finance', 'Senior'): 90000,
            ('Operations', 'Junior'): 50000, ('Operations', 'Senior'): 75000
        }

        base_salary = base_salaries.get((department, position), 60000)
        salary = base_salary * np.random.uniform(0.9, 1.4)

        # Other attributes
        years_experience = np.random.randint(0, 15)
        satisfaction = np.random.uniform(1, 5)
        performance = np.random.uniform(1, 5)

        hr_data.append({
            'Employee_ID': f"EMP{1000 + len(hr_data)}",
            'Department': department,
            'Position': position,
            'Location': location,
            'Salary': round(salary, 0),
            'Years_Experience': years_experience,
            'Satisfaction_Score': round(satisfaction, 1),
            'Performance_Rating': round(performance, 1),
            'Age': np.random.randint(22, 65),
            'Gender': np.random.choice(['Male', 'Female', 'Other']),
            'Education': np.random.choice(['Bachelor', 'Master', 'PhD', 'High School']),
            'Remote_Work': np.random.choice([True, False]),
            'Bonus': round(salary * np.random.uniform(0, 0.2), 0)
        })

    hr_df = pd.DataFrame(hr_data)

    return sales_df, hr_df

def get_season(month):
    """Get season from month"""
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

def create_demo_commands():
    """Create demonstration commands for different scenarios"""

    sales_commands = [
        "Show revenue trends over time",
        "Top 5 products by profit margin", 
        "Compare sales performance across regions",
        "Analyze seasonal patterns in sales",
        "Show correlation between discount and revenue",
        "Group revenue by customer segment and channel",
        "Display monthly sales by product category",
        "Find the most profitable quarters",
        "Show distribution of customer ages",
        "Compare online vs retail channel performance"
    ]

    hr_commands = [
        "Show salary distribution by department",
        "Analyze employee satisfaction across locations", 
        "Compare performance ratings by position level",
        "Show correlation between experience and salary",
        "Group employees by education and department",
        "Display age distribution in the company",
        "Analyze remote work adoption by department",
        "Show top performers by department",
        "Compare bonuses across different roles",
        "Analyze gender distribution by department"
    ]

    return {
        'sales_dataset': sales_commands,
        'hr_dataset': hr_commands
    }

def save_demo_data():
    """Save demo datasets to CSV files"""
    import os

    # Create data directory
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)

    # Generate datasets
    sales_df, hr_df = create_sample_datasets()

    # Save datasets
    sales_df.to_csv(f"{data_dir}/sales_data_demo.csv", index=False)
    hr_df.to_csv(f"{data_dir}/hr_analytics_demo.csv", index=False)

    # Save demo commands
    commands = create_demo_commands()
    with open(f"{data_dir}/demo_commands.json", 'w') as f:
        json.dump(commands, f, indent=2)

    print("✅ Demo datasets created:")
    print(f"   📊 Sales Dataset: {len(sales_df)} records - {data_dir}/sales_data_demo.csv")
    print(f"   👥 HR Analytics: {len(hr_df)} records - {data_dir}/hr_analytics_demo.csv") 
    print(f"   💬 Demo Commands: {data_dir}/demo_commands.json")

    return sales_df, hr_df

def print_demo_info():
    """Print information about the demo"""
    print("🎯 Data Analytics AI - Demo Information")
    print("=" * 50)
    print()
    print("📊 SAMPLE DATASETS INCLUDED:")
    print("1. Sales Dataset (2000+ records)")
    print("   - E-commerce sales data across multiple regions")
    print("   - Includes products, revenue, profit, customer data")
    print("   - Time series data for trend analysis")
    print()
    print("2. HR Analytics Dataset (500+ records)")
    print("   - Employee information across departments")
    print("   - Salary, performance, satisfaction data")
    print("   - Location and demographic information")
    print()
    print("💬 EXAMPLE NATURAL LANGUAGE COMMANDS:")
    print()
    print("Sales Analysis:")
    print('   • "Show revenue trends over time"')
    print('   • "Top 5 products by profit margin"')
    print('   • "Compare sales across regions"')
    print('   • "Analyze seasonal patterns"')
    print()
    print("HR Analysis:")
    print('   • "Show salary distribution by department"')
    print('   • "Analyze employee satisfaction"')
    print('   • "Compare performance by position"')
    print('   • "Show correlation between experience and salary"')
    print()
    print("🚀 TO GET STARTED:")
    print("1. Run: python run.py")
    print("2. Enter your OpenAI API key in the sidebar")
    print("3. Load sample data or upload your own CSV")
    print("4. Try natural language commands!")
    print()

if __name__ == "__main__":
    print_demo_info()
    save_demo_data()
