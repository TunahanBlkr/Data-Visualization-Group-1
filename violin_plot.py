import random
import plotly.express as px
import streamlit as st

def show_violin_plot(df):
    st.subheader("Age Distribution by Sport and Gender (Violin Plot)")

    # Cleaning data
    violin_df = df.dropna(subset=["age", "discipline", "gender"]).copy()
    all_disciplines = sorted(violin_df["discipline"].unique())

    # Select randomly 3 disciplines at first
    if "selected_disc" not in st.session_state:
        st.session_state.selected_disc = random.sample(all_disciplines, 3)

    # Fields
    f_col1, f_col2 = st.columns([1, 3])

    with f_col1:
        st.write("")
        if st.button("Randomly Select 3 Disciplines", width="stretch"):
            st.session_state.selected_disc = random.sample(all_disciplines, 3)

    with f_col2:
        selected_disciplines = st.multiselect(
            "Select Disciplines:",
            options=all_disciplines,
            key="selected_disc",
        )

    # Filter the data according to selected disciplines
    filtered_violin_df = violin_df[
        violin_df["discipline"].isin(selected_disciplines)
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
                "gender": "Gender",
            },
            color_discrete_map={"Male": "#2b5c8f", "Female": "#d95f02"},
            category_orders={"gender": ["Male", "Female"]},
        )

        fig_violin.update_layout(height=550, violinmode="group")
        st.plotly_chart(fig_violin, width="stretch")