import networkx as nx
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import seaborn as sns
import matplotlib.pyplot as plt
import os

def basket_trend_analysis(customer_df, df, segment='Active (0-3 months)', min_support=0.002, min_confidence=0.6, output_path='data/processed'):
    os.makedirs(output_path, exist_ok=True)
    segment_ids = customer_df[customer_df['Customer Segment'] == segment]['Customer Name'].unique()
    segment_orders = df[df['Customer Name'].isin(segment_ids)].copy()
    transactions = segment_orders['Items'].dropna().tolist()
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    transaction_df = pd.DataFrame(te_ary, columns=te.columns_)
    frequent_itemsets = apriori(transaction_df, min_support=min_support, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    rules =  rules[(rules['confidence']>0.6)&(rules['lift']>2)].sort_values(by='support', ascending=False)
    frequent_itemsets.to_csv(f"{output_path}/frequent_itemsets_{segment}.csv", index=False)
    rules.to_csv(f"{output_path}/basket_rules_{segment}.csv", index=False)
    return frequent_itemsets, rules

def plot_association_network(rules, output_path='docs/visualizations', top_n=10):
    top_rules = rules.sort_values(by='confidence', ascending=False).head(top_n)
    G = nx.DiGraph()
    for _, row in top_rules.iterrows():
        for antecedent in row['antecedents']:
            for consequent in row['consequents']:
                G.add_edge(antecedent, consequent, weight=row['lift'])
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=1.2, seed=42)

    # Node and edge settings
    node_sizes = [3000 for _ in G.nodes()]  # Bigger node circles
    edge_weights = [G[u][v]['weight'] for u, v in G.edges()]

    nx.draw_networkx_edges(G, pos, edge_color=edge_weights, edge_cmap=plt.cm.Blues, width=2.5)
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='skyblue', alpha=0.9)

    # Draw node labels with better font and offset
    labels = {node: str(node) for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')

    plt.title("Top Association Rules Network (by Confidence)", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f"{output_path}/association_rules_network.png", dpi=300)
    plt.close()

def plot_basket_distribution(df, output_path='docs/visualizations/basket_distribution.png'):
    plt.figure(figsize=(8,6))
    sns.histplot(df['Count'], bins=20, kde=True,)
    plt.title("Basket Size Distribution", fontsize=16)
    plt.xlabel("Number of Items in Basket", fontsize=14)
    plt.ylabel("Frequency", fontsize=14)
    plt.savefig(output_path)
    plt.close()

def plot_average_basket_with_time(df, output_path='docs/visualizations/average_basket.png'):
    df['Month']=df['Order Date'].dt.to_period('M')
    monthly_basket_size = df.groupby(df['Month'])['Count'].mean().reset_index()
    monthly_basket_size['Month'] = monthly_basket_size['Month'].dt.to_timestamp()
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=monthly_basket_size, x='Month', y='Count', marker='o')
    plt.title("Average Basket Size Over Time", fontsize=16)
    plt.xlabel("Month", fontsize=14)
    plt.ylabel("Average Basket Size", fontsize=14)
    plt.xticks(rotation=45)
    plt.savefig(output_path)
    plt.close()