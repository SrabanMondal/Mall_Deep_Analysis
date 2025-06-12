import pandas as pd
from src.data_preprocessing import load_data, sales_data, order_data, items_data, forecast_data, customer_data, cohort_data
from src.sales_analysis import analyze_categories, analyze_time_trends, plot_sales_by_region_segment
from src.customer_analysis import analyze_customer_pattern, analyze_cohorts
from src.churn_analysis import plot_churn_rate_by_segment, plot_lost_customer_purchase_distribution, plot_churn_trend
from src.forecasting import run_sales_forecast_pipeline
from src.basket_analysis import plot_average_basket_with_time, plot_basket_distribution, basket_trend_analysis, plot_association_network
from src.recommendation import build_market_basket_rules, build_similarity_matrix, recommend
import matplotlib.pyplot as plt
plt.style.use('dark_background')
def main():
    # Load and preprocess data
    df = load_data('data/raw/train.csv')
    summary, category_totals = analyze_categories(df)
    
    #Sales Analysis
    print("Category Sales Analysis")
    print(category_totals)
    print('-'*50)
    print('Product Sales analysis')
    print(summary)
    print("""\nAnalysis : Here, we see, most sales are in office supplies, while technology sales are low but prices of products are high
in tech, copiers are most expensive and ofc underperforming, while in office supplies, most selling is paper and binders.
Highest revenue contribution is Technology, mostly from phones, and 2nd highest nis chairs from furniture""")
    print('-'*50)
    
    sales_df = sales_data(df)
    monthly_sales = analyze_time_trends(sales_df)
    print(monthly_sales)
    print('\nMonthly Sales analysis : march, september, novemember and december have sales peak')
    print('-'*50)
    region_segment_sales = plot_sales_by_region_segment(df)
    print("Region-Segment Sales:\n", region_segment_sales)
    print('\nAnalysis : Consumers in east and west are main revenue contributors')
    print('-'*50)
    
    #Customer Analysis
    order_df = order_data(df)
    seg_dist = analyze_customer_pattern(order_df)
    print(seg_dist)
    print('Analysis : 8%% of customers have been lost')
    print('-'*50)
    cohort_counts = cohort_data(order_df)
    retention = analyze_cohorts(cohort_counts)
    print("Retention - Customer Joined to Next Years")
    print(retention)
    print('-'*50)
    
    # Customer Churn Analysis
    
    churn_rate = plot_churn_rate_by_segment(order_df)
    print(churn_rate)
    print('Analysis : around 14%% from home office and 13%% from corporte are lost')
    print('-'*50)
    customer_df = customer_data(order_df)
    plot_lost_customer_purchase_distribution(customer_df)
    print('Analysis of churn customer purchase patterns : Lost customers mostly bought 5-10 purchases before churning')
    print('-'*50)
    plot_churn_trend(customer_df)
    print('Analysis of churn trend plot : Churned spiked up recently indicating many customers have not purchased for a long time again')
    print('-'*50)

    # Forecasting
    forecast_results = run_sales_forecast_pipeline(df, months_ahead=36)
    print(forecast_results.tail(12)[['Pred', 'MoM Growth %']])
    print('-'*50)
    # Basket Analysis
    items_df = items_data(df)
    print(items_df.head())
    plot_basket_distribution(items_df)
    plot_average_basket_with_time(items_df)
    print("""Analysis of basket plot : Average basket size has declined over time. Mostly small basket purchases are done now, while there are few large baskets we can promote sales by giving offers if you buy 4-5 items together to increase basket size
to increase large basket purchases, we can give special discounts to bulk buyers""")
    print('-'*50)
    print('Trending Basket Variations')
    frequent_items, rules = basket_trend_analysis(customer_df, items_df)
    print(rules.head())
    plot_association_network(rules)
    print('-'*50)
    
    # # Recommendation System
    rules = build_market_basket_rules(items_df)
    similarity_df, tedf = build_similarity_matrix(items_df)
    sample_user = df['Customer Name'].iloc[0]
    recommendations = recommend(name=sample_user, rules=rules, similarity_df=similarity_df, tedf=tedf, cart=None, category='Binders', df=df)
    print(f"Recommendations for {sample_user}:\n", recommendations)

if __name__ == "__main__":
    main()