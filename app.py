import random
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
    "medal_code",
    "event_type",
    "discipline",
    "medal_date",
    "birth_date",
    "is_medallist",
    "country_code",
    "country",
]

df = pd.read_csv("medallists.csv", usecols=target_columns) #

#Derive 'age' column
df["medal_date"] = pd.to_datetime(df["medal_date"], errors="coerce")
df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")
df["age"] = ((df["medal_date"] - df["birth_date"]).dt.days / 365.25).round(1)

if "selected_button" not in st.session_state:
    st.session_state.selected_button = None

left_column, right_column = st.columns([1, 5]) # Left Column - 16.66% // Right Column - 83.33%

# Menu Area
with left_column:
    st.caption("MENU")

    if st.button("Violin Plot", key="button_1", use_container_width=True):
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
    if st.session_state.selected_button == "Buton 1":
        st.subheader("Age Distribution by Sport and Gender (Violin Plot)")

        # Celaning data
        violin_df = df.dropna(subset=["age", "discipline", "gender"]).copy()
        all_disciplines = sorted(violin_df["discipline"].unique())

        # Select randomly 3 disciplines at first
        if "selected_disc" not in st.session_state:
            st.session_state.selected_disc = random.sample(all_disciplines, 3)

        #Fields
        f_col1, f_col2 = st.columns([1, 3])
        
        with f_col1:
            st.write("") 
            if st.button("Randomly Select 3 Disciplines", use_container_width=True):
                st.session_state.selected_disc = random.sample(all_disciplines, 3)

        with f_col2:
            
            selected_disciplines = st.multiselect(
                "Select Disciplines:",
                options=all_disciplines,
                key="selected_disc"
            )
            

        #Filter the data according to selected disciplines
        filtered_violin_df = violin_df[
            (violin_df["discipline"].isin(selected_disciplines))
        ]

        # Plot Violin
        if filtered_violin_df.empty:
            st.warning("Select at least one discipline.")
        else:
            fig_violin = px.violin(
                filtered_violin_df,
                x="discipline",
                y="age",
                color="gender",
                title="Age Density by Selected Sports and Gender",
                labels={
                    "discipline": "Discipline",
                    "age": "Age",
                    "gender": "Gender"
                },
                color_discrete_sequence=["#2b5c8f", "#d95f02"]
            )

            fig_violin.update_layout(height=550, violinmode="group")          
            st.plotly_chart(fig_violin, use_container_width=True)

    
    elif st.session_state.selected_button:
        st.info(f"**{st.session_state.selected_button}** selected.")
    else:
        st.info("No selection has been made yet.")

