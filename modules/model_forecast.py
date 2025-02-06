# Model and forecast loop
import streamlit as st
import joblib
# we need a model environemnt to use .predict(), could also be XGboost or RandomForest or others
from sklearn.multioutput import MultiOutputRegressor 

# Load the trained model
@st.cache_resource
def load_model():
    model = joblib.load('models/stacked_multivariate_model.pkl')
    return model

# create predictions and output
@st.cache_resource
def predict_energy_production(_model, weather_features, target_columns):
    predictions = _model.predict(weather_features)
    # Ensure predictions have the correct shape (days, number of energy sources)
    if len(predictions.shape) == 1:
        # If the model only produces one value per day, raise an error
        raise ValueError(f"Unexpected prediction shape: {predictions.shape}, expected multiple target outputs.")
    elif predictions.shape[1] != len(target_columns):
        raise ValueError(f"Unexpected prediction shape: {predictions.shape}, expected (_, {len(target_columns)})")
    return predictions