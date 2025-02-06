## openMeteo API

# load packages
import openmeteo_requests
import requests_cache
import requests
from retry_requests import retry

import pandas as pd
import datetime
import streamlit as st

# Function to fetch weather forecast data from OpenMeteo API
def get_weather_forecast(days, past_days):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # List of cities
    cities = [
        {"city": "Emden", "latitude": 53.367, "longitude": 7.207},
        {"city": "Hamburg", "latitude": 53.551, "longitude": 9.993},
        {"city": "Greifswald", "latitude": 54.093, "longitude": 13.387},
        {"city": "Braunschweig", "latitude": 52.268, "longitude": 10.526},
        {"city": "Köln", "latitude": 50.937, "longitude": 6.960},
        {"city": "Kassel", "latitude": 51.316, "longitude": 9.498},
        {"city": "Dresden", "latitude": 51.050, "longitude": 13.738},
        {"city": "Freiburg", "latitude": 47.999, "longitude": 7.842},
        {"city": "Würzburg", "latitude": 49.791, "longitude": 9.953},
        {"city": "Augsburg", "latitude": 48.370, "longitude": 10.897},
        {"city": "Passau", "latitude": 48.574, "longitude": 13.460},
        {"city": "Albatros", "latitude": 54.433, "longitude": 6.317}, # Windfarm northsea
        {"city": "Wikinger", "latitude": 54.834, "longitude": 14.068} # Windfarm baltic sea
    ]

    # Initialize an empty DataFrame to collect all the data
    df = pd.DataFrame()

    # Iterate over each city and request weather data
    for city in cities:
        try:
            # Prepare parameters for each city
            params = {
                "latitude": city["latitude"],
                "longitude": city["longitude"],
                "daily": [
                    "temperature_2m_max", "temperature_2m_min", 
                    "apparent_temperature_max", "apparent_temperature_min",
                    "daylight_duration", "sunshine_duration", "precipitation_sum", 
                    "precipitation_hours", "snowfall_sum",
                    "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant",
                    "shortwave_radiation_sum"
                ],
                "timezone": "Europe/Berlin",
                "forecast_days": days,
                "past_days": past_days
            }

            # Make the API request for each city
            response = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
            if response.status_code == 200:
                data = response.json()
                daily_data = data.get('daily', {})
                if not daily_data:
                    raise ValueError("Daily weather data not found in the response.")

                daily_dataframe = pd.DataFrame(daily_data)
                daily_dataframe["date"] = pd.to_datetime(daily_dataframe["time"])
                daily_dataframe["city"] = city["city"]

                # Append city data to the complete DataFrame
                weather_data = pd.concat([df, daily_dataframe], ignore_index=True)
            else:
                print(f"Failed to load weather forecast data for city {city['city']}. HTTP status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error loading data for city {city['city']}: Network error - {e}")
        except ValueError as e:
            print(f"Error loading data for city {city['city']}: Data error - {e}")
        except Exception as e:
            print(f"Error loading data for city {city['city']}: {e}")

    return weather_data



# Function to determine if data needs to be updated
def refresh_data_if_needed():
    current_date = datetime.datetime.now().date()

    # Check if 'last_fetch_date' is in session_state
    if 'last_fetch_date' not in st.session_state or st.session_state.last_fetch_date != current_date:
        # If date has changed or data not fetched yet, load new data
        st.session_state.weather_data = get_weather_forecast(7,3)
        st.session_state.last_fetch_date = current_date
