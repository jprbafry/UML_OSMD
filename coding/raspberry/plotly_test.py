import dash
from dash import html, dcc
import plotly.graph_objects as go

app = dash.Dash(__name__)

# Create the gauge figure properly
gauge_fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=50,
        title={'text': "Temperature"},
        gauge={'axis': {'range': [0, 100]}}
    )
)

app.layout = html.Div([
    html.H2("Lab Dashboard"),
    dcc.Slider(0, 100, 1, value=50, id='slider'),
    dcc.Graph(id='gauge', figure=gauge_fig)
])

if __name__ == "__main__":
    app.run(debug=True)
