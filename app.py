from pathlib import Path

from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
from flask_caching import Cache

from src.data_loader import load_csv
from src.gps_processing import process_gps
from src.metrics import calculate_metrics
from src.plotting import make_3d_track, make_elevation_profile, make_grade_profile


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "Track Test data"
CACHE_DIR = BASE_DIR / "processed_cache"

CACHE_DIR.mkdir(exist_ok=True)


def find_csv_files():
    return sorted(DATA_DIR.rglob("*.csv"))


def cache_path_for_csv(csv_path):
    csv_path = Path(csv_path)
    safe_name = csv_path.stem.replace(" ", "_")
    return CACHE_DIR / f"{safe_name}.parquet"


def load_processed_data(csv_path):
    """
    Loads processed GPS data from Parquet cache if available.
    If not available, loads CSV, processes GPS, then saves cache.
    """
    csv_path = Path(csv_path)
    parquet_path = cache_path_for_csv(csv_path)

    if parquet_path.exists():
        return load_parquet(parquet_path)

    df = load_csv(csv_path)
    df = process_gps(df)

    df.to_parquet(parquet_path, index=False)

    return df


def load_parquet(parquet_path):
    import pandas as pd
    return pd.read_parquet(parquet_path)


def downsample_for_plot(df, max_points=10000):
    """
    Keeps the plotted data small enough for Plotly/Dash.
    Metrics should still use the full dataframe.
    """
    if len(df) <= max_points:
        return df

    step = max(1, len(df) // max_points)
    return df.iloc[::step].copy()


csv_files = find_csv_files()

app = Dash(__name__)

cache = Cache(app.server, config={
    "CACHE_TYPE": "filesystem",
    "CACHE_DIR": str(BASE_DIR / "dash_cache")
})


@cache.memoize()
def get_processed_data(csv_path):
    return load_processed_data(csv_path)


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

    df = get_processed_data(csv_path)

    if color_by not in df.columns:
        color_by = "altitude_smooth_m"

    plot_df = downsample_for_plot(df, max_points=10000)

    metrics = calculate_metrics(df)

    metrics_display = html.Div(
        [
            html.Div(f"{key}: {value}")
            for key, value in metrics.items()
        ]
    )

    return (
        make_3d_track(plot_df, color_by),
        make_elevation_profile(plot_df),
        make_grade_profile(plot_df),
        metrics_display,
    )


if __name__ == "__main__":
    app.run(debug=True)