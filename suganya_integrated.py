import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st

# Load data
data = pd.read_csv("data/all_track_artist.csv")
data_top = pd.read_csv("data/chart_filter_release.csv")

# Changing "chart_week" to datetime format
data["chart_week"] = pd.to_datetime(data["chart_week"])
data_top["chart_week"] = pd.to_datetime(data_top["chart_week"], errors="coerce")

# Creating the year column
data_top["year"] = data_top["chart_week"].dt.year

# Setting up Streamlit page
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dashboard title
st.title("Top 10 Tracks")
st.subheader("Tracks with longest appearance on the chart from 2018 to 2024")

# Sidebar for Year Selection
select_year = st.sidebar.selectbox(
    "Select Year:",
    ["Select"] + sorted(data_top["year"].unique().tolist()),
    help="Choose a year to filter tracks."
)

# Stop execution if "Select" is chosen for year
if select_year == "Select":
    st.sidebar.warning("Please select a year.")
    st.stop()

# Filter data based on selected year
top_10_tracks = (
    data_top[data_top["year"] == select_year]
        .groupby("name")["chart_week"]
        .count()
        .reset_index()
        .sort_values(by="chart_week", ascending=False)
        .head(10)
)

# Sidebar for Track Selection
select_track = st.sidebar.selectbox(
    "Select Track:",
    ["Select"] + top_10_tracks["name"].unique().tolist(),
    help="Choose a track to view details."
)

# Stop execution if "Select" is chosen for track
if select_track == "Select":
    st.sidebar.warning("Please select a track.")
    st.stop()

# Aggregating details
top_track_artist_grouped_chart_week = data.groupby("track_id").agg(
    min_rank_chart_week=("chart_week", "min"),
    max_rank_last_chart_week=("chart_week", "max"),
    track_name=("name_x", "first"),
    duration_ms=("duration_ms", "first"),
    release_date=("release_date", "first"),
    explicit=("explicit", "first"),
    danceability=("danceability", "first"),
    energy=("energy", "first"),
    tempo=("tempo", "first"),
    popularity=("popularity", lambda x: ", ".join(x.unique().astype(str))),
    followers=("followers", lambda x: ", ".join(x.unique().astype(str))),
    no_of_weeks_on_chart=("chart_week", "count"),
    artist_name=("name_y", lambda x: "|".join(x.unique())),
    artist_count=("name_y", lambda x: x.nunique())
).reset_index()

# Adding artist type
top_track_artist_grouped_chart_week['artist_type'] = top_track_artist_grouped_chart_week['artist_count'].apply(
    lambda x: 'Solo Artist' if x == 1 else 'Multiple Artists'
)

# no_of_weeks_on_chart
top_track_artist_grouped_chart_week['adjusted_weeks_on_chart'] = (
    top_track_artist_grouped_chart_week['no_of_weeks_on_chart'] / 
    top_track_artist_grouped_chart_week['artist_count']
    ).round(0).astype(int)

# Extracting release year
top_track_artist_grouped_chart_week['release_date'] = pd.to_datetime(top_track_artist_grouped_chart_week['release_date'])
top_track_artist_grouped_chart_week['release_year'] = top_track_artist_grouped_chart_week['release_date'].dt.year

# Clean column names
top_track_artist_grouped_chart_week.columns = top_track_artist_grouped_chart_week.columns.str.strip()

# Format duration
def format_duration(ms):
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    return f"{minutes}m {seconds}s"

filtered_data = top_track_artist_grouped_chart_week[top_track_artist_grouped_chart_week["track_name"] == select_track]
track_data = filtered_data.iloc[0]

# Extract track details
track_id = track_data["track_id"]
track_name = track_data["track_name"]
release_year = track_data["release_year"]
artist_names = track_data["artist_name"].split("|")
popularity = track_data["popularity"].split(", ")
followers = track_data["followers"].split(", ")
duration_ms = track_data["duration_ms"]
no_of_weeks_on_chart = track_data["adjusted_weeks_on_chart"]
artist_type = track_data["artist_type"]

# Format track duration
track_duration = format_duration(duration_ms)

# Sidebar for Artist Selection (if multiple artists are available)
if len(artist_names) > 1:
    selected_artist = st.sidebar.selectbox(
        "Select an Artist:",
        ["Select"] + artist_names,
        help="Choose an artist to view their details."
    )
else:
    selected_artist = artist_names[0]

# Main section: Display selected artist details
if selected_artist and selected_artist != "Select":
    artist_index = artist_names.index(selected_artist)
    artist_popularity = popularity[artist_index] if artist_index < len(popularity) else "Unknown"
    artist_followers = followers[artist_index] if artist_index < len(followers) else "Unknown"

    st.subheader(f"Details for Artist: {selected_artist}")
    st.write(f"**Popularity:** {artist_popularity}")
    st.write(f"**Followers:** {artist_followers}")

# Charts and KPIs
selected_data = data[data["name_x"] == select_track].iloc[0]

# Display all track and artist details in the main content area
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Track Details")
    st.write(f"**Track Name:** {track_name}")
    st.write(f"**Artist Type:** {artist_type}")
    st.write(f"**Duration:** {track_duration}")
    st.write(f"**Number of Weeks on Chart:** {no_of_weeks_on_chart}")
    
    # Add the Explicit field here
    explicit = "Yes" if selected_data["explicit"] else "No"
    st.write(f"**Explicit Content:** {explicit}")

    # Top 10 tracks table
    #top_10_year = data_top.groupby(["year", "name"])["chart_week"].count().sort_values(ascending=False).reset_index()
    #selet_year_data = top_10_year[top_10_year["year"] == select_year].head(10)
    #selet_year_data["year"] = selet_year_data["year"].astype(str)
    #st.write(f"**Top 10 Tracks for {select_year}**")
    #st.dataframe(selet_year_data, hide_index=True)

with col2:
    # Track performance chart
    data_perf = data.groupby(["name_x", "chart_week"])["list_position"].mean().reset_index()
    selected_performance = data_perf[data_perf["name_x"] == select_track]
    fig_perf = px.line(
        selected_performance,
        x="chart_week",
        y="list_position",
        title=f"Performance of '{select_track}'",
        markers=True
    )
    fig_perf.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Chart Week",
        yaxis_title="List Position",
        template="plotly_white"
    )
    st.plotly_chart(fig_perf, use_container_width=True)

    # KPIs
st.header("Audio Features")
kpi_data = {
    'Danceability': selected_data['danceability'],
    'Tempo': selected_data['tempo'],
    'Energy': selected_data['energy'],
    'Valence': selected_data['valence'],
    #'Explicit': "Yes" if selected_data['explicit'] else "No"  # Add explicit feature
}

# Display KPI metrics
kpi_cols = st.columns([1, 1, 1, 1])  # Increase columns by 1 to accommodate 'Explicit'
for idx, (kpi, value) in enumerate(kpi_data.items()):
    with kpi_cols[idx]:
        st.metric(kpi, value)
