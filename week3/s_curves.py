## S-Curve Technology Diffusion Model Dashboard
## Made with Sweat and Tears and ChatGPT: https://chat.openai.com/share/8142378b-57e8-446e-8cff-b351c59f44bc


import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.graph_objs as go

# Define the adoption model for generating data
def adoption_model(t, alpha, ymax, y_prev):
    return y_prev + y_prev * alpha * (ymax - y_prev)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define a fixed sample size
sample_size = 100

# Generate the data once and store it
def generate_data(alpha_value, noise_scale):
    np.random.seed(42)
    time_steps = np.arange(sample_size)
    adoption_rate = np.zeros(sample_size)
    adoption_rate[0] = 0.1  # Starting value

    for i in range(1, sample_size):
        adoption_rate[i] = adoption_model(i, alpha_value, 1.0, adoption_rate[i - 1])

    observed_data = adoption_rate + np.random.normal(scale=noise_scale, size=sample_size)
    simulated_df = pd.DataFrame({'Time': time_steps, 'Adoption Rate': observed_data})
    
    return simulated_df

# Initial data with alpha and noise scale
alpha_start = 0.1
noise_scale_start = 0.1
simulated_df = generate_data(alpha_value=alpha_start, noise_scale=noise_scale_start)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("Technology Adoption Dashboard"),
    
    html.Label("Select Alpha (Growth Rate):"),
    dcc.Slider(
        id='alpha-slider',
        min=0,
        max=0.5,
        step=0.01,
        value=alpha_start
    ),
    
    html.Label("Select Noise Scale:"),
    dcc.Slider(
        id='noise-scale-slider',
        min=0.01,
        max=1.0,
        step=0.01,
        value=noise_scale_start
    ),
    
    html.Label("Select Subsample Size:"),
    dcc.Slider(
        id='subsample-size-slider',
        min=1,
        max=sample_size,  # Use the fixed sample size as the maximum value
        step=1,
        value=sample_size
    ),
    
    dcc.Graph(id='adoption-plot'),
    
    html.Div(id='alpha-hat-output')
])

# Define a function for estimating alpha
def estimate_alpha(t, adoption_rate, subsample_size):
    # Initialize alpha as 0.1 as a starting point
    alpha = 0.1
    
    for i in range(1, subsample_size):
        y_prev = adoption_rate[i - 1]
        y_current = adoption_rate[i]
        
        alpha += (y_current - y_prev) / (y_prev * (100 - y_prev))  # Use 100 as ymax
    
    # Normalize alpha
    #alpha /= subsample_size - 1
    
    return alpha

# Callback to update the scatter plot, alpha_hat, and adoption model plot
@app.callback(
    [Output('adoption-plot', 'figure'),
     Output('alpha-hat-output', 'children')],
    [Input('alpha-slider', 'value'),
     Input('subsample-size-slider', 'value'),
     Input('noise-scale-slider', 'value')]
)
def update_plot(selected_alpha, subsample_size, noise_scale):
    global simulated_df  # Use the global variable for simulated data
    
    # Regenerate data when alpha or noise scale changes
    simulated_df = generate_data(alpha_value=selected_alpha, noise_scale=noise_scale)
    
    # Select the subsample based on the slider value
    subsample = simulated_df.iloc[:subsample_size]
    
    scatter_fig = go.Figure()
    
    # Scatter trace for observed data
    scatter_fig.add_trace(go.Scatter(x=simulated_df['Time'], y=simulated_df['Adoption Rate'], 
                                     mode='markers', name='Simulated Data', marker=dict(size=8)))
    
    # Line trace for adoption model
    estimated_alpha = estimate_alpha(simulated_df['Time'], simulated_df['Adoption Rate'], subsample_size)
    
    adoption_rate_estimated = np.zeros(sample_size)
    adoption_rate_estimated[0] = 0.1  # Starting value
    
    for i in range(1, sample_size):
        adoption_rate_estimated[i] = adoption_model(i, estimated_alpha, 1.0, adoption_rate_estimated[i - 1])
    
    scatter_fig.add_trace(go.Scatter(x=simulated_df['Time'], y=adoption_rate_estimated, 
                                     mode='lines', name='Adoption Model', line=dict(width=2)))
    
    scatter_fig.update_layout(title=f'Technology Adoption (Alpha={selected_alpha}, Noise Scale={noise_scale}, Sample Size={subsample_size})',
                              xaxis_title='Time',
                              yaxis_title='Adoption Rate',
                              xaxis=dict(range=[0, 100]))  # Set the x-axis range from 0 to 100
    
    return scatter_fig, f'Estimated Alpha: {estimated_alpha:.4f}'

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
