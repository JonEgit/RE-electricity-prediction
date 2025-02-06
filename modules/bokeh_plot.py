import pandas as pd
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, HoverTool, Span, DatetimeTickFormatter, DaysTicker
from bokeh.palettes import Viridis256
from bokeh.colors import RGB
import matplotlib.cm as colormaps
# from bokeh.io import output_notebook
# only needed for depictions in jupyter notebooks not for python scripts
# output_notebook()

def generate_energy_forecast_plot(predictions_df, consumption_df):
    """
    Generates an energy forecast plot showing renewable energy production versus average consumption.

    Parameters:
    - forecast_days (int): Number of days for weather forecast.
    - model_path (str): Path to the pre-trained model file.
    - consumption_data_path (str): Path to the CSV file with average consumption data.
    - output_html_path (str): Path to save the output HTML file of the plot.
    """

    predictions_df = predictions_df.reset_index()
    predictions_df['date'] = pd.to_datetime(predictions_df['date'])

    # Determine if prediction dates are weekends or weekdays
    predictions_df['day_of_week'] = predictions_df['date'].dt.weekday
    predictions_df['is_weekend'] = predictions_df['day_of_week'] >= 5

    # Extract corresponding average consumption
    avg_consumptions = []
    for date in predictions_df['date']:
        calendar_day = date.strftime('%m-%d')
        avg_row = consumption_df[consumption_df['calendar_day'] == calendar_day]
        if not avg_row.empty:
            if predictions_df.loc[predictions_df['date'] == date, 'is_weekend'].values[0]:
                avg_consumptions.append(avg_row['avg_weekend_consumption'].values[0])
            else:
                avg_consumptions.append(avg_row['avg_weekday_consumption'].values[0])
        else:
            avg_consumptions.append(None)
    predictions_df['avg_consumption'] = avg_consumptions

    # Set theme for the plot - deactivate because of interference with streamlit
    curdoc().theme = None #'dark_minimal'

    # Prepare data for Bokeh plot
    predictions_df['total_renewable'] = predictions_df['windpower'] + predictions_df['solar_pv']
    source = ColumnDataSource(predictions_df)

    # Create the Bokeh plot
    p = figure(
        x_axis_type='datetime', 
        # title='Renewable Electricity Production vs. Average Consumption', 
        height=300, width=800, 
        tools='pan,box_zoom,reset,save', 
        toolbar_location='above',
        background_fill_color='#2F2F2F',  # Dark background color
        border_fill_color='#2F2F2F',      # Dark border color
        outline_line_color=None
    )

    # Convert 'cividis' colormap to RGB colors for Bokeh usage
    cividis_cmap = colormaps.get_cmap('cividis')
    solar_color = cividis_cmap(0.8)  # Yellowish tone
    wind_color = cividis_cmap(0.2)  # Blueish tone
    bokeh_solar_color = RGB(int(solar_color[0] * 255), int(solar_color[1] * 255), int(solar_color[2] * 255))
    bokeh_wind_color = RGB(int(wind_color[0] * 255), int(wind_color[1] * 255), int(wind_color[2] * 255))

    # Plot windpower and solar production
    p.varea(x='date', y1=0, y2='windpower', source=source, fill_color=bokeh_wind_color, alpha=0.8, legend_label='Windpower') #Viridis256[100]
    p.varea(x='date', y1='windpower', y2='total_renewable', source=source, fill_color=bokeh_solar_color, alpha=0.8, legend_label='Solar PV') #Viridis256[150]

    # Plot average consumption
    p.line(x='date', y='avg_consumption', source=source, color='black', line_dash='dashed', line_width=2, legend_label='Average Consumption')

    # Fill areas for deficit and surplus
    # deficit_color = Viridis256[50]
    surplus_color = Viridis256[200]
    # p.varea(x='date', y1='total_renewable', y2='avg_consumption', source=source,
    #         fill_color=deficit_color, fill_alpha=0.2, legend_label='Deficit Area', hatch_pattern='//') #deficit_color
    p.varea(x='date', y1='avg_consumption', y2='total_renewable', source=source,
            fill_color=surplus_color, fill_alpha=0.2, legend_label='Surplus/Deficit', hatch_pattern='xx') #surplus_color

    # Add hover tool
    hover = HoverTool(tooltips=[
        # ('Date', '@date{%F}'),
        ('Windpower', '@windpower{0.0} GWh'),
        ('Solar PV', '@solar_pv{0.0} GWh'),
        ('Total Renewable', '@total_renewable{0.0} GWh'),
        ('Avg Consumption', '@avg_consumption{0.0} GWh')
    ], formatters={'@date': 'datetime'})
    p.add_tools(hover)

    # Additional formatting
    p.legend.click_policy = 'hide'
    p.legend.location = 'bottom_center'  # Position the legend at the bottom center
    p.legend.orientation = 'horizontal'  # Arrange the legend entries horizontally
    p.add_layout(p.legend[0]) #, 'right'
    
    # Add a background color and style to the legend
    p.legend.background_fill_color = 'lightgray'  # Set the background color
    p.legend.label_text_color = "white"
    p.legend.background_fill_alpha = 0.2 # Set the transparency of the background
    p.legend.border_line_alpha = 0

    # Add a dashed vertical line for "Today"
    today_date = predictions_df['date'].iloc[3]
    vline_today = Span(location=today_date.timestamp() * 1000, 
                       dimension='height', line_color='white', line_dash='dashed', line_width=1)
    p.add_layout(vline_today)

    # Ensure all dates on x-axis
    p.xaxis[0].ticker = DaysTicker(days=list(range(1, 32)))
    p.xaxis.formatter = DatetimeTickFormatter(days="%d/%m")# "%d/%m/%y"

    # Set the rest of the properties explicitly
    p.title.text_color = "white"
    p.title.text_font_size = "14pt"
    p.xaxis.major_label_text_color = "white"
    p.yaxis.major_label_text_color = "white"
    p.yaxis.axis_label_text_color = "white"
    p.yaxis.axis_label = 'Electricity Production (GWh)'
    p.axis.axis_line_color = "white"
    p.grid.grid_line_color = "gray"
    p.legend.label_text_color = "white"

    # return the plot
    return p
