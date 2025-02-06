## folium-map electricity production per federal state

import pandas as pd
import folium
from branca.colormap import linear
from branca.element import MacroElement
from jinja2 import Template
import os


class BindColormap(MacroElement):
    """Binds a colormap to a given layer.

    Parameters
    ----------
    colormap : branca.colormap.ColorMap
        The colormap to bind.
    """
    def __init__(self, layer, colormap):
        super(BindColormap, self).__init__()
        self.layer = layer
        self.colormap = colormap
        self._template = Template(u"""
        {% macro script(this, kwargs) %}
            // Check if the layer is visible when the map loads, and set the legend accordingly
            if ({{this.layer.get_name()}}.options.show === true) {
                {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
            } else {
                {{this.colormap.get_name()}}.svg[0][0].style.display = 'none';
            }
    
            // Event listener for overlay add (to show legend)
            {{this._parent.get_name()}}.on('overlayadd', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
                }
            });

            // Event listener for overlay remove (to hide legend)
            {{this._parent.get_name()}}.on('overlayremove', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'none';
                }
            });
        {% endmacro %}
        """)

def create_map(data, date_choice, df_offshore): # predictions_df    

    # Resolve the absolute path to the turbine icon
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of create_map.py
    icon_path = os.path.join(script_dir, '../assets/turbine.png')  # Relative to streamlit_app.py

    # Ensure the path works
    if not os.path.exists(icon_path):
        raise FileNotFoundError(f"Turbine icon not found at {icon_path}")

    # Set initial map location and zoom level
    m = folium.Map(location=[53.1657, 10.4515], zoom_start=5, tiles='Cartodb Positron') # , width='100%' # 'cartodbdark_matter'; 'Cartodb Positron', width='80%', height='80%'
    # 'north_sea': [54.433, 6.317],  # Albatros coordinates for the North Sea
    #     'baltic_sea': [54.834, 14.068],
    # Define base colormaps for both layers
    solar_colormap = linear.YlOrRd_09.scale(data[f'solar_contribution_{date_choice}'].min(), data[f'solar_contribution_{date_choice}'].max())
    solar_colormap.caption = f"Solar Electricity Production [GWh]" # on {date_choice}
    # solar_colormap.caption_style = {'color': 'white'}
    wind_colormap = linear.YlGnBu_09.scale(data[f'wind_contribution_{date_choice}'].min(), data[f'wind_contribution_{date_choice}'].max())
    wind_colormap.caption = f"Wind Electricity Production [GWh]"  # on {date_choice}
    # wind_colormap.caption_style = {'color': 'white'}

    # Add wind contribution layer (default active)
    wind_layer = folium.FeatureGroup(name='Wind Contribution', control=True, overlay=True, show=True).add_to(m)
    folium.GeoJson(
        data,
        style_function=lambda feature: {
            'fillColor': wind_colormap(feature['properties'][f'wind_contribution_{date_choice}']),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7,
        },
        tooltip=folium.features.GeoJsonTooltip(
            fields=['region', f'wind_contribution_{date_choice}'],
            aliases=[f'Date: {date_choice} / Region:', f'Wind Contribution [GWh]:'],
            localize=True
        ),
        highlight_function=lambda x: {'weight': 3, 'color': 'yellow'},
        name="Wind Contribution"
    ).add_to(wind_layer)

    # Add solar contribution layer (default inactive)
    solar_layer = folium.FeatureGroup(name='Solar Contribution', control=True, overlay=True, show=False).add_to(m)
    folium.GeoJson(
        data,
        style_function=lambda feature: {
            'fillColor': solar_colormap(feature['properties'][f'solar_contribution_{date_choice}']),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7,
        },
        tooltip=folium.features.GeoJsonTooltip(
            fields=['region', f'solar_contribution_{date_choice}'],
            aliases=[f'Date: {date_choice} / Region:', f'Solar Contribution [GWh]:'],
            localize=True
        ),
        highlight_function=lambda x: {'weight': 3, 'color': 'yellow'},
        name="Solar Contribution"
    ).add_to(solar_layer)

    # Add Layer Control to switch between layers
    folium.LayerControl(collapsed=True).add_to(m)

    # Add colormap legends and bind to respective layers dynamically
    m.add_child(solar_colormap).add_child(wind_colormap)
    solar_colormap.position = 'bottomleft'
    wind_colormap.position = 'bottomleft'
    m.add_child(BindColormap(solar_layer, solar_colormap)).add_child(BindColormap(wind_layer, wind_colormap))

    # Approximate coordinates for North Sea and Baltic Sea
    offshore_coordinates = {
        'north_sea': [54.433, 6.317],  # Albatros coordinates for the North Sea
        'baltic_sea': [54.834, 14.068],  # Approximate coordinates for the Baltic Sea
    }

    formatted_date_choice = pd.to_datetime(date_choice).strftime('%d/%m/%y')
    df_offshore_filtered = df_offshore[df_offshore['date'] == formatted_date_choice]

        # Add markers for North Sea and Baltic Sea with dynamic values based on date_choice
    for _, row in df_offshore_filtered.iterrows():
        folium.Marker(
            location=offshore_coordinates[row['region']],
            popup=(
                f"<b>Date:</b> {formatted_date_choice}<br>"
                f"<b>Region:</b> {row['region'].replace('_', ' ').title()}<br>"
                f"<b>Wind Contribution:</b> {row['calculated_windpower']:.2f} GWh<br>"
                # f"<b>Solar Contribution:</b> {row['calculated_solarpower']:.2f} GWh"
            ),
            icon=folium.CustomIcon(
                icon_image=icon_path,  # Ensure this path is correct and accessible #'../assets/turbine.png'
                icon_size=(35, 35)
            )
        ).add_to(wind_layer)

    return m