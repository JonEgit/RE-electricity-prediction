# Prediction of Electricity Production - Streamlit Dashboard

# load packages
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import geopandas as gpd

# functions
from modules.openMeteo_API import refresh_data_if_needed
from modules.preprocessing import preprocess_weather_data, scaling
from modules.model_forecast import load_model, predict_energy_production
from modules.geopredictions import geo_pred
from modules.offshore import create_offshore_dataframe
from modules.folium_map import create_map
from modules.fed_state_bokeh import create_fed_state_production_plot
from modules.bokeh_plot import generate_energy_forecast_plot
from modules.co2_visual import saved_emissions
from modules.household_calc import household

# Set page configuration
st.set_page_config(
        page_title="Project Overview", 
        layout="wide", 
        initial_sidebar_state="expanded"
) # collapsed

# # Serve static assets
# icon_path = os.path.join(os.getcwd(), 'assets', 'turbine.png')
# if not os.path.exists(icon_path):
#     st.error(f"Turbine icon not found at {icon_path}")

# Sidebar setup
st.sidebar.title("Navigation")
st.sidebar.markdown("Use the controls below to filter the data:")

# Main title
st.title("Renewable Electricity Outlook: Wind & Solar Forecast", anchor='left', help='Predictions for renewable electricity.')

# checks if the weather data is up to date or if needs to be reloaded because a date change
# it saves the output 'weather_data' of the openMeteo API as dataframe in streamlit session_state
# standard setting is to fetch 7 predicted and 3 past days of weather conditions   
# see openMeteo_API.py for more information
refresh_data_if_needed()

weather_data = st.session_state.weather_data

# check if preprocessed data 'prep' is already in session_state; if not, calculate and store it in session_state
# preprocess the weather data
# see preprocessing.py for more information
if 'prep' not in st.session_state:
    prep = preprocess_weather_data(weather_data)
    st.session_state.prep = prep

# use the pretrained scaler on the preprocessed weather data
# see preprocessing.py for more information
prep_data = scaling(st.session_state.prep)

# load trained model
# see model_forecast.py for more information
model = load_model()

# predict energy production
target_columns = ['windpower', 'solar_pv']

# check if predictions are in session_state; if not, calculate and store them
# check if prediction data 'predictions' is already in session_state; if not, calculate and store it in session_state
# see model_forecast.py for more information
if 'predictions' not in st.session_state:
    predictions = predict_energy_production(model, prep_data, target_columns)
    st.session_state.predictions = predictions

#Create a DataFrame for predicted energy production
predictions_df = pd.DataFrame(st.session_state.predictions, columns=target_columns, index=prep_data.index)

# check if consumption data 'consumption_df' is already in session_state; if not, load and store it in session_state
# only needed for a reference value presented in the dashboard, not for predictions 
# Load consumption data
if 'consumption_df' not in st.session_state:
    consumption_df = pd.read_csv('data/consumption.csv', sep=',')
    st.session_state.consumption_df = consumption_df

# Load GeoJSON file and the nominal installed capacity for federal states in germany (as of november 2024)
gdf = gpd.read_file('data/nominal_production_geo.geojson')
# calculates contributions of wind and pv electricity per federal state in germany based on nominal installed capacities 
# and the electricity predictions. This is an approximation to present the possibilities of the dashboard 
# if regional data would be accessible to train the model
# see geopredictions.py for more information
geo_df = geo_pred(gdf, predictions_df)

################ STREAMLIT APP #######################


# Sidebar for date and state selection
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
date_choice = st.sidebar.selectbox(label='Select a day', options=predictions_df.index.strftime('%d/%m/%y'))
st.sidebar.markdown("<p style='font-size: 12px; color: grey;'>Select a date to view the predicted electricity production and weather conditions for that day.</p>", unsafe_allow_html=True)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
state_choice = st.sidebar.selectbox(label='Select a state', options=geo_df['GEN'].tolist() + ['North Sea', 'Baltic Sea'])
st.sidebar.markdown("<p style='font-size: 12px; color: grey;'>Choose a federal state or offshore region to view the corresponding electricity production forecast.</p>", unsafe_allow_html=True)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)

# Download options for data in the sidebar
st.sidebar.markdown("### Download Data")
selected_download = st.sidebar.selectbox(label='Choose data to download', options=['Predictions Data', 'Geo Data'])

if selected_download == 'Predictions Data':
    st.sidebar.download_button(label='Download Predictions Data', data=predictions_df.to_csv(), file_name='predictions_data.csv', mime='text/csv')
elif selected_download == 'Geo Data':
    st.sidebar.download_button(label='Download Geo Data', data=geo_df.to_csv(), file_name='geo_data.csv', mime='text/csv')


# load offshore data and save in session_state
# this data was not considered in geo_df and needs to be added manually
# see offshore.py for more information
if 'df_offshore' not in st.session_state:
    df_offshore = create_offshore_dataframe(predictions_df)
    st.session_state.df_offshore = df_offshore


######## Weather ICONS ########
# create weather icons from the loaded open meteo weather data
# this is only for dashboard design and completeness but not needed for the model predictions
weather = st.session_state.prep.reset_index()
df = pd.DataFrame(weather)
df['date'] = pd.to_datetime(df['date'])

######## Icons Version 1: Bigger weather icons within a slider window ########
st.markdown("")

st.markdown("""
### Information:

The weather information boxes present historic weather data (grey boxes) as well as the recent weatherforcast. The data is accessed via an automated API to openMeteo 
and is an excerpt of the input data which is used for the renewable electricity predictions. Its request changes in dependency of the date. 
Predicted electricity production for wind and solar are shown in the graphs below and used for further calculations to present infomation about geograhical distribution as well as on saved emissions.   
""")
st.markdown("")

# Define sliding window size
WINDOW_SIZE = 5

# Initialize or retrieve the current index for the weather columns window
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

# Calculate the number of rows and set up the navigation controls
num_days = len(df)
start_index = st.session_state.current_index
end_index = start_index + WINDOW_SIZE

# Create navigation buttons
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    if st.button('Previous'):
        if start_index - WINDOW_SIZE >= 0:
            st.session_state.current_index -= WINDOW_SIZE

with col3:
    if st.button('Next'):
        if end_index < num_days:
            st.session_state.current_index += WINDOW_SIZE

# Ensure that the window indices are within bounds
start_index = max(0, st.session_state.current_index)
end_index = min(num_days, start_index + WINDOW_SIZE)

