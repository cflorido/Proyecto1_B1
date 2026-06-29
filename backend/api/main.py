from fastapi import FastAPI
from pydantic import BaseModel
from joblib import load, dump
import pandas as pd
from pathlib import Path
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from sklearn.model_selection import train_test_split
from typing import List

BASE_DIR = Path(__file__).resolve().parent
PIPELINE_PATH = BASE_DIR / "pipeline.joblib"
MODEL_PATH = BASE_DIR / "model.joblib"

pipeline = load(PIPELINE_PATH)


app = FastAPI()


class NewsItem(BaseModel):
    ID: str
    Titulo: str
    Descripcion: str
    Fecha: str



class RetrainData(BaseModel):
    ID: str
    Titulo: str
    Descripcion: str
    Fecha: str
    Label: int

@app.post("/predict/")
def predict(news: NewsItem):
    df = pd.DataFrame([news.dict()])
    prediction = pipeline.predict(df)[0]
    probabilidades = pipeline.predict_proba(df)[0]
    return {"prediction": int(prediction), "probabilidades": probabilidades.tolist()}

@app.post("/predictMany")
def predict(news_list: List[NewsItem]):
    df = pd.DataFrame([news.dict() for news in news_list])
    predictions = pipeline.predict(df)  
    probabilidades = pipeline.predict_proba(df)
    return {
        "predictions": predictions.tolist(),
        "probabilidades": [list(probs) for probs in probabilidades]
    }

@app.post("/retrain/")
def retrain(data: list[RetrainData]):
    global df_historical


    df_historical = pd.DataFrame([item.dict() for item in data])


    X = df_historical.drop(columns=["ID","Label"])
    y = df_historical["Label"]


    X_processed = pipeline[:-1].transform(X)


    X_train, X_val, y_train, y_val = train_test_split(X_processed, y, test_size=0.2, random_state=42)


    new_model = GradientBoostingClassifier(n_estimators=500, max_depth=5, criterion="friedman_mse")
    new_model.fit(X_train, y_train)


    y_train_pred = new_model.predict(X_train)
    train_f1 = f1_score(y_train, y_train_pred, average="weighted")
    train_recall = recall_score(y_train, y_train_pred, average="weighted")
    train_precision = precision_score(y_train, y_train_pred, average="weighted")
    train_accuracy = accuracy_score(y_train, y_train_pred)


    y_val_pred = new_model.predict(X_val)
    val_f1 = f1_score(y_val, y_val_pred, average="weighted")
    val_recall = recall_score(y_val, y_val_pred, average="weighted")
    val_precision = precision_score(y_val, y_val_pred, average="weighted")
    val_accuracy = accuracy_score(y_val, y_val_pred)


    pipeline.steps[-1] = ("classification", new_model)
    dump(pipeline, PIPELINE_PATH)
    dump(new_model, MODEL_PATH)
    return {
        "Training Metrics": {
            "F1": train_f1,
            "Recall": train_recall,
            "Precision": train_precision,
            "Accuracy": train_accuracy
        },
        "Validation Metrics": {
            "F1": val_f1,
            "Recall": val_recall,
            "Precision": val_precision,
            "Accuracy": val_accuracy
        }
    }