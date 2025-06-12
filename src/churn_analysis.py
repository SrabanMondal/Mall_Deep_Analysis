import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_churn_rate_by_segment(df, output_path='docs/visualizations'):
    total_customers = df.groupby('Segment')['Customer ID'].nunique()
    lost_customers = df[df['Customer Segment'] == 'Lost (>12 months)'].groupby('Segment')['Customer ID'].nunique()
    churn_rate = (lost_customers / total_customers * 100).sort_index()
    plt.figure(figsize=(8, 5))
    sns.barplot(x=churn_rate.index, y=churn_rate.values, palette='Reds_d', hue=churn_rate.index, legend=False)
    plt.title("Churn Rate by Segment (Lost >12 Months)")
    plt.ylabel("Churn Rate (%)")
    plt.xlabel("Customer Segment")
    plt.ylim(0, churn_rate.max() * 1.2)
    plt.tight_layout()
    filename = os.path.join(output_path, 'churn_rate_by_segment.png')
    plt.savefig(filename)
    plt.close()
    return churn_rate


def plot_lost_customer_purchase_distribution(df, output_path='docs/visualizations'):
    lost_df = df[df['Customer Segment'] == 'Lost (>12 months)']
    plt.figure(figsize=(8, 5))
    sns.histplot(lost_df['No of Purchases'], bins=20, kde=True, color='red')
    plt.title("Distribution of Purchase Counts for Lost Customers")
    plt.xlabel("Number of Purchases (before churn)")
    plt.ylabel("Number of Customers")
    plt.tight_layout()

    plt.savefig(f"{output_path}/lost_customers_purchase_distribution.png")
    plt.close()
def plot_churn_trend(df, output_path='docs/visualizations'):
    churn_trend = df[df['Customer Segment']=='Lost (>12 months)'].groupby('Last Purchase').size()
    plt.figure(figsize=(8, 5))
    churn_trend.plot(title='Churned Customers Over Time')
    plt.title("Churn with time")
    plt.xlabel("Time")
    plt.ylabel("Number of Customers churned")
    plt.tight_layout()
    plt.savefig(f"{output_path}/churn_trend.png")
    plt.close()