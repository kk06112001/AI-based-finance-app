import pandas as pd
from prophet import Prophet
import joblib

df=pd.read_csv('../data/processed/transactions_clean.csv')

df=df[df['transaction_type']=='debit']

df['date']=pd.to_datetime(df['date'])
#monthly aggregate
monthly=(
    df.set_index('date').resample('M')['amount'].sum().reset_index()
)

monthly.columns=['ds','y']
model=Prophet()
model.fit(monthly)

joblib.dump(model,'artifacts/forecast_model.joblib')

print ("Forecast model trained and saved.")