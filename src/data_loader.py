import pandas as pd


def load_csv(path):
    df = pd.read_csv(path)

    rename_map = {
        "lat": "lat",
        "lon": "lon",
        "alt": "altitude",
        "millis": "millis",
        "vel": "speed",
        "ax": "ax",
        "ay": "ay",
        "az": "az",
        "gx": "gx",
        "gy": "gy",
        "gz": "gz",
    }

    df = df.rename(columns={c: rename_map.get(c.strip().lower(), c.strip()) for c in df.columns})

    required = ["lat", "lon", "altitude"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}. Found: {list(df.columns)}")

    df = df.dropna(subset=["lat", "lon", "altitude"]).copy()

    # Remove obviously invalid GPS points
    df = df[(df["lat"].abs() > 0.001) & (df["lon"].abs() > 0.001)]

    return df