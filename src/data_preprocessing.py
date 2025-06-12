import pandas as pd
from statsmodels.tsa.seasonal import STL
from datetime import timedelta, datetime
from .utils import encode_transactions

def load_data(file_path):
    """Load and preprocess the retail dataset."""
    df = pd.read_csv(file_path)
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%d/%m/%Y')
    df.set_index('Order Date', inplace=True)
    df.sort_index(inplace=True)
    return df

def sales_data(df):
    return pd.DataFrame({'sales':df.groupby(level=0)['Sales'].sum()})

def order_data(df):
    df['Order Year'] = df.index.to_period('Y')
    first_purchase = df.groupby('Customer ID')['Order Year'].min().reset_index()
    first_purchase.rename(columns={'Order Year':'First Purchase Year'}, inplace=True)
    df2 = df.reset_index().copy()
    df2 = df2.merge(first_purchase, on='Customer ID', how='left')
    df2.set_index(keys='Order Date',inplace=True)
    df['Order Month'] = df.index.to_period('M')
    last_purchase = df.groupby('Customer ID')['Order Month'].max().reset_index()
    last_purchase.rename(columns={'Order Month':'Last Purchase'}, inplace=True)
    df2.reset_index(inplace=True)
    df2 = df2.merge(last_purchase, on='Customer ID', how='left')
    df2.set_index(keys='Order Date',inplace=True)
    ref_date = pd.to_datetime('2019-1')
    df2['Time passed'] = (ref_date.year - df2['Last Purchase'].dt.year) * 12 + (ref_date.month - df2['Last Purchase'].dt.month)
    df2['No of purchases'] = df2.groupby('Customer ID')['Order ID'].transform('count')
    bins = [0, 3, 6, 12, df2['Time passed'].max()]
    labels = ['Active (0-3 months)', 'At Risk (3-6 months)', 'Churning (6-12 months)', 'Lost (>12 months)']
    df2['Customer Segment'] = pd.cut(df2['Time passed'], bins=bins, labels=labels)
    return df2

def cohort_data(df):
    df['Year Offset'] = df['Order Year'].dt.year - df['First Purchase Year'].dt.year
    df_cohorts = df[df['First Purchase Year'].notna()]
    cohort_counts = df_cohorts.groupby(['First Purchase Year', 'Year Offset'])['Customer ID'].nunique().unstack(fill_value=0)
    cohort_counts = cohort_counts.sort_index()
    return cohort_counts

def customer_data(df):
    df_customer = df.groupby('Customer ID')['Sub-Category'].agg(list).reset_index()
    df_customer=df_customer.set_index(keys='Customer ID')
    df_customer['No of Purchases']= df.groupby('Customer ID').size()
    df_customer = df_customer.merge(df[['Customer Name', 'Segment','Customer Segment','Time passed','First Purchase Year','Last Purchase']].drop_duplicates(), 
                                    on=df_customer.index, 
                                    how='left')
    df_customer=df_customer.rename(columns={'key_0':'Customer ID'})
    df_customer=df_customer.set_index(keys='Customer ID')
    return df_customer

def forecast_data(df):
    sales_df = df.groupby(level=0)['Sales'].sum().resample('ME').sum().reset_index()
    sales_df.set_index(keys='Order Date',inplace=True)
    stl = STL(sales_df)
    r = stl.fit()
    sales_df['Trend']=r.trend
    sales_df['Seasonal']=r.seasonal
    sales_df['Resid']=r.resid
    sales_df['Sales_S1'] = sales_df['Sales'].diff(12)
    train_df = sales_df[:datetime(2016,12,31)].copy()
    test_df = sales_df[datetime(2016,12,31)+timedelta(days=1):].copy()
    return train_df, test_df

def items_data(df):
    items_df=df.groupby([df.index,'Customer Name'])['Sub-Category'].agg(list).reset_index()
    items_df = items_df.rename(columns={'Sub-Category':'Items'})
    items_df['Count'] = items_df['Items'].apply(lambda x:len(x))
    return items_df
    