import numpy as np


def calculate_metrics(df):
    total_distance = df["distance_m"].iloc[-1]

    elevation_gain = (
        df["altitude_smooth_m"].iloc[-1]
        - df["altitude_smooth_m"].iloc[0]
    )

    max_grade = df["grade_percent"].abs().max()
    max_angle = df["hill_angle_deg"].abs().max()

    if "speed" in df.columns:
        max_speed = df["speed"].max()
        avg_speed = df["speed"].mean()
    else:
        max_speed = np.nan
        avg_speed = np.nan

    return {
        "Total distance": f"{total_distance:.1f} m",
        "Net elevation change": f"{elevation_gain:.1f} m",
        "Max grade": f"{max_grade:.1f} %",
        "Max hill angle": f"{max_angle:.1f}°",
        "Max speed": f"{max_speed:.1f}" if not np.isnan(max_speed) else "N/A",
        "Average speed": f"{avg_speed:.1f}" if not np.isnan(avg_speed) else "N/A",
    }