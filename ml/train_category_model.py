import os
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from preprocessing import build_preprocessing_pipeline

os.makedirs('artifacts', exist_ok=True)

df = pd.read_csv('../data/processed/transactions_clean.csv')

# merge rare categories
min_samples = 4
category_counts = df['category'].value_counts()
rare_categories = category_counts[category_counts < min_samples].index
df['category'] = df['category'].replace(rare_categories, 'Other')

X = df[['description', 'amount']]
y = df['category']

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

pipeline = Pipeline(steps=[
    ('preprocessor', build_preprocessing_pipeline()),
    ('classifier', LogisticRegression(max_iter=1000))
])

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
print(classification_report(y_test, y_pred))

joblib.dump(pipeline, 'artifacts/category_model.joblib')
