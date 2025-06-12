import pandas as pd
import matplotlib.pyplot as plt
import os
dark_colors = [
    '#1f2f3f', '#2e3b4e', '#3c4a5d', '#4b596c', '#5a687b',
    '#6a798c', '#7b8c9f', '#8c9fb2', '#9eb2c5', '#b1c6d9'
]
def analyze_categories(df, output_dir = 'docs/visualizations'):
    summary = (
        df.groupby(['Category', 'Sub-Category'])
        .agg(Total_Sales=('Sales', 'sum'), Count=('Sales', 'count'))
        .reset_index()
    )
    category_totals = (
        df.groupby('Category')
        .agg(Total_Sales=('Sales', 'sum'), Count=('Sales', 'count'))
        .reset_index()
    )
    plt.figure(figsize=(6, 6))
    plt.pie(category_totals['Total_Sales'], labels=category_totals['Category'], autopct='%1.1f%%', startangle=140, colors=dark_colors[:len(category_totals)])
    plt.title('Total Sales by Category')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'sales_by_category.png'))
    plt.close()

    for category in summary['Category'].unique():
        sub_df = summary[summary['Category'] == category]
        plt.figure(figsize=(6, 6))
        plt.pie(sub_df['Total_Sales'], labels=sub_df['Sub-Category'], autopct='%1.1f%%', startangle=140, colors=dark_colors[:len(sub_df)])
        plt.title(f'Total Sales in {category}')
        plt.tight_layout()
        filename = f'sales_by_subcategory_in_{category.lower().replace(" ", "_")}.png'
        plt.savefig(os.path.join(output_dir, filename))
        plt.close()

    return summary, category_totals

def analyze_time_trends(daily_sales: pd.DataFrame, output_dir='docs/visualizations'):
    daily_sales['30_day_avg'] = daily_sales['sales'].rolling(window=30).mean()
    
    plt.figure(figsize=(12,6))
    daily_sales['sales'].plot(title='Daily Sales')
    plt.ylabel('Sales')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'daily_sales.png'))
    plt.close()
    
    plt.figure(figsize=(12,6))
    daily_sales['30_day_avg'].plot(title='30-Day Rolling Average of Sales', color='orange')
    plt.ylabel('Sales')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'rolling_avg_30_day.png'))
    plt.close()
    
    monthly_mean = daily_sales['sales'].resample('ME').sum()
    plt.figure(figsize=(12,6))
    monthly_mean.plot(title='Monthly Sales Total', color='purple')
    plt.ylabel('Sales')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'monthly_sales_every_year.png'))
    plt.close()
    
    daily_sales['month'] = daily_sales.index.month_name()
    monthly_avg = daily_sales.groupby('month')['sales'].mean()
    monthly_avg = monthly_avg.reindex([
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ])
    plt.figure(figsize=(12,6))
    monthly_avg.plot(kind='bar', color='purple', title='Average Monthly Sales Across Years')
    plt.ylabel('Average Sales')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir,'monthly_average.png'))
    plt.close()
    return monthly_avg

def plot_sales_by_region_segment(df, output_path='docs/visualizations/region_segment_sales.png'):
    sales_pivot = df.groupby(['Region', 'Segment'])['Sales'].sum().unstack()
    ax = sales_pivot.plot(kind='barh', figsize=(10, 6), colormap='Set2')
    plt.title('Sales by Region and Segment')
    plt.xlabel('Total Sales')
    plt.ylabel('Region')
    plt.legend(title='Segment')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return sales_pivot