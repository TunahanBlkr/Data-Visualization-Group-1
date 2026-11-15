import plotly.graph_objects as go
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

from k_means_and_mekko_chart import show_mekko_page, show_scatter_plot, show_map_page

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
    
    if st.button("Sankey Diagram", key="button_2", use_container_width=True):
        st.session_state.selected_button = "Buton 2"
    
    if st.button("Stacked Bar Chart", key="button_3", use_container_width=True):
        st.session_state.selected_button = "Buton 3"
    
    if st.button("Buton 4", key="button_4", use_container_width=True):
        st.session_state.selected_button = "Buton 4"
    
    if st.button("Buton 5", key="button_5", use_container_width=True):
        st.session_state.selected_button = "Buton 5"
    
    if st.button("Buton 6", key="button_6", use_container_width=True):
        st.session_state.selected_button = "Buton 6"
    
    if st.button("Mekko Chart (K-Means)", key="button_7", use_container_width=True):
        st.session_state.selected_button = "Buton 7"
    
    if st.button("PCA Scatter Plot (K-Means)", key="button_8", use_container_width=True):
        st.session_state.selected_button = "Buton 8"
    
    if st.button("Cluster Maps (Decision Tree)", key="button_9", use_container_width=True):
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
                color_discrete_map={"Male": "#2b5c8f", "Female": "#d95f02"},
                category_orders={"gender": ["Male", "Female"]}
            )

            fig_violin.update_layout(height=550, violinmode="group")          
            st.plotly_chart(fig_violin, use_container_width=True)

    elif st.session_state.selected_button == "Buton 2":
        st.subheader("Medal Flow: Gender ➔ Event Type ➔ Medal Type (Sankey Diagram)")

        # Cleaning data for Sankey
        sankey_df = df.dropna(subset=["gender", "event_type", "medal_type", "country"]).copy()

        # Make event_type codes more readable (ATH -> Individual, TEAM -> Team)
        sankey_df["event_category"] = sankey_df["event_type"].apply(
            lambda x: "Individual Event" if x in ["ATH", "HATH"] else "Team / Group Event"
        )

        # Country Selection (Empty = All Countries)
        all_countries = sorted(sankey_df["country"].unique())
        selected_countries = st.multiselect(
            "Filter by Country (Leave empty to see All Countries):",
            options=all_countries,
            default=[]
        )

        if selected_countries:
            sankey_df = sankey_df[sankey_df["country"].isin(selected_countries)]

        color_map = {
            "Male": "#2b5c8f",
            "Female": "#d95f02",
            "Individual Event": "#7570b3",
            "Team / Group Event": "#1b9e77",
            "Gold Medal": "#FFD700",
            "Silver Medal": "#C0C0C0",
            "Bronze Medal": "#CD7F32",
}

        # Create unique nodes (labels) for all 3 stages
        genders = [g for g in ["Male", "Female"] if g in sankey_df["gender"].unique()]
        events = [e for e in ["Individual Event", "Team / Group Event"] if e in sankey_df["event_category"].unique()]
        medals = ["Gold Medal", "Silver Medal", "Bronze Medal"]
        
        labels = genders + events + medals
        label_map = {label: i for i, label in enumerate(labels)}

        # Step 1 Links: Gender -> Event Category
        link1 = sankey_df.groupby(["gender", "event_category"]).size().reset_index(name="count")
        # Step 2 Links: Event Category -> Medal Type
        link2 = sankey_df.groupby(["event_category", "medal_type"]).size().reset_index(name="count")

        sources = [label_map[x] for x in link1["gender"]] + [label_map[x] for x in link2["event_category"]]
        targets = [label_map[x] for x in link1["event_category"]] + [label_map[x] for x in link2["medal_type"]]
        values = list(link1["count"]) + list(link2["count"])

        # Plot Sankey Diagram
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=25,
                thickness=25,
                line=dict(color="black", width=0.5),
                label=labels,
                color=[color_map[l] for l in labels]
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values
            )
        )])

        fig_sankey.update_layout(
            title_text="Flow of Medals from Gender to Event Category and Medal Type",
            height=550
        )
        st.plotly_chart(fig_sankey, use_container_width=True)

    elif st.session_state.selected_button == "Buton 3":
        st.subheader("Top Medallist Countries by Medal Type (Stacked Bar Chart)")

        # Cleaning data
        bar_df = df.dropna(subset=["country", "medal_type"]).copy()

        # Interactive Slider: Choose how many top countries to display
        top_n = st.slider("Select Number of Top Countries to Display:", min_value=5, max_value=30, value=15)

        # Find top N countries by total medallists
        top_countries = bar_df["country"].value_counts().nlargest(top_n).index
        filtered_bar_df = bar_df[bar_df["country"].isin(top_countries)]

        # Group by country and medal type
        medal_counts = filtered_bar_df.groupby(["country", "medal_type"]).size().reset_index(name="count")

        # Plot Stacked Bar Chart
        fig_bar = px.bar(
            medal_counts,
            x="country",
            y="count",
            color="medal_type",
            barmode="stack",
            title=f"Top {top_n} Countries Medal Breakdown (Gold, Silver, Bronze)",
            labels={
                "country": "Country",
                "count": "Number of Medallists",
                "medal_type": "Medal Type"
            },
            category_orders={
                "country": list(top_countries), # Sorts bars from highest total to lowest
                "medal_type": ["Gold Medal", "Silver Medal", "Bronze Medal"]
            },
            color_discrete_map={
                "Gold Medal": "#FFD700",
                "Silver Medal": "#C0C0C0",
                "Bronze Medal": "#CD7F32"
            }
        )

        fig_bar.update_layout(height=550, xaxis_tickangle=-30)
        st.plotly_chart(fig_bar, use_container_width=True)
    elif st.session_state.selected_button == "Buton 7":
        show_mekko_page()
    elif st.session_state.selected_button == "Buton 8":
        show_scatter_plot()
    elif st.session_state.selected_button == "Buton 9":
            show_map_page()
    elif st.session_state.selected_button:
        st.info(f"**{st.session_state.selected_button}** selected.")
    else:
        st.info("No selection has been made yet.")