# Display the data for the current window
columns = st.columns(end_index - start_index)
for i, row in df.iloc[start_index:end_index].iterrows():
    with columns[i - start_index]:
        date = row['date'].strftime('%a, %d %b')  # Abbreviate the weekday and delete the year
        sunshine = row.get('sunshine_duration', 0)  # Get sunshine if it exists, otherwise default to 0
        wind_speed_max = row['wind_speed_10m']
        precipitation_sum = row['precipitation_sum']

        # Set a grey transparent background for the first three boxes and more transparent text for the first three boxes
        background_style = "background-color: rgba(128, 128, 128, 0.3);" if i < 3 else ""
        text_style = "color: rgba(255, 255, 255, 0.7);" if i < 3 else "color: white;"

        # Create a box around each day's weather data
        st.markdown(f"""
            <div style="border: 1px solid #ccc; padding: 10px; border-radius: 5px; text-align: left; height: 220px; display: flex; flex-direction: column; justify-content: space-evenly; align-items: left; {background_style}">
                <h6 style='margin: 2px 0; font-size: 14px; {text_style}'>{date}</h6>
                <div style='margin: 2px 0;'>
                    <p style='font-size: 12px; margin: 2px 0; font-weight: bold; {text_style}'>☀️ Sunshine</p>
                    <p style='font-size: 12px; margin: 2px 0; {text_style}'>{sunshine:.1f} hours</p>
                </div>
                <div style='margin: 2px 0;'>
                    <p style='font-size: 12px; margin: 2px 0; font-weight: bold; {text_style}'>💨 Wind:</p>
                    <p style='font-size: 12px; margin: 2px 0; {text_style}'>{wind_speed_max:.1f} m/s</p>
                </div>
                <div style='margin: 2px 0;'>
                    <p style='font-size: 12px; margin: 2px 0; font-weight: bold; {text_style}'>☔️ Precip:</p>
                    <p style='font-size: 12px; margin: 2px 0; {text_style}'>{precipitation_sum:.1f} mm</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Add some vertical space after the columns of daily data
st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

######## Icons Version 2: Smaller weather icons design and all side by side (for bigger screens) ########
## -> Activate Version 2 by toggling between block commants of Version 1 and 2

# st.markdown("")

# st.markdown("""
# ### Information:

# The weather information boxes present historic weather data (grey boxes) as well as the recent weatherforcast. The data is accessed via an automated API to openMeteo 
# and is an excerpt of the input data which is used for the renewable electricity predictions. Its request changes in dependency of the date. 
# Predicted electricity production for wind and solar are shown in the graphs below and used for further calculations to present infomation about geograhical distribution as well as on saved emissions.   
# """)
# st.markdown("")

# ### weather icons all on the page
# # Display the data for each day horizontally
# columns = st.columns(len(df))
# for i, row in df.iterrows():
#     with columns[i]:
#         date = row['date'].strftime('%a, %d %b')  # Abbreviate the weekday and delete the year
#         sunshine = row.get('sunshine_duration', 0)  # Get sunshine if it exists, otherwise default to 0
#         wind_speed_max = row['wind_speed_10m']
#         precipitation_sum = row['precipitation_sum']

#         # Set a grey transparent background for the first three boxes and more transparent text for the first three boxes
#         background_style = "background-color: rgba(128, 128, 128, 0.3);" if i < 3 else ""
#         text_style = "color: rgba(255, 255, 255, 0.7);" if i < 3 else "color: white;"

#         # Create a box around each day's weather data
#         st.markdown(f"""
#             <div style="border: 1px solid #ccc; padding: 10px; border-radius: 5px; text-align: left; height: 220px; display: flex; flex-direction: column; justify-content: space-evenly; align-items: left; {background_style}">
#                 <h6 style='margin: 2px 0; font-size: 14px; {text_style}'>{date}</h6>
#                 <div style='margin: 2px 0;'>
#                     <p style='font-size: 12px; margin: 2px 0; font-weight: bold; {text_style}'>☀️ Sunshine</p>
#                     <p style='font-size: 12px; margin: 2px 0; {text_style}'>{sunshine:.1f} hours</p>
#                 </div>
#                 <div style='margin: 2px 0;'>
#                     <p style='font-size: 12px; margin: 2px 0; font-weight: bold; {text_style}'>💨 Wind:</p>
#                     <p style='font-size: 12px; margin: 2px 0; {text_style}'>{wind_speed_max:.1f} m/s</p>
#                 </div>
#                 <div style='margin: 2px 0;'>
#                     <p style='font-size: 12px; margin: 2px 0; font-weight: bold; {text_style}'>🌧️ Precip:</p>
#                     <p style='font-size: 12px; margin: 2px 0; {text_style}'>{precipitation_sum:.1f} mm</p>
#                 </div>
#             </div>
#         """, unsafe_allow_html=True)

# # Add some vertical space after the columns of daily data
# st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)

######## End Weather ICONS ########

# print selected date and state
st.markdown(f"**Currently Selected Date:** {date_choice}")
st.markdown(f"**Currently Selected State/Region:** {state_choice}")
st.markdown("<hr>", unsafe_allow_html=True)

# Creating the columns layout for the UI with adjusted ratios for responsiveness
# text input first level
col1, col2 = st.columns([1.8, 1], vertical_alignment="top")

with col1:
    # Add a description for the bokeh electricity forecast plot
    st.markdown("### Daily Electricity Production Forecast")
    st.markdown("Predicted daily production vs. average daily consumption of renewable electricity (wind and solar) based on current weather forecast and model predictions.")
    st.markdown("**Daily Values for:** Germany")
with col2:
    # Add a description for the approximation of electricity production comparison with households
    st.markdown("### Total Households Powered")
    st.markdown("Estimated equivalent of 2-person households that could be powered by the daily wind and solar electricity.")
    # add selected date
    st.markdown(f"**Currently Selected Date:** {date_choice}")
    st.markdown("")

# Creating the columns layout for the UI with adjusted ratios for responsiveness
col1, col2 = st.columns([1.8, 1], vertical_alignment="center")

with col1:
    # create bokeh electricity production plot
    # see bokeh_plot.py for more information
    pred_cons = generate_energy_forecast_plot(predictions_df, st.session_state.consumption_df)
    st.bokeh_chart(pred_cons, use_container_width=True)


with col2:
    # how many 2 person households could be powered with the daily amount of produced wind and solar electricity (rough approximation)
    # see household_calc.py for more information 
    total_households_latest = household(predictions_df, date_choice)

    # box style for presenting houshold calculation
    st.markdown(f"""
        <div style='border: 1px solid #ddd; padding: 33px; display: flex; flex-direction: column; align-items: center; justify-content: center;'>
            <div style='display: flex; align-items: center;'>
                <img src='https://img.icons8.com/ios-filled/50/ffffff/home.png' style='margin-right: 10px;'/>
                <h3 style='margin: 0;'><b>~{total_households_latest}</b> Million two-person households</h3>
            </div>
            <hr style='width: 100%; margin: 20px 0; border: none; border-top: 1px solid #ccc;'/>
            <p style='font-size: 12px; color: #31708f; text-align: center;'>
                Private households add up to about 28% to <a href="https://de.statista.com/statistik/daten/studie/236757/umfrage/stromverbrauch-nach-sektoren-in-deutschland/" target="_blank" style='color: #31708f; text-decoration: underline;'>overall electricity consumption</a>. 
                43% is consumed by industry, 26% by trade & service, 3% by Mobility (statista).
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)


# Creating the columns layout for the UI with adjusted ratios for responsiveness
# text input second level
col1, col2 = st.columns([1.8, 1], vertical_alignment="top")

with col1:
    # add some info for the map
    st.markdown("### Geographic Contribution")
    st.markdown("""Geographical distribution of wind and solar electricity production across federal states and offshore locations. The layer wind and solar can be chosen in the map. 
                The date can be adjusted in the sidebar. Data is based on nominal installed capacity for wind and solar per federal state and the daily predictions.""")
with col2:
    st.markdown("### CO2 Emissions Savings")
    st.markdown("""Estimated CO2 savings achieved by the renewable electricity produced for the selected date. Savings are calculated based on averaged CO2 emissions from conventional fossil fuels
                and the produced electricity by wind and solar for the predicted days.""")


# Creating the columns layout for geographic & co2-savings depiction
col1, col2 = st.columns([1.8, 1], vertical_alignment="center")
    
with col1:
    # add selected date
    st.markdown(f"**Currently Selected Date:** {date_choice}")
    # create the map and add spinner for loading time
    # see folium_map.py for more information
    with st.spinner('Calculating predictions, please wait...'):
        m = create_map(geo_df, date_choice, st.session_state.df_offshore)
    # this activates the map
    folium_static(m, width=500, height=500) # , width=500, height=500

with col2:
    # add selected date
    st.markdown(f"**Currently Selected Date:** {date_choice}")
    # create the co2 savings plot and add spinner for loading time
    # see co2_visual.py for more information
    with st.spinner('Calculating predictions, please wait...'):
        emissions = saved_emissions(predictions_df, date_choice)
    st.bokeh_chart(emissions, use_container_width=True)

st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)
# add federal state production plot below the columns
st.markdown("### Daily Electricity Production by State")
st.markdown("Electricity production for all predicted days and the chosen federal state or offshore location.")
# add selected federal state 'state_choice'
st.markdown(f"**Currently Selected State/Region:** {state_choice}")
# create the federal state contribution plot and add spinner for loading time
# see fed_state_bokeh.py for more information
with st.spinner('Calculating predictions, please wait...'):
    fed_plot = create_fed_state_production_plot(geo_df, state_choice, st.session_state.df_offshore)
st.bokeh_chart(fed_plot, use_container_width=True)