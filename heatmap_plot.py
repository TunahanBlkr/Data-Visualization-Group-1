import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


def show_heatmap_plot(df):
    st.subheader("2D Matrix Heatmap: Daily Medal Performance by Country")

    col1, col2, col3 = st.columns(3)
    with col1:
        top_n_countries = st.slider(
            "How many top countries to show?", min_value=5, max_value=35, value=15
        )
    with col2:
        medal_filter = st.selectbox(
            "Medal Type",
            options=["All", "Gold Medal", "Silver Medal", "Bronze Medal"],
        )
    with col3:
        disciplines = sorted(df["discipline"].dropna().unique().tolist())
        discipline_filter = st.selectbox(
            "Discipline Filter (Optional)",
            options=["All Disciplines", *disciplines],
        )

    filtered_df = df.dropna(subset=["medal_date", "country"])

    if medal_filter != "All":
        filtered_df = filtered_df[filtered_df["medal_type"] == medal_filter]

    if discipline_filter != "All Disciplines":
        filtered_df = filtered_df[filtered_df["discipline"] == discipline_filter]

    if filtered_df.empty:
        st.warning("No data found matching the selected filters.")
        return

    top_countries = (
        filtered_df["country"]
        .value_counts()
        .nlargest(top_n_countries)
        .index.tolist()
    )
    matrix_df = filtered_df[filtered_df["country"].isin(top_countries)].copy()

    # Preserve all tournament dates chronologically even if a specific filter yields 0 medals on a day
    all_dates = sorted(df["medal_date"].dropna().unique())
    date_labels = [pd.Timestamp(d).strftime("%d %b") for d in all_dates]
    matrix_df["date_str"] = matrix_df["medal_date"].dt.strftime("%d %b")

    def build_medal_matrix(subset: pd.DataFrame) -> pd.DataFrame:
        return pd.crosstab(
            index=subset["date_str"], columns=subset["country"]
        ).reindex(index=date_labels, columns=top_countries, fill_value=0)

    pivot_table = build_medal_matrix(matrix_df)

    fig = px.imshow(
        pivot_table,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="YlOrRd",
        labels={"x": "Country", "y": "Date (Day)", "color": "Medal Count"},
    )

    fig.update_layout(
        height=650,
        xaxis_title="Country (Sorted by Total Medals)",
        yaxis_title="Olympic Days (27 Jul - 11 Aug)",
        xaxis_tickangle=-45,
        yaxis={"type": "category"},
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
    )

    if medal_filter == "All":
        medal_types = ["Gold Medal", "Silver Medal", "Bronze Medal"]
        medal_matrices = [
            build_medal_matrix(matrix_df[matrix_df["medal_type"] == m_type]).values
            for m_type in medal_types
        ]
        custom_data = np.dstack(medal_matrices)

        fig.update_traces(
            customdata=custom_data,
            hovertemplate=(
                "<b>Date:</b> %{y}<br>"
                "<b>Country:</b> %{x}<br>"
                "<b>Total Medals:</b> %{z}<br>"
                "-------------------<br>"
                "🥇 <b>Gold:</b> %{customdata[0]}<br>"
                "🥈 <b>Silver:</b> %{customdata[1]}<br>"
                "🥉 <b>Bronze:</b> %{customdata[2]}"
                "<extra></extra>"
            ),
        )
    else:
        fig.update_traces(
            hovertemplate=(
                "<b>Date:</b> %{y}<br>"
                "<b>Country:</b> %{x}<br>"
                f"<b>{medal_filter}s:</b> %{{z}}"
                "<extra></extra>"
            )
        )

    st.plotly_chart(fig, width="stretch")