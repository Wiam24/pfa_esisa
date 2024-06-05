import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html

# Load the dataset
data = pd.read_csv('Clean_Input_Data.csv')
data.drop(columns='Unnamed: 0', inplace=True)

# Function to create and return a Dash app
def create_dash_app(flask_app):
    dash_app = Dash(__name__, server=flask_app, url_base_pathname='/dashboard/')

    # Create histogram for each column
    histograms = []
    for column in data.columns:
        if column not in ['CUST_ID', 'FRAUD_FLAG']:
            histograms.append(dcc.Graph(
                id=f'histogram-{column}',
                figure=px.histogram(data, x=column, color='FRAUD_FLAG', title=f'{column} Distribution by Fraud Flag')
            ))

    # Create pie chart for Fraud Flag distribution
    fig_pie = px.pie(data, names='FRAUD_FLAG', title='Fraud Flag Distribution')

    # Create scatter plot for Purchases vs. Payments with Fraud Flag as color
    fig_scatter = px.scatter(data, x='PURCHASES', y='PAYMENTS', color='FRAUD_FLAG', title='Purchases vs. Payments')

    # Define the layout of the dashboard
    dash_app.layout = html.Div(children=[
        html.H1(children='Credit Card Data Analysis Dashboard'),

        html.H2(children='Fraud Flag Distribution'),
        dcc.Graph(
            id='fraud-flag-dist',
            figure=fig_pie
        ),

        html.H2(children='Purchases vs. Payments'),
        dcc.Graph(
            id='purchases-vs-payments',
            figure=fig_scatter
        ),

        html.H2(children='Histograms of Features'),
        html.Div(children=histograms)
    ])

    return dash_app

if __name__ == '__main__':
    dash_app.run(debug=True, use_reloader=False)
