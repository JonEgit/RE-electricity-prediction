## combine geodataframe with predictions and calculate partial contributin per federal state and per day

# load libraries
import pandas as pd


def geo_pred(gdf, predictions_df):
    """Calculates federal state contributions of wind and solar electricity based on predicted electricity production 
    and the nominal installed capacity of wind and pv power plants per federal state.

    This function:
    - Computes wind and solar electricity contributions per federal state for each day.
    - Uses percentage-based distribution per federal state (as of november 2024) from `gdf` to allocate predicted wind and solar electricity.
    - Transposes the data so that each row represents a day and each column represents a federal state.
    - Merges the computed contributions back into the input GeoDataFrame.

    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame containing regional boundaries and percentage-based 
            wind and solar electricity contributions.
        predictions_df (pd.DataFrame): DataFrame containing daily predicted wind and solar electricity production.

    Returns:
        gpd.GeoDataFrame: Updated GeoDataFrame with wind and solar contributions added for each day.
    """
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