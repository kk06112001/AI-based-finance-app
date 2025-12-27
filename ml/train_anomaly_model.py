import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib   

df=pd.read_csv('../data/processed/transactions_clean.csv')

df=df[df['transaction_type']=='debit']
X=df[['amount']]

model=IsolationForest(
    n_estimators=200,
    contamination=0.02,
    random_state=42
)
model.fit(X)
df['anomaly']=model.predict(X)
df['anomaly']=df['anomaly'].map({1:0,-1:1})
print(df['anomaly'].value_counts())
joblib.dump(model,'artifacts/anomaly_model.joblib')

df.to_csv('../data/processed/personal_transactions_with_anomalies.csv',index=False)