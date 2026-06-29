from joblib import dump
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from preprocessing import dropna_and_combine_text, text_preprocessing_function, vectorization_function_transform
import joblib


model = joblib.load("model.joblib")


pipeline = Pipeline([
    ('dropna_and_combine', FunctionTransformer(dropna_and_combine_text)),
    ('text_preprocessing', FunctionTransformer(text_preprocessing_function)),
    ('vectorization', FunctionTransformer(vectorization_function_transform)), 
    ('classification', model)
])


dump(pipeline, 'pipeline.joblib')
