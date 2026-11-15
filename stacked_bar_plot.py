import plotly.express as px
import streamlit as st


def show_stacked_bar_plot(df):
    st.subheader("Top Medallist Countries by Medal Type (Stacked Bar Chart)")

    # Cleaning data
    bar_df = df.dropna(subset=["country", "medal_type"]).copy()

    # Interactive Slider: Choose how many top countries to display
    top_n = st.slider(
        "Select Number of Top Countries to Display:",
        min_value=5,
        max_value=30,
        value=15,
    )

    # Find top N countries by total medallists
    top_countries = bar_df["country"].value_counts().nlargest(top_n).index
    filtered_bar_df = bar_df[bar_df["country"].isin(top_countries)]

    # Group by country and medal type
    medal_counts = (
        filtered_bar_df.groupby(["country", "medal_type"])
        .size()
        .reset_index(name="count")
    )

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
            "medal_type": "Medal Type",
        },
        category_orders={
            "country": list(top_countries),  # Sorts bars from highest total to lowest
            "medal_type": ["Gold Medal", "Silver Medal", "Bronze Medal"],
        },
        color_discrete_map={
            "Gold Medal": "#FFD700",
            "Silver Medal": "#C0C0C0",
            "Bronze Medal": "#CD7F32",
        },
    )

    fig_bar.update_layout(height=550, xaxis_tickangle=-30)
    st.plotly_chart(fig_bar, width="stretch")