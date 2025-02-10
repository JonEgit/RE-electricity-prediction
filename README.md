# Predicting wind and solar electricity in germany

## Content of this repository
Interactive streamlit dashboard which presents a set of visualizations of the prediction of electricity production by wind and photovoltaics in germany.

## Project Summary
As part of a 3 month data science and AI bootcamp at neuefische, students were required to create and present a final machine learning capstone project of their choice. For this project i implemented machine learning tools to predict electricity produced by wind an pv in germany based on weather forecast data. The repository at hand presents the code for the creation of the model and the implementation of the streamlit dashboard. The preceeding EDA and preprocessing process of the necessary data which i conducted is however not presented in this repository but will be added in the future.

For the project implementation followed these steps:
1. Data akquisition
1. Created an automated openMeteo API
1. Data preprocessing
1. Exploratory data analysis
1. Data cleaning and preperation for modeling (Scaling, Feature importance, ...) 
1. Comparison of different modelarchitectures and systems (multioutput vs singleoutput)
1. Model training
1. Model optimization and hyperparametertuning
1. Model finalization and testing
1. Created dynamic visualizations
1. Created a streamlit dashboard
1. Embedded model and scripts in dashboard
1. Finalized dashboard

Since the goal of this repository is to present the final product, it contains the following parts for its implementaion:
1. Already cleaned data for modeling and dashboard creation
1. Jupyter Notebook to train and recreate the final model and save it
1. Python scripts: API and visualization functions
1. Python script: dashboard creation with streamlit

How to use this repository:
1. Download (copy) repository to a folder in your local machine  and keep the folder structure.
1. Open a terminal and navigate to the newly created folder
1. Use the terminal to prepare your repo:
    1. For this project python 3.11.3 was used. To function properly it is advised to use the same version 
        1. `pyenv local 3.11.3`
    1. install a virtual environment 
        1. `python -m venv .venv`
        1. macOS: `source .venv/bin/activate` or
        1. PowerShell CLI: `.venv\Scripts\Activate.ps1` or
        1. Git-Bash CLI: `source .venv/Scripts/activate`
    1. install required packages:
        1. `pip install -r requirements.txt`

1. Train the **model** and the **scaler** by opening the jupyter notebook in the main folder and run the code (start the training). This will take about ~ 2-10 minutes. This only needs to be done once since **model** and **scaler** will be saved in the *models/* folder as pkl-file.
    1. Open and run **model_training.ipynb** in your preferred IDE
1. Go back to your terminal to start the app/dashboard. Make sure your still in your repository folder and your virtual environment is activated. The app will be hosted locally on your machine and open in your standard browser. The first time it loads will take a bit of time. If possible use a bigger screen. Overlapping might occur on smaller screens. Start the streamlit app by running:
    1. `streamlit run Dashboard.py`


Data Sources:
1. Bundesnetzagentur: https://www.smard.de
    1. 'realisierte erzeugung' - 3 years, daily (01/10/2021-30/09/2024)
    1. 'realisierter verbrauch' - 9 years, daily (01/10/2015-30/09/2024) (used as reference value, not for model predictions)
1. Bundesnetzagentur: https://www.bundesnetzagentur.de/
    1. nominal installed capacity per federal state in germany (As of: October 2024)
1. open Meteo: https://open-meteo.com
    1. set of meteorological variables of germany for 11 locations - 3 years, daily mean of 11 evenly distributed locations (01/10/2021-30/09/2024)
    1. automated request for present data for of the same set of meteorological variables of germany for 11 locations to create a mean value for each day of 3 historic and 7 predicted days for moedel predictions (see openMeteo_API.py)
1. Esri open data portal: https://opendata-esridech.hub.arcgis.com              
    1. Bundesländergrenzen 2022 (geojson)

