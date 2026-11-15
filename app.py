import os
import time
import signal
import pandas as pd
import streamlit as st
from threading import Thread
from streamlit.runtime import get_instance

from violin_plot import show_violin_plot # Hasan
from sankey_plot import show_sankey_plot
from stacked_bar_plot import show_stacked_bar_plot

from parallel_plot import show_parallel_plot # Tunahan
from heatmap_plot import show_heatmap_plot
from polar_plot import show_polar_plot

from k_means_and_mekko_chart import show_mekko_page, show_scatter_plot, show_map_page # İsmail

st.set_page_config(layout="wide")

def monitor_connections():
    time.sleep(3)
    runtime = get_instance()
    
    while True:
        time.sleep(2)
        session_count = len(runtime._session_mgr.list_active_sessions())

        if session_count == 0:
            os.kill(os.getpid(), signal.SIGINT)
            break

if "monitor_started" not in st.session_state:
    st.session_state.monitor_started = True
    Thread(target=monitor_connections, daemon=True).start()

@st.cache_data
def load_data():
    cols = [
        "name", "gender", "medal_type", "medal_code", "event_type",
        "discipline", "medal_date", "birth_date", "is_medallist",
        "country_code", "country"
    ]
    data = pd.read_csv("medallists.csv", usecols=cols)
    data["medal_date"] = pd.to_datetime(data["medal_date"], errors="coerce")
    data["birth_date"] = pd.to_datetime(data["birth_date"], errors="coerce")
    data["age"] = ((data["medal_date"] - data["birth_date"]).dt.days / 365.25).round(1)
    return data

df = load_data()

if "selected_button" not in st.session_state:
    st.session_state.selected_button = None

left_column, right_column = st.columns([1, 5]) # Left Column - 16.66% // Right Column - 83.33%

# Menu Area
with left_column:
    st.caption("MENU")

    if st.button("Violin Plot", key="button_1", width="stretch"):
        st.session_state.selected_button = "Buton 1"
    
    if st.button("Sankey Diagram", key="button_2", width="stretch"):
        st.session_state.selected_button = "Buton 2"
    
    if st.button("Stacked Bar Chart", key="button_3", width="stretch"):
        st.session_state.selected_button = "Buton 3"
    
    if st.button("Parallel Coordinates Plot", key="button_4", width="stretch"):
        st.session_state.selected_button = "Buton 4"
    
    if st.button("Polar Chart", key="button_5", width="stretch"):
        st.session_state.selected_button = "Buton 5"
    
    if st.button("Heatmap Plot", key="button_6", width="stretch"):
        st.session_state.selected_button = "Buton 6"
    
    if st.button("Mekko Chart (K-Means)", key="button_7", width="stretch"):
        st.session_state.selected_button = "Buton 7"
    
    if st.button("PCA Scatter Plot (K-Means)", key="button_8", width="stretch"):
        st.session_state.selected_button = "Buton 8"
    
    if st.button("Cluster Maps (Decision Tree)", key="button_9", width="stretch"):
        st.session_state.selected_button = "Buton 9"
    

# Content Area
with right_column:
    st.caption("Content Area")
    if st.session_state.selected_button == "Buton 1":
        show_violin_plot(df)
    elif st.session_state.selected_button == "Buton 2":
        show_sankey_plot(df)
    elif st.session_state.selected_button == "Buton 3":
        show_stacked_bar_plot(df)
    elif st.session_state.selected_button == "Buton 4":
        show_parallel_plot(df)
    elif st.session_state.selected_button == "Buton 5":
        show_polar_plot(df)
    elif st.session_state.selected_button == "Buton 6":
        show_heatmap_plot(df)
    elif st.session_state.selected_button == "Buton 7":
        show_mekko_page()
    elif st.session_state.selected_button == "Buton 8":
        show_scatter_plot()
    elif st.session_state.selected_button == "Buton 9":
        show_map_page()
    else:
        st.info("No selection has been made yet.")