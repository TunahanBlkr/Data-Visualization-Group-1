import os
import time
import signal
import pandas as pd
import streamlit as st
import plotly.express as px
from threading import Thread
from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx

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

target_columns = [
    "name",
    "gender",
    "medal_type",
    "event_type",
    "medal_date",
    "is_medallist",
    "country_code",
]

df = pd.read_csv("medallists.csv", usecols=target_columns) #

if "selected_button" not in st.session_state:
    st.session_state.selected_button = None

left_column, right_column = st.columns([1, 5]) # Left Column - 16.66% // Right Column - 83.33%

# Menu Area
with left_column:
    st.caption("MENU")

    if st.button("Buton 1", key="button_1", use_container_width=True):
        st.session_state.selected_button = "Buton 1"
    
    if st.button("Buton 2", key="button_2", use_container_width=True):
        st.session_state.selected_button = "Buton 2"
    
    if st.button("Buton 3", key="button_3", use_container_width=True):
        st.session_state.selected_button = "Buton 3"
    
    if st.button("Buton 4", key="button_4", use_container_width=True):
        st.session_state.selected_button = "Buton 4"
    
    if st.button("Buton 5", key="button_5", use_container_width=True):
        st.session_state.selected_button = "Buton 5"
    
    if st.button("Buton 6", key="button_6", use_container_width=True):
        st.session_state.selected_button = "Buton 6"
    
    if st.button("Buton 7", key="button_7", use_container_width=True):
        st.session_state.selected_button = "Buton 7"
    
    if st.button("Buton 8", key="button_8", use_container_width=True):
        st.session_state.selected_button = "Buton 8"
    
    if st.button("Buton 9", key="button_9", use_container_width=True):
        st.session_state.selected_button = "Buton 9"
    

# Content Area
with right_column:
    st.caption("Content Area")
    if st.session_state.selected_button:
        st.info(f"**{st.session_state.selected_button}** selected.")
    else:
        st.info("No selection has been made yet.")