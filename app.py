from pathlib import Path

from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

from src.data_loader import load_csv
from src.gps_processing import process_gps
from src.metrics import calculate_metrics
from src.plotting import make_3d_track, make_elevation_profile, make_grade_profile


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "Track Test data"


def find_csv_files():
    return sorted(DATA_DIR.rglob("*.csv"))


csv_files = find_csv_files()

app = Dash(__name__)

app.layout = html.Div(
    style={"fontFamily": "Arial", "margin": "20px"},
    children=[
        html.Img(
            src="/assets/baja_logo.png",
            style={
                "width": "100%",
                "maxHeight": "180px",
                "objectFit": "contain",
                "backgroundColor": "black",
                "marginBottom": "20px",
            },
        ),

        html.H1("UC Baja 3D Track Dashboard"),

        html.Label("Select CSV file"),
        dcc.Dropdown(
            id="csv-selector",
            options=[
                {"label": str(path.relative_to(DATA_DIR)), "value": str(path)}
                for path in csv_files
            ],
            value=str(csv_files[0]) if csv_files else None,
            style={"width": "90%"},
        ),

        html.Label("Color track by", style={"marginTop": "15px", "display": "block"}),
        dcc.Dropdown(
            id="color-selector",
            options=[
                {"label": "Altitude", "value": "altitude_smooth_m"},
                {"label": "Grade %", "value": "grade_percent"},
                {"label": "Speed / Vel", "value": "speed"},
                {"label": "Ax", "value": "ax"},
                {"label": "Ay", "value": "ay"},
                {"label": "Az", "value": "az"},
            ],
            value="altitude_smooth_m",
            style={"width": "300px"},
        ),

        html.Div(id="metrics-box", style={"marginTop": "20px", "fontSize": "18px"}),

        dcc.Graph(id="track-3d", style={"height": "700px"}),

        dcc.Graph(id="elevation-profile", style={"height": "350px"}),

        dcc.Graph(id="grade-profile", style={"height": "350px"}),
    ],
)


@app.callback(
    Output("track-3d", "figure"),
    Output("elevation-profile", "figure"),
    Output("grade-profile", "figure"),
    Output("metrics-box", "children"),
    Input("csv-selector", "value"),
    Input("color-selector", "value"),
)
def update_dashboard(csv_path, color_by):
    if not csv_path:
        return go.Figure(), go.Figure(), go.Figure(), "No CSV files found."

    df = load_csv(csv_path)
    df = process_gps(df)

    if color_by not in df.columns:
        color_by = "altitude_smooth_m"

    metrics = calculate_metrics(df)

    metrics_display = html.Div(
        [
            html.Div(f"{key}: {value}")
            for key, value in metrics.items()
        ]
    )

    return (
        make_3d_track(df, color_by),
        make_elevation_profile(df),
        make_grade_profile(df),
        metrics_display,
    )


if __name__ == "__main__":
    app.run(debug=True)