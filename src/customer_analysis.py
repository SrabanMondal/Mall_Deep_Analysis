import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def analyze_customer_pattern(df, output_path='docs/visualizations'):
    seg_dist = df['Customer Segment'].value_counts(normalize=True).sort_index() * 100
    plt.figure(figsize=(8, 5))
    sns.barplot(x=seg_dist.index, y=seg_dist.values, palette='Blues_d', hue=seg_dist.index, legend=False)
    plt.title("Customer Lifecycle Segment Distribution")
    plt.ylabel("Percentage of Customers (%)")
    plt.xlabel("Customer Segment")
    plt.xticks(rotation=15)
    plt.tight_layout()
    file_path = os.path.join(output_path, 'customer_segment_distribution.png')
    plt.savefig(file_path)
    plt.close()
    return seg_dist

    
def analyze_cohorts(cohort_counts, output_path='docs/visualizations/retention.png'):
    retention = cohort_counts.divide(cohort_counts[0], axis=0)
    plt.figure(figsize=(10, 6))
    sns.heatmap(retention, annot=True, fmt=".0%", cmap="YlGnBu")
    plt.title("Customer Retention by Cohort")
    plt.ylabel("Cohort Year (First Purchase)")
    plt.xlabel("Year Offset")
    plt.savefig(output_path)
    plt.close()
    return retention
