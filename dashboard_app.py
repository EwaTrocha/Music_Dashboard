import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st

data = pd.read_csv("data/all_track_artist.csv")
data_top = pd.read_csv("data/chart_filter_release.csv")

# Changing "chart_week" for data format
data["chart_week"] = pd.to_datetime(data["chart_week"])
data_top["chart_week"] = pd.to_datetime(data_top["chart_week"], errors="coerce")


# Creatiing the year
data_top["year"] = data_top["chart_week"].dt.year

#Setting page
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded")


#Dashbord title
st.title ("Top 10 Tracks")
st.subheader ("Tracks with longest apperance on the chart from 2018 to 2024")

#st.write(f"**<span style='font-size: 36px;'>Top 10 Tracks</span>**", unsafe_allow_html=True)
#st.write(f"**<span style='font-size: 24px;'>Tracks with longest apperance on the chart from 2018 to 2024</span>**", unsafe_allow_html=True)

#Sidebar
select_year= st.sidebar.selectbox("Select Year:", sorted(data_top["year"].unique()))



top_10_tracks = (
    data_top[data_top["year"] == select_year]
    .groupby("name")["chart_week"]
    .count()
    .reset_index()
    .sort_values(by="chart_week", ascending=False)
    .head(10)
)

select_track = st.sidebar.selectbox("Select Track:", top_10_tracks["name"].unique())

st.sidebar.markdown("---")
st.sidebar.markdown("**About:**")

#Filter data for selected track
selected_data = data[data["name_x"] == select_track].iloc[0]
top_10_select = data_top[data_top["year"] == select_year]


# Create columns for dashboard
col1, col2 = st.columns([1,3], gap='medium')

#Column 1: Artist Info + Explicit

with col1:
    #Artist Info
    st.write(f"**<span style='font-size: 24px;'>Track Info</span>**", unsafe_allow_html=True)
    st.markdown(f"**Artist:**  <br><span style='font-size: 18px;'>{selected_data['name_y']}</span>", unsafe_allow_html=True)
    st.markdown(f"**Popularity:**  <br><span style='font-size: 18px;'>{selected_data['popularity']}</span>", unsafe_allow_html=True)
    st.markdown(f"**Followers:**  <br><span style='font-size: 18px;'>{selected_data['followers']}</span>", unsafe_allow_html=True)

    #Explicit info
    explicit = "Yes" if selected_data["explicit"] == True else "No"
    st.write(f"**Explicit:** {'Yes' if selected_data['explicit'] else 'No'}")

    #Top 10 tracks list
    top_10_year = data_top.groupby(["year", "name"])["chart_week"].count().sort_values(ascending=False).reset_index()
     # Rename columns
    #top_10_year.columns = ["Track Name", "# of Weeks"]
    selet_year_data = top_10_year[top_10_year["year"] == select_year]
    selet_year_data = selet_year_data.head(10)


    # Display the Table
    st.write(f"**<span style='font-size: 24px;'>Top 10 Tracks for {select_year}</span>**", unsafe_allow_html=True)
    st.dataframe(
        selet_year_data,
        hide_index=True,
        width=None,
        height=None
    )

#Coumn 2: Line Charts + KPI's

with col2:
    #Line chart
    data_perf = data.groupby(["name_x","chart_week"])["list_position"].mean()
    data_perf = data_perf.to_frame().reset_index()
    selected_performance = data_perf[data_perf["name_x"] == select_track]

    fig_perf = px.line(
        selected_performance,
        x = "chart_week",
        y = "list_position",
        title = f"Performance of '{select_track}",
        labels = {"chart_week": "Chart Week", "list_position": "List Positoin"},
        markers = True 
    )

    fig_perf.update_layout(
        yaxis=dict(autorange='reversed', title='List Position'),
        xaxis_title = "Chart Week",
        yaxis_title = "List Position",
        template = "plotly_white",
        title_font_size = 16
    )

    st.plotly_chart(fig_perf, use_container_width=True)

# KPI's : dancebility, tempo, energy, valence

    st.header("Audio Features")
    kpi_data = {
        'Danceability': selected_data['danceability'],
        'Tempo': selected_data['tempo'],
        'Energy': selected_data['energy'],
        'Valence': selected_data['valence']
    }

    kpi_cols = st.columns([1,1,1,1])

    for idx, (kpi,value) in enumerate(kpi_data.items()):
        with kpi_cols[idx]:
            st.metric(kpi, round(value,2))

