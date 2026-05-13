import numpy as np
from pyproj import Transformer


def latlon_to_local_meters(df):
    df = df.copy()

    lat0 = df["lat"].iloc[0]
    lon0 = df["lon"].iloc[0]

    utm_zone = int((lon0 + 180) / 6) + 1
    epsg = 32600 + utm_zone if lat0 >= 0 else 32700 + utm_zone

    transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)

    east, north = transformer.transform(df["lon"].to_numpy(), df["lat"].to_numpy())

    df["x_m"] = east - east[0]
    df["y_m"] = north - north[0]

    return df


def process_gps(df):
    df = df.copy()
    df = latlon_to_local_meters(df)

    dx = df["x_m"].diff()
    dy = df["y_m"].diff()

    df["segment_distance_m"] = np.sqrt(dx**2 + dy**2).fillna(0)
    df["distance_m"] = df["segment_distance_m"].cumsum()

    df["altitude_smooth_m"] = (
        df["altitude"]
        .rolling(window=9, center=True, min_periods=1)
        .mean()
    )

    df["delta_alt_m"] = df["altitude_smooth_m"].diff()
    
    min_segment_m = 0.25  # ignore near-zero GPS movement
    valid_segment = df["segment_distance_m"] > min_segment_m

    df["grade"] = np.nan
    df.loc[valid_segment, "grade"] = (
        df.loc[valid_segment, "delta_alt_m"] /
        df.loc[valid_segment, "segment_distance_m"]
    )

    df["grade_percent"] = df["grade"] * 100
    df["hill_angle_deg"] = np.degrees(np.arctan(df["grade"]))
    df["grade_percent"] = df["grade"] * 100
    df["hill_angle_deg"] = np.degrees(np.arctan(df["grade"]))

    df = df.replace([np.inf, -np.inf], np.nan)

    return df