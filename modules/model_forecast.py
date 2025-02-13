# Model and forecast loop
import streamlit as st
import joblib
# we need a model environemnt to use .predict(), could also be XGboost or RandomForest or others
from sklearn.multioutput import MultiOutputRegressor 

# Load the trained model
@st.cache_resource
def load_model():
    """Loads the pre-trained stacked multivariate machine learning model using joblib.

    Returns:
        object: The loaded machine learning model.
    """
    model = joblib.load('models/stacked_multivariate_model.pkl')
    return model

# create predictions and output
@st.cache_resource
def predict_energy_production(_model, weather_features, target_columns):
    """Predicts energy production based on weather features using the trained model.

    The function:
    - Uses a pre-trained model to predict electricity production by wind and pv in germany.
    - Ensures the prediction output matches the expected shape.
    - Raises an error if the output shape is incorrect.

    Args:
        _model (object): The trained machine learning model.
        weather_features (pd.DataFrame): Preprocessed and scaled weather data.
        target_columns (list): List of expected target variables (e.g., ['windpower', 'solar_pv']).

    Returns:
        np.ndarray: Predicted energy production values.

    Raises:
        ValueError: If the output shape does not match expectations.
    """
    predictions = _model.predict(weather_features)
    # Ensure predictions have the correct shape (days, number of energy sources)
    if len(predictions.shape) == 1:
        # If the model only produces one value per day, raise an error
        raise ValueError(f"Unexpected prediction shape: {predictions.shape}, expected multiple target outputs.")
    elif predictions.shape[1] != len(target_columns):
        raise ValueError(f"Unexpected prediction shape: {predictions.shape}, expected (_, {len(target_columns)})")
    return predictions