import pandas as pd
import plotly.express as px
import streamlit as st


def show_polar_plot(df):
    st.subheader("Polar Chart: Medal Distribution Analysis")

    col1, col2, col3 = st.columns(3)
    with col1:
        top_n_disciplines = st.slider(
            "Top N Disciplines", min_value=5, max_value=20, value=12
        )
    with col2:
        gender_filter = st.selectbox(
            "Gender Filter",
            options=["All", "Male", "Female"],
        )
    with col3:
        event_filter = st.selectbox(
            "Event Type",
            options=["All"] + sorted(df["event_type"].dropna().unique().tolist()),
        )

    filtered_df = df.dropna(subset=["discipline", "medal_type", "country"])

    if gender_filter != "All":
        filtered_df = filtered_df[filtered_df["gender"] == gender_filter]

    if event_filter != "All":
        filtered_df = filtered_df[filtered_df["event_type"] == event_filter]

    if filtered_df.empty:
        st.warning("No data found matching the selected filters.")
        return

    top_disciplines = (
        filtered_df["discipline"]
        .value_counts()
        .nlargest(top_n_disciplines)
        .index.tolist()
    )

    medal_order = ["Gold Medal", "Silver Medal", "Bronze Medal"]
    color_map = {
        "Gold Medal": "#FFD700",
        "Silver Medal": "#C0C0C0",
        "Bronze Medal": "#CD7F32",
    }

    agg_df = (
        filtered_df[filtered_df["discipline"].isin(top_disciplines)]
        .groupby(["discipline", "medal_type"], as_index=False)
        .size()
        .rename(columns={"size": "medal_count"})
    )

    fig = px.bar_polar(
        agg_df,
        r="medal_count",
        theta="discipline",
        color="medal_type",
        category_orders={
            "discipline": top_disciplines,
            "medal_type": medal_order,
        },
        color_discrete_map=color_map,
        labels={
            "medal_count": "Medal Count",
            "discipline": "Discipline",
            "medal_type": "Medal Type",
        },
    )
    fig.update_traces(
        hovertemplate=(
            "<b>Discipline:</b> %{theta}<br>"
            "<b>Medal Count:</b> %{r}"
            "<extra>%{fullData.name}</extra>"
        )
    )

    fig.update_layout(
        height=650,
        bargap=0.05,
        polar={
            "radialaxis": {
                "visible": True,
                "showline": False,
                "gridcolor": "rgba(128,128,128,0.25)",
            },
            "angularaxis": {"direction": "clockwise", "rotation": 90},
        },
        margin={"l": 40, "r": 40, "t": 50, "b": 40},
    )

    st.plotly_chart(fig, width="stretch")