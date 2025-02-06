## combine geodataframe with predictions and calculate partial contributin per federal state and per day

# load libraries
import pandas as pd


def geo_pred(gdf, predictions_df):

    # Create new DataFrames to store the contributions per day for each region for wind and solar
    wind_contributions = pd.DataFrame()
    solar_contributions = pd.DataFrame()

    # Calculate wind contributions for each region per day
    for day in range(len(predictions_df)):
        wind_contributions_for_day = gdf['wind_percentage'] * predictions_df.iloc[day]['windpower']
        wind_contributions[day] = wind_contributions_for_day

    # Calculate solar contributions for each region per day
    for day in range(len(predictions_df)):
        solar_contributions_for_day = gdf['solar_percentage'] * predictions_df.iloc[day]['solar_pv']
        solar_contributions[day] = solar_contributions_for_day

    # Transpose the contributions DataFrames so that each row represents a day and each column represents a region
    wind_contributions = wind_contributions.T
    wind_contributions.columns = gdf['GEN']
    wind_contributions.index = predictions_df.index.strftime('%d/%m/%y')#'%m-%d'

    solar_contributions = solar_contributions.T
    solar_contributions.columns = gdf['GEN']
    solar_contributions.index = predictions_df.index.strftime('%d/%m/%y')#'%m-%d'

    gdf_pred = gdf.copy()
    
    # Add wind and solar contributions for each day to the GeoDataFrame
    for day in predictions_df.index.strftime('%d/%m/%y'):#'%m-%d'
        gdf_pred[f'wind_contribution_{day}'] = wind_contributions.loc[day].values
        gdf_pred[f'solar_contribution_{day}'] = solar_contributions.loc[day].values

    return gdf_pred