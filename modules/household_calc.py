## equal 2-person household electricity need

def household(predictions_df, date_choice):
    """Calculates the equivalent number of households which could be supplied by renewable electricity production on a given day.

    This function:
    - Converts predicted wind and solar electricity production from GWh to kWh.
    - Estimates the number of households that could be supplied with the produced electricity.
    - Returns the total number of households (in millions, rounded) for a specific date.

    Args:
        predictions_df (pd.DataFrame): DataFrame containing predicted wind and solar electricity production 
                                       with 'windpower' and 'solar_pv' columns.
        date_choice (str): Date in the format '%d/%m/%y' for which the household equivalent is calculated.

    Returns:
        int: Estimated number of households (in millions) supplied by renewable electricity on the selected day.
    """
    
    GW_TO_KW = 1_000_000  # Conversion factor from Gwh to kWh
    # kWh per day per 2-person-household in average (this is a rough approximation)
    AVERAGE_HOUSEHOLD_CONSUMPTION_PER_DAY = 3470 / 365

    df = predictions_df.copy()

    # Calculate total energy production in kWh
    df['windpower_kwh'] = predictions_df['windpower'] * GW_TO_KW
    df['solar_pv_kwh'] = predictions_df['solar_pv'] * GW_TO_KW
    df['total_energy_kwh'] = df['windpower_kwh'] + df['solar_pv_kwh']

    # Calculate equivalent number of households
    df['windpower_households'] = df['windpower_kwh'] / AVERAGE_HOUSEHOLD_CONSUMPTION_PER_DAY
    df['solar_pv_households'] = df['solar_pv_kwh'] / AVERAGE_HOUSEHOLD_CONSUMPTION_PER_DAY
    df['total_households'] = df['total_energy_kwh'] / AVERAGE_HOUSEHOLD_CONSUMPTION_PER_DAY
    df.index = df.index.strftime('%d/%m/%y')
    
    # Create a new DataFrame dropping the specified columns
    household = df.drop(columns=['windpower', 'solar_pv', 'windpower_kwh', 'solar_pv_kwh', 'total_energy_kwh'])

    total_households_latest = round(household.loc[date_choice, 'total_households'] / 1_000_000)

    # Displaying an icon and number of total households for the latest day
    # total_households_latest = round(household['total_households'].iloc[-1] / 1_000_000)  # Convert to millions and round

    return total_households_latest

# st.markdown("## Total Households Powered")
# st.markdown(f"<div style='border: 1px solid #ddd; padding: 20px; display: flex; align-items: center; justify-content: center;'>"
#             f"<img src='https://img.icons8.com/ios-filled/50/ffffff/home.png' style='margin-right: 10px;'/>"
#             f"<h2 style='margin: 0;'><b>~{total_households_latest}</b> Million two-person households</h2>"
#             f"</div>", unsafe_allow_html=True)

# # Adding an information box below
# st.info("This number represents the estimated equivalent number of 2-person households that could be powered by the total wind and solar energy produced on the selected day.")