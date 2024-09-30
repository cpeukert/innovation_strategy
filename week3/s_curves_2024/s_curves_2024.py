import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

# Generate time data
time = np.linspace(0, 20, 200)

# Logistic function parameters
L = 1  # Maximum value (market potential)
k = 1  # Growth rate
x0 = 10  # Midpoint (time of maximum growth rate)

# Logistic function
def logistic_function(t, L, k, x0):
    return L / (1 + np.exp(-k * (t - x0)))

market_potential = logistic_function(time, L, k, x0)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("S-shaped Diffusion Curve Visualization"),
    dcc.Graph(id='diffusion-curve'),
    html.Label("Number of Data Points:"),
    dcc.Slider(
        id='data-slider',
        min=5,
        max=200,
        step=1,
        value=5,
        marks={i: str(i) for i in range(0, 201, 20)}
    )
])

@app.callback(
    Output('diffusion-curve', 'figure'),
    [Input('data-slider', 'value')]
)
def update_graph(num_points):
    # Sample data points based on the slider value
    indices = np.linspace(0, len(time)-1, num_points).astype(int)
    sampled_time = time[indices]
    sampled_market = market_potential[indices]
    
    # Add random noise to the sampled market data
    noise_level = 0.1  # Adjust the noise level as needed (e.g., 0.1 for 10% noise)
    np.random.seed(42)  # For reproducibility
    noise = np.random.normal(0, noise_level * max(market_potential), size=sampled_market.shape)
    sampled_market_noisy = sampled_market + noise
    
    # Fit the logistic function to the noisy sampled data
    try:
        # Initial guesses for L, k, x0
        initial_guesses = [max(sampled_market_noisy), 1, np.median(sampled_time)]
        
        # Fit the logistic function
        popt, _ = curve_fit(
            logistic_function,
            sampled_time,
            sampled_market_noisy,
            p0=initial_guesses,
            maxfev=10000
        )
        
        # Extract fitted parameters
        L_fit, k_fit, x0_fit = popt
        
        # Generate predicted market potential using the fitted parameters
        predicted_market = logistic_function(time, L_fit, k_fit, x0_fit)
        
        # Create the predicted curve plot
        predicted_line = go.Scatter(
            x=time,
            y=predicted_market,
            mode='lines',
            name='Predicted',
            line=dict(dash='dash')
        )
        
    except Exception as e:
        # If fitting fails, set predicted_line to None
        predicted_line = None
        
    # Create scatter plot for noisy sampled data
    scatter = go.Scatter(
        x=sampled_time,
        y=sampled_market_noisy,
        mode='markers',
        name='Sampled Data (Noisy)'
    )
    
    # Create line plot for the actual diffusion curve
    actual_line = go.Scatter(
        x=time,
        y=market_potential,
        mode='lines',
        name='Actual'
    )
    
    # Prepare the data list for plotting
    data = [actual_line, scatter]
    if predicted_line:
        data.append(predicted_line)
    
    layout = go.Layout(
        xaxis={'title': 'Time'},
        yaxis={'title': 'Market Potential'},
        title='Diffusion Curve with Noisy Sampled Data and Prediction'
    )
    
    return {'data': data, 'layout': layout}

if __name__ == '__main__':
    app.run_server(debug=True)
