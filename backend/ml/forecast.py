import pandas as pd
from prophet import Prophet
def forecast_monthly_spending(monthly_data:dict,periods: int=6):
    df=pd.DataFrame(
        list(monthly_data.items()),
        columns=['ds','y']
    )

    df['ds']=pd.to_datetime(df['ds'])
    model=Prophet()
    model.fit(df)
    future=model.make_future_dataframe(periods=periods,freq='M')
    forecast=model.predict(future)

    forecast_df=forecast[['ds','yhat']].tail(periods)
    return dict(zip(forecast_df["ds"], forecast_df["yhat"].round(2)))
