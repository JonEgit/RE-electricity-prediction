# Preprocess the forecasted weather data

import streamlit as st
import numpy as np
import pandas as pd
import joblib

@st.cache_data
def preprocess_weather_data(data):
    """Preprocesses the raw weather data by cleaning, transforming, and aggregating it.

    This function:
    - Drops unnecessary columns (`time`, `city`).
    - Converts `daylight_duration` and `sunshine_duration` from seconds to hours.
    - Calculates temperature differences between min and max temperature values.
    - Converts wind direction from degrees to radians and computes wind vector components.
    - Averages data by day and reconstructs wind speed and direction.
    - Removes redundant columns and reorders the final dataset.

    Args:
        data (pd.DataFrame): Raw weather data with various meteorological features.

    Returns:
        pd.DataFrame: Preprocessed and aggregated daily weather data with relevant features for the model.
    """
    # drop COLUMNS: time, city
    data = data.drop(['time', 'city'], axis=1)

    # Changing daylight_duration and sunshine_duration into hours instead of seconds
    data['daylight_duration'] = data['daylight_duration'] / 3600
    data['sunshine_duration'] = data['sunshine_duration'] / 3600

    # Add Temp diff column
    data['temp_diff_2m'] = data['temperature_2m_max'] - data['temperature_2m_min']
    data['apparent_temp_diff'] = data['apparent_temperature_max'] - data['apparent_temperature_min']

    # transform wind data
    # transform polar to radiant
    data['wind_direction_rad'] = np.deg2rad(data['wind_direction_10m_dominant'])
    # Calculate u and v components
    data['u'] = -data['wind_speed_10m_max'] * np.sin(data['wind_direction_rad'])
    data['v'] = -data['wind_speed_10m_max'] * np.cos(data['wind_direction_rad'])

    # Build averages for each column by day
    daily_averages = data.groupby('date').mean()
    # Convert the averaged u and v components back to wind speed and direction
    daily_averages['wind_speed_10m'] = np.sqrt(daily_averages['u']**2 + daily_averages['v']**2)
    daily_averages['wind_direction_10m'] = np.rad2deg(np.arctan2(-daily_averages['u'], -daily_averages['v']))

    # Normalize direction to be between 0 and 360 degrees
    # Use .loc to update values where wind direction is negative
    daily_averages.loc[daily_averages['wind_direction_10m'] < 0, 'wind_direction_10m'] += 360

    data = daily_averages.drop(['wind_speed_10m_max', 'wind_direction_10m_dominant', 'wind_direction_rad', 'u', 'v'], axis=1)

    # Reorder specific columns of a DataFrame
    col_order = ['temperature_2m_max', 'temperature_2m_min', 'temp_diff_2m',
                 'apparent_temperature_max', 'apparent_temperature_min', 'apparent_temp_diff', 
                 'daylight_duration', 'sunshine_duration', 'precipitation_sum', 
                 'precipitation_hours', 'snowfall_sum', 'shortwave_radiation_sum',
                 'wind_speed_10m', 'wind_direction_10m', 'wind_gusts_10m_max']

    data = data[col_order]  # Reorder columns

    return pd.DataFrame(data, columns=col_order, index=data.index)



@st.cache_data
def scaling(data):
    """Applies a pre-trained RobustScaler to normalize the weather data.

    Loads a RobustScaler model (`robust_scaler_multivariate.pkl`) and applies it to scale 
    the input data, ensuring consistency with previously trained models.

    Args:
        data (pd.DataFrame): The preprocessed weather data to be scaled.

    Returns:
        pd.DataFrame: Scaled weather data with the same column structure and index.
    """
    # Load the scaler used during training
    scaler = joblib.load('models/robust_scaler_multivariate.pkl')
    data_scaled = scaler.transform(data)
    col = data.columns 

    return pd.DataFrame(data_scaled, columns=col, index=data.index)