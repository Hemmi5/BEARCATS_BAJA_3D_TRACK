import plotly.graph_objects as go


def make_3d_track(df, color_by="altitude_smooth_m"):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter3d(
            x=df["x_m"],
            y=df["y_m"],
            z=df["altitude_smooth_m"],
            mode="lines+markers",
            marker=dict(
                size=3,
                color=df[color_by],
                colorscale="Viridis",
                colorbar=dict(title=color_by),
            ),
            line=dict(
                width=5,
                color=df[color_by],
                colorscale="Viridis",
            ),
            text=[
                f"Distance: {d:.1f} m<br>"
                f"Alt: {a:.1f} m<br>"
                f"Grade: {g:.1f}%"
                for d, a, g in zip(
                    df["distance_m"],
                    df["altitude_smooth_m"],
                    df["grade_percent"].fillna(0),
                )
            ],
            hoverinfo="text",
        )
    )

    fig.update_layout(
        title="3D Track View",
        scene=dict(
            xaxis_title="East/West [m]",
            yaxis_title="North/South [m]",
            zaxis_title="Altitude [m]",
            aspectmode="data",
        ),
        margin=dict(l=0, r=0, t=40, b=0),
    )

    return fig


def make_elevation_profile(df):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["distance_m"],
            y=df["altitude_smooth_m"],
            mode="lines",
            name="Elevation",
        )
    )

    fig.update_layout(
        title="Elevation vs Distance",
        xaxis_title="Distance [m]",
        yaxis_title="Altitude [m]",
        margin=dict(l=40, r=20, t=40, b=40),
    )

    return fig


def make_grade_profile(df):
    fig = go.Figure()

    valid = df["distance_m"].notna() & df["grade_percent"].notna()

    fig.add_trace(
        go.Scatter(
            x=df.loc[valid, "distance_m"],
            y=df.loc[valid, "grade_percent"],
            mode="lines",
            name="Grade",
            line=dict(color="red", width=3),
            connectgaps=True,
        )
    )

    fig.update_layout(
        title="Grade vs Distance",
        xaxis_title="Distance [m]",
        yaxis_title="Grade [%]",
        template="plotly_white",
        margin=dict(l=40, r=20, t=40, b=40),
    )

    return fig