# create dataframe for north sea and baltic sea
import streamlit as st
import pandas as pd

# External script to create the offshore dataframe
@st.cache_data
def create_offshore_dataframe(predictions_df):
    offshore = {
        'region': ['north_sea', 'baltic_sea'],
        'solar_pv': [0, 0],
        'windpower': [6882, 1047],
        'solar_percentage': [0, 0],
        'wind_percentage': [0.099816, 0.015186],
    }
    
    # Create the initial offshore dataframe
    df_offshore = pd.DataFrame(offshore)

    # Reset the index and ensure date is a column
    predictions_df = predictions_df.reset_index()
    predictions_df['date'] = predictions_df['date'].dt.strftime('%d/%m/%y')

    # Initialize a list to hold offshore contributions for each date
    offshore_data = []

    # Iterate over each date in the predictions_df
    for _, row in predictions_df.iterrows():
        wind_prediction = row['windpower']
        solar_prediction = row['solar_pv']
        date = row['date']

        # Calculate offshore wind contributions for the current date
        df_offshore_copy = df_offshore.copy()
        df_offshore_copy['date'] = date
        df_offshore_copy['calculated_windpower'] = df_offshore_copy['wind_percentage'] * wind_prediction
        df_offshore_copy['calculated_solarpower'] = df_offshore_copy['solar_percentage'] * solar_prediction

        # Append the calculated contributions to the list
        offshore_data.append(df_offshore_copy)

    # Concatenate all the offshore contributions into a single DataFrame
    df_offshore_final = pd.concat(offshore_data, ignore_index=True)

    return df_offshore_final
