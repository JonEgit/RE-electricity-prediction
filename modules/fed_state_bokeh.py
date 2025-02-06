import re
from bokeh.plotting import figure
from bokeh.colors import RGB
import matplotlib.cm as colormaps
from bokeh.transform import dodge
from bokeh.models import ColumnDataSource, HoverTool, Span


def create_fed_state_production_plot(geo_df, state_choice, df_offshore):
    # # create dataframe of geo_pred function and predictions dataframe
    # geo_pred = geo_pred(gdf, predictions_df)

    # Filter data for the specified federal state
    if state_choice in ['North Sea', 'Baltic Sea']:
        # Handle offshore regions
        federal_state = df_offshore[df_offshore['region'] == state_choice.lower().replace(' ', '_')]
        # federal_state['date'] = pd.to_datetime(federal_state['date'], format='%d/%m/%y')
        dates = federal_state['date'].tolist()
        wind_contributions = federal_state['calculated_windpower'].tolist()
        solar_contributions = federal_state['solar_pv'].tolist()
    else:
        federal_state = geo_df[geo_df['GEN'] == state_choice]
  
        # Extract all columns with wind and solar contributions
        contribution_columns = [col for col in federal_state.columns if re.match(r'^(wind|solar)_contribution_\d{2}/\d{2}/\d{2}$', col)] #\d{2}-\d{2}$

        # Extract dates and corresponding wind and solar contributions
        dates = [col.split('_')[-1] for col in contribution_columns if 'solar' in col]
        wind_contributions = federal_state[[col for col in contribution_columns if 'wind' in col]].values.flatten()
        solar_contributions = federal_state[[col for col in contribution_columns if 'solar' in col]].values.flatten()


    # Convert 'cividis' colormap to RGB colors for Bokeh usage
    cividis_cmap = colormaps.get_cmap('cividis')
    solar_color = cividis_cmap(0.8)  # Yellowish tone
    wind_color = cividis_cmap(0.2)  # Blueish tone
    bokeh_solar_color = RGB(int(solar_color[0] * 255), int(solar_color[1] * 255), int(solar_color[2] * 255))
    bokeh_wind_color = RGB(int(wind_color[0] * 255), int(wind_color[1] * 255), int(wind_color[2] * 255))

    # Creating the ColumnDataSource for stacked bar chart
    source = ColumnDataSource(data={
        'dates': dates,
        'wind_contributions': wind_contributions,
        'solar_contributions': solar_contributions
    })

    # Creating the Bokeh plot
    p = figure(
        # title=f"Wind and Solar Electricity Production in {state_choice} (per day)", 
        x_range=dates, 
        tools="pan,wheel_zoom,box_zoom,reset,hover",
        height=300,
        width=800,
        background_fill_color='#2F2F2F',  # Dark background color
        border_fill_color='#2F2F2F',      # Dark border color
        outline_line_color=None           # No outline border
    )

    # Adding stacked bar chart
    p.vbar(x=dodge('dates', -0.25, range=p.x_range), top='wind_contributions', width=0.4, source=source, color=bokeh_wind_color, alpha = 0.8, legend_label="Wind Contribution")
    p.vbar(x=dodge('dates', 0.25, range=p.x_range), top='solar_contributions', width=0.4, source=source, color=bokeh_solar_color, alpha = 0.8, legend_label="Solar Contribution")

    # Adding value labels inside the bars for wind and solar contributions
    for i, (date, wind, solar) in enumerate(zip(dates, wind_contributions, solar_contributions)):
        p.text(x=date, y=wind - (wind * 0.1), text=[f"{wind:.2f}"], text_align="center", text_baseline="middle", text_color="white")
        p.text(x=date, y=solar - (solar * 0.1), text=[f"{solar:.2f}"], text_align="center", text_baseline="middle", text_color="white")


    p.title.text_color = "white"
    p.title.text_font_size = "14pt"
    p.xaxis.axis_label = "Date"
    p.xaxis.axis_label_text_color = "white"
    p.xaxis.major_label_text_color = "white"
    p.yaxis.axis_label = "Electricity Contribution (GWh)"
    p.yaxis.axis_label_text_color = "white"
    p.yaxis.major_label_text_color = "white"

    # Adjust legend position
    p.legend.label_text_color = "white"
    p.legend.background_fill_alpha = 0
    p.legend.border_line_alpha = 0
    p.add_layout(p.legend[0], 'right')

    # Adding hover tooltips
    hover = HoverTool()
    hover.tooltips = [
        ("Date", "@dates"),
        ("Wind Contribution (GWh)", "@wind_contributions"),
        ("Solar Contribution (GWh)", "@solar_contributions")
    ]
    p.add_tools(hover)

    # Adding a dashed thin vertical line on the fourth day
    vertical_line = Span(location=3, dimension='height', line_color='white', line_dash='dashed', line_width=1)
    p.add_layout(vertical_line)

    # Show the plot
    return p

# Example usage:
# create_fed_state_production_plot(gdf, predictions_df, federal_state_name='Bayern')
