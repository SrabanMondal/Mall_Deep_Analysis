import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from sklearn.metrics.pairwise import cosine_similarity
from itertools import chain, combinations

def build_market_basket_rules(items_df, min_support=0.001, min_lift=1.5):
    transactions = items_df['Items'].tolist()
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    transaction_df = pd.DataFrame(te_ary, columns=te.columns_)
    frequent_itemsets = apriori(transaction_df, min_support=min_support, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric='lift', min_threshold=min_lift)
    rules = rules.sort_values(by='confidence')
    
    mba_rules = {}
    for _, row in rules.iterrows():
        key = tuple(row['antecedents'])
        if key not in mba_rules:
            mba_rules[key] = []
        mba_rules[key].append((row['consequents'], row['confidence'], row['lift']))
    return mba_rules

def build_popular_catalogue(df):
    popular_catalogue = {}
    for sub_cat in df['Sub-Category'].value_counts().index:
        popular_catalogue[sub_cat] = df[df['Sub-Category'] == sub_cat].groupby('Product Name').size().nlargest(2).index.to_list()
    return popular_catalogue

def build_similarity_matrix(items_df, customer_col='Customer Name', items_col='Items'):
    cust_df = items_df.groupby(customer_col)[items_col].sum().reset_index()
    tras = cust_df['Items'].to_list()
    te = TransactionEncoder()
    te_ary = te.fit(tras).transform(tras)
    tedf = pd.DataFrame(te_ary, columns=te.columns_, index=cust_df['Customer Name'])
    similarity_matrix = cosine_similarity(tedf)
    similarity_df = pd.DataFrame(similarity_matrix, index=cust_df['Customer Name'], columns=cust_df['Customer Name'])
    return similarity_df, tedf

def recommend_cf(target_user, similarity_df, tedf, top_n=6):
    if target_user not in similarity_df.index:
        return {}
    similar_users = similarity_df[target_user].drop(target_user)
    recommendations = {}
    for similar_user in similar_users.index:
        similarity_score = similar_users.loc[similar_user]
        for item in tedf.columns:
            if not tedf.loc[target_user, item] and tedf.loc[similar_user, item]:
                recommendations[item] = recommendations.get(item, 0) + similarity_score
    sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    return {item[0]: float(item[1]) for item in sorted_recommendations[:top_n]}

def all_non_empty_subsets(s):
    return [tuple(subset) for subset in chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))]

def recommend(name, rules, cart=None, category=None, similarity_df=None, tedf=None, df=None):
    user_known = name in tedf.index
    popular_catalogue = build_popular_catalogue(df)
    if cart is None and category is None and user_known:
        recom = recommend_cf(name, similarity_df, tedf)
        return [item for sublist in [popular_catalogue.get(i[0], [i[0]]) for i in recom][:4] for item in sublist]

    if cart is None and category is not None and not user_known:
        return popular_catalogue.get(category, [])

    if cart is None and category is not None and user_known:
        recom = recommend_cf(name, similarity_df, tedf)
        filtered = [item for sublist in [popular_catalogue.get(i, []) for i in recom] for item in sublist][:4]
        extra = popular_catalogue.get(category, [])
        filtered.extend(extra)
        return filtered

    if cart is not None:
        if user_known:
            item_count = tedf.loc[name].sum()
            alpha = 0.7 if item_count > 5 else 0.3
        else:
            alpha = 0
        beta = 1 - alpha
        cart = set(cart)
        recommendations = {}
        mba={}
        cf_n={}
        for itemsets in all_non_empty_subsets(cart):
            for r, c, l in rules.get(itemsets, []):  
                filtered_r = set(r) - cart 
                for item in filtered_r:
                    mba[item] = mba.get(item, 0) + (c * l)
        if(name in tedf.index):
            cf = recommend_cf(name,similarity_df,tedf)
            cf_max = max(cf.values(),default=1)
            cf_n = {item[0]:item[1]/cf_max for item in cf.items()}
        mba_max = max(mba.values(),default=1)  
        mba_n = {item[0]:item[1]/mba_max for item in mba.items()}
        for item in set(cf_n.keys()).union(set(mba_n.keys())):
            recommendations[item] = alpha * cf_n.get(item, 0) + beta * mba_n.get(item, 0)
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        rec = [popular_catalogue.get(i[0], [i[0]]) for i in sorted_recommendations][:4]
        return [item for sublist in rec for item in sublist]

    # Default fallback
    return [item for sublist in list(popular_catalogue.values())[:4] for item in sublist[:1]]
