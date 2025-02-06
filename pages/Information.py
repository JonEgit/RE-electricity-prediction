# Information

import streamlit as st

# Project Overview Page
# Set page configuration to set a custom page name
# st.set_page_config(page_title="Project Overview", layout="wide")
# Set page configuration
st.set_page_config(
    page_title="Project Overview",  # This will be the title of the page
    page_icon=":info:",  # You can also set an emoji as the icon
    layout="wide"  # Sets the layout, options are 'centered' or 'wide'
)


st.title("Renewable Electricity Production Forecast - Project Overview")

## Project Description
st.markdown("""
## Project Description

This project aims to forecast the renewable electricity production for various regions, including both onshore and offshore areas. The application visualizes these predictions interactively through different charts, geographic maps, and other data-driven insights. Users can gain a better understanding of how renewable sources, specifically wind and solar, contribute to electricity production, and also observe the resulting environmental benefits, like CO2 savings.

The application is intended for stakeholders in the renewable energy sector, policymakers, and researchers who want to explore the potential of renewable energy production for different timeframes and geographical locations.
""")

## Key Features
st.markdown("""
## Key Features

### 1. Daily Renewable Production Forecast

The app uses machine learning models trained on historical weather and energy production data to provide forecasts of renewable electricity production for the next seven days. These forecasts help visualize potential energy contributions from wind and solar power in different regions.

### 2. Interactive Weather Visualization

- **Weather Data Display**: The app shows detailed daily weather forecasts, including wind speed, sunshine duration, and precipitation levels.
- **Interactive Elements**: Users can scroll through the weather columns to understand daily variations in the meteorological parameters that directly impact renewable electricity production.

### 3. Geographic Map of Renewable Contributions

The app integrates a geographic map that presents wind and solar energy contributions by region, including offshore areas like the North Sea and the Baltic Sea. Users can interact with the map to learn more about the spatial distribution of energy production.

### 4. CO2 Emissions Savings Calculation

The CO2 emissions savings module provides insights into the environmental benefits of renewable energy production. This chart shows how much carbon dioxide has been saved by replacing conventional energy sources with wind and solar.

### 5. Data Download Options

Users can download the data used in the app, including energy predictions and geographical datasets. This feature is helpful for stakeholders interested in conducting further analyses on the data.
""")

## User Interaction
st.markdown("""
## User Interaction

- **Sidebar Controls**: The sidebar allows users to select a specific date and region to explore. Options for North Sea and Baltic Sea are also available to understand offshore contributions.
- **Tooltips and Descriptions**: Each chart and dropdown in the app has been supplemented with intuitive descriptions and tooltips to guide users through the features.
- **Download Data**: Users can select and download the data used in the forecasts to perform their own analysis or to keep a copy for further reference.
""")

## Technologies Used
st.markdown("""
## Technologies Used

- **Python** and **Streamlit**: Used for the overall app development, data preprocessing, and visualization.
- **Folium**: Used for creating the interactive geographic map to represent regional contributions of renewable energy.
- **Bokeh**: Used for visualizing energy production forecasts and CO2 emissions savings.
- **OpenMeteo API**: For fetching weather data needed to predict renewable energy production.
- **Pandas & GeoPandas**: For data management, transformation, and spatial operations.
""")

## Future Enhancements
st.markdown("""
## Future Enhancements

- **Enhanced UI**: Add more sophisticated UI components and improve mobile responsiveness.
- **More Detailed Regional Analysis**: Include additional regions and more granular data for even better insights.
- **User Authentication**: Allow for secure login so that users can save their analysis and come back later.
""")

## How to Use
st.markdown("""
## How to Use

1. **Select a Date**: Use the sidebar to choose a specific date to see the weather and energy forecast for that day.
2. **Select a Region**: Pick a federal state or offshore region to understand the contribution of renewable energy from that specific location.
3. **Explore Charts and Maps**: Scroll through the interactive charts and geographic maps to gain insights.
4. **Download Data**: Use the download option in the sidebar to save data of interest.
""")

st.markdown("Feel free to reach out if you need more information or want to contribute to this project!")
