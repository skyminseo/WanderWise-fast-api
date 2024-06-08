from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta

router = APIRouter()

rf_model = joblib.load('rf_model.joblib')


class PredictionRequest(BaseModel):
    source_city: str
    destination_city: str
    departure_time: str
    arrival_time: str
    depart_date: str
    number_of_changes: int


def prepare_features(data):
    data['depart_date'] = pd.to_datetime(
        data['depart_date'], format='%d/%m/%Y')
    data['depart_day'] = data['depart_date'].dt.day
    data['depart_month'] = data['depart_date'].dt.month
    data['depart_year'] = data['depart_date'].dt.year
    data['depart_day_of_week'] = data['depart_date'].dt.dayofweek
    data = data.drop(columns=['depart_date'])
    data = pd.get_dummies(data, columns=[
                          'departure_time', 'arrival_time', 'source_city', 'destination_city'], drop_first=True)
    return data


@router.post("/predict")
async def predict(request: PredictionRequest):
    content = request.dict()

    predictions = []
    for i in range(300):  # Predict for the next 300 days
        depart_date = datetime.strptime(
            content['depart_date'], '%d/%m/%Y') + timedelta(days=i)
        data = {
            "source_city": content['source_city'],
            "destination_city": content['destination_city'],
            "departure_time": content['departure_time'],
            "arrival_time": content['arrival_time'],
            "depart_date": depart_date.strftime('%d/%m/%Y'),
            "number_of_changes": content['number_of_changes'],
            "days_left": (depart_date - datetime.now()).days
        }

        data_df = pd.DataFrame([data])
        data_prepared = prepare_features(data_df)
        model_features = rf_model.feature_names_in_
        for feature in model_features:
            if feature not in data_prepared.columns:
                data_prepared[feature] = 0
        data_prepared = data_prepared[model_features]
        prediction = rf_model.predict(data_prepared)[0]
        predictions.append({
            "date": depart_date.strftime('%Y-%m-%d'),
            "predicted_price": prediction
        })

    predicted_prices = [p['predicted_price'] for p in predictions]
    quantiles = np.percentile(predicted_prices, [25, 50, 75])

    for p in predictions:
        if p['predicted_price'] <= quantiles[0]:
            p['price_level'] = 'very low'
        elif p['predicted_price'] <= quantiles[1]:
            p['price_level'] = 'slightly low'
        elif p['predicted_price'] <= quantiles[2]:
            p['price_level'] = 'slightly high'
        else:
            p['price_level'] = 'very high'

    return predictions
