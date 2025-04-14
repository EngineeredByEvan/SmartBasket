from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import tensorflow as tf
import joblib
import json
import os
import numpy as np

app = FastAPI()

# Load paths
MODEL_PATH = os.getenv("MODEL_PATH", "./models/current")
MODEL_FILE = os.path.join(MODEL_PATH, "grocery_predictor_model.keras")
ENCODER_FILE = os.path.join(MODEL_PATH, "mlb_encoder.pkl")
MAPPING_FILE = os.path.join(MODEL_PATH, "item_mapping.json")

# Load model and encoder
try:
    model = tf.keras.models.load_model(MODEL_FILE)
    mlb = joblib.load(ENCODER_FILE)
    with open(MAPPING_FILE, "r") as f:
        unique_items = json.load(f)
except Exception as e:
    print(f"Error loading model or encoder: {e}")
    model = None

# Request model
class Basket(BaseModel):
    items: List[str]

@app.post("/predict")
def predict(basket: Basket):
    if model is None:
        raise HTTPException(status_code=500, detail="Model or encoder not available")

    basket_items = basket.items

    try:
        encoded_input = mlb.transform([basket_items])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Encoding failed: {str(e)}")

    predictions = model.predict(encoded_input)[0]
    
    # Exclude already present items
    results = []
    for i, prob in enumerate(predictions):
        item = unique_items[i]
        if item not in basket_items:
            results.append({
                "item": item,
                "probability": float(prob)
            })

    sorted_results = sorted(results, key=lambda x: x["probability"], reverse=True)
    return {"predicted_items": sorted_results[:5]}  # Top 5 recommendations
