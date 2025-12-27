import re
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import joblib
def clean_text(text):
    text=text.lower()
    text=re.sub(r'[^a-z0-9\s]','',text)
    return text

def build_preprocessing_pipeline():
    text_features = 'description'
    numeric_features = ['amount']

    text_pipeline = Pipeline(steps=[
        ('tfidf', TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words='english'
        ))
    ])

    numeric_pipeline = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('text', text_pipeline, text_features),
            ('num', numeric_pipeline, numeric_features)
        ],
        remainder='drop'
    )

    return preprocessor