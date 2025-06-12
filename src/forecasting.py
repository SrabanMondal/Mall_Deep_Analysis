from statsmodels.tsa.arima.model import ARIMA
from numpy.polynomial.polynomial import Polynomial
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from statsmodels.tsa.seasonal import STL
from sklearn.metrics import r2_score, mean_absolute_percentage_error, mean_squared_error
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def preprocess_sales_data(df):
    sales_df = df.groupby(level=0)['Sales'].sum().resample('ME').sum().reset_index()
    sales_df.set_index('Order Date', inplace=True)
    stl = STL(sales_df['Sales'])
    result = stl.fit()
    sales_df['Trend'] = result.trend
    sales_df['Seasonal'] = result.seasonal
    sales_df['Resid'] = result.resid
    sales_df['Sales_S1'] = sales_df['Sales'].diff(12)
    train_df = sales_df[:datetime(2016, 12, 31)].copy()
    test_df = sales_df[datetime(2017, 1, 1):].copy()
    return sales_df, train_df, test_df

def train_arima_trend_model(train_df, test_df, order=(4,0,4), trend_deg=2):
    arima_model = ARIMA(train_df['Resid'].dropna(), order=order, freq='ME').fit()
    pred_resid = arima_model.forecast(steps=len(test_df))
    test_df['Pred_res'] = pred_resid
    x = np.arange(len(train_df))
    poly_model = Polynomial.fit(x, train_df['Trend'], deg=trend_deg)
    pred_trend = poly_model(np.arange(len(train_df), len(train_df) + len(test_df)))
    test_df['pred_tr'] = pred_trend
    test_df['Pred'] = test_df['pred_tr'] + test_df['Seasonal'] + test_df['Pred_res']
    return test_df, arima_model, poly_model

def forecast_future(sales_df, train_df, arima_model, poly_model, months_ahead=36):
    pred_res = arima_model.forecast(steps=months_ahead)
    seasonal_pattern = sales_df['Seasonal'][-12:].values
    pred_seasonal = np.tile(seasonal_pattern, months_ahead // 12 + 1)[:months_ahead]
    pred_trend = poly_model(np.arange(len(train_df), len(train_df) + months_ahead))
    pred = pred_trend + pred_res + pred_seasonal
    future_dates = pd.date_range(start=train_df.index[-2] + timedelta(days=1), periods=months_ahead, freq='ME')
    future_df = pd.DataFrame({'Pred': pred}, index=future_dates)
    return future_df

def evaluate_forecast(test_df):
    true = test_df.dropna()['Sales']
    pred = test_df.dropna()['Pred']
    r2 = r2_score(true, pred)
    mape = mean_absolute_percentage_error(true, pred)
    rmse = np.sqrt(mean_squared_error(true, pred))
    print(f"R2 Score: {r2:.4f}")
    print(f"100 - MAPE: {100 - mape * 100:.2f}")
    print(f"RMSE: {rmse:.2f}")
    return r2, mape, rmse

def plot_forecast(df, columns=['Sales', 'Pred'], title='Sales Forecast', save_path='docs/visualizations/forecast.png'):
    df[columns].plot(figsize=(12,6))
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Sales")
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()
    
def run_sales_forecast_pipeline(df, months_ahead=36, plot_path='sales_forecast.png'):
    sales_df, train_df, test_df = preprocess_sales_data(df)
    test_df, arima_model, poly_model = train_arima_trend_model(train_df, test_df)
    evaluate_forecast(test_df)
    plot_forecast(test_df, title="Backtest Forecast vs Actual", save_path='docs/visualizations/'+plot_path)
    future_df = forecast_future(sales_df, train_df, arima_model, poly_model, months_ahead=months_ahead)
    combined_df = pd.concat([sales_df, future_df])
    plot_forecast(combined_df, title="Future Sales Forecast", save_path=f"docs/visualizations/future_{plot_path}")
    future_df['MoM Growth %'] = future_df['Pred'].pct_change() * 100
    return future_df
