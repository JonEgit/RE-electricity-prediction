import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.transform import dodge
import matplotlib.cm as colormaps
from bokeh.colors.rgb import RGB


# Creating a DataFrame from the given CO2 gramms table
# original value is gCO2/KWh; predicted values are in GWh
# gCO2/GWh = gCO2/KWh*1000*1000
# tCO2/GWh = gCO2/GWh/1000/1000
# original values can be kept - units are changed to tonns of CO2/GWh but don't need to be transformed
def saved_emissions(predictions_df, date_choice):
    data = {
        'tco2_gwh': [358, 867, 1049],
        # 'co2_mwh': [358000, 867000, 1049000],
        # 'co2_gwh': [358000000, 867000000, 1049000000]
    }
    index = ['Gas', 'Coal', 'Lignite']

    df_co2 = pd.DataFrame(data, index=index)
    
    predictions_df_adj = predictions_df.copy()
    predictions_df_adj.index = predictions_df_adj.index.strftime('%d/%m/%y')
    # # Converting the values from grams to kilograms for each unit
    # df_kg = df_co2 / 1000

    # # Converting the values from kilograms to tonnes for each unit
    # df_tons = df_kg / 1000

    # drop columns of MWh and KWh
    # df_t_co2 = df_tons.drop(columns=['co2_kwh', 'co2_mwh'])

    # Calculate the CO2 saved by wind and solar each day for each fossil fuel type (in tons)
    fossil_types = df_co2.index
    for fossil in fossil_types:
        co2_per_gwh = df_co2.loc[fossil, 'tco2_gwh'] / 1_000 # convert from tons to kilotons
        predictions_df_adj[f'co2_saved_wind_{fossil}'] = predictions_df_adj['windpower'] * co2_per_gwh
        predictions_df_adj[f'co2_saved_solar_{fossil}'] = predictions_df_adj['solar_pv'] * co2_per_gwh

    # Select a specific day to visualize
    day_to_plot = date_choice

    # Prepare data for Bokeh plot
    fossil_labels = list(fossil_types)
    wind_savings = [predictions_df_adj.loc[day_to_plot, f'co2_saved_wind_{fossil}'] for fossil in fossil_types]
    solar_savings = [predictions_df_adj.loc[day_to_plot, f'co2_saved_solar_{fossil}'] for fossil in fossil_types]

    # Creating the ColumnDataSource for stacked bar chart
    source = ColumnDataSource(data={
        'fossil_types': fossil_labels,
        'wind_savings': wind_savings,
        'solar_savings': solar_savings
    })

    # Convert 'cividis' colormap to RGB colors for Bokeh usage
    cividis_cmap = colormaps.get_cmap('cividis')
    wind_color = cividis_cmap(0.2)  # Blueish tone
    solar_color = cividis_cmap(0.8)  # Yellowish tone
    bokeh_wind_color = RGB(int(wind_color[0] * 255), int(wind_color[1] * 255), int(wind_color[2] * 255))
    bokeh_solar_color = RGB(int(solar_color[0] * 255), int(solar_color[1] * 255), int(solar_color[2] * 255))

    # Creating the Bokeh plot
    p = figure(
        y_range=fossil_labels, 
        # title=f"CO2 Savings by Renewable Electricity Production {day_to_plot}", 
        tools="pan,wheel_zoom,box_zoom,reset,hover",
        height=500,
        width=800,
        background_fill_color='#2F2F2F',  # Dark background color
        border_fill_color='#2F2F2F',      # Dark border color
        outline_line_color=None           # No outline border
    )

    # Adding stacked bar chart
    p.hbar(y=dodge('fossil_types', 0, range=p.y_range), right='solar_savings', height=0.4, source=source, color=bokeh_solar_color, alpha = 0.8, legend_label="Solar CO2 Savings")
    p.hbar(y=dodge('fossil_types', 0, range=p.y_range), right='wind_savings', height=0.4, source=source, color=bokeh_wind_color, alpha = 0.8, legend_label="Wind CO2 Savings", left='solar_savings')

    # Adding titles and labels with specified colors
    p.title.text_color = "white"
    p.title.text_font_size = "14pt"
    p.xaxis.axis_label = "CO2 Saved (kilotons)"
    p.xaxis.axis_label_text_color = "white"
    p.xaxis.major_label_text_color = "white"
    p.xaxis.formatter.use_scientific = False  # Disable scientific notation on x-axis
    p.yaxis.axis_label = "Fossil Fuel Type"
    p.yaxis.axis_label_text_color = "white"
    p.yaxis.major_label_text_color = "white"

    # Adjust legend position and color
    p.legend.label_text_color = "white"
    p.legend.background_fill_alpha = 0
    p.legend.border_line_alpha = 0
    p.add_layout(p.legend[0], 'below')

    # Adding hover tooltips
    hover = HoverTool()
    hover.tooltips = [
        ("Fossil Fuel Type", "@fossil_types"),
        ("Wind CO2 Savings", "@wind_savings{0,0}"),
        ("Solar CO2 Savings", "@solar_savings{0,0}")
    ]
    p.add_tools(hover)

    # Show the plot
    return p

