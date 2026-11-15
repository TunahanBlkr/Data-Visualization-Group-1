import plotly.graph_objects as go
import streamlit as st

def show_sankey_plot(df):
    st.subheader(
        "Medal Flow: Gender ➔ Event Type ➔ Medal Type (Sankey Diagram)"
    )

    # Cleaning data for Sankey
    sankey_df = df.dropna(
        subset=["gender", "event_type", "medal_type", "country"]
    ).copy()

    # Make event_type codes more readable (ATH -> Individual, TEAM -> Team)
    sankey_df["event_category"] = sankey_df["event_type"].apply(
        lambda x: (
            "Individual Event" if x in ["ATH", "HATH"] else "Team / Group Event"
        )
    )

    # Country Selection (Empty = All Countries)
    all_countries = sorted(sankey_df["country"].unique())
    selected_countries = st.multiselect(
        "Filter by Country (Leave empty to see All Countries):",
        options=all_countries,
        default=[],
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
    genders = [
        g for g in ["Male", "Female"] if g in sankey_df["gender"].unique()
    ]
    events = [
        e
        for e in ["Individual Event", "Team / Group Event"]
        if e in sankey_df["event_category"].unique()
    ]
    medals = ["Gold Medal", "Silver Medal", "Bronze Medal"]

    labels = genders + events + medals
    label_map = {label: i for i, label in enumerate(labels)}

    # Step 1 Links: Gender -> Event Category
    link1 = (
        sankey_df.groupby(["gender", "event_category"])
        .size()
        .reset_index(name="count")
    )
    # Step 2 Links: Event Category -> Medal Type
    link2 = (
        sankey_df.groupby(["event_category", "medal_type"])
        .size()
        .reset_index(name="count")
    )

    sources = [label_map[x] for x in link1["gender"]] + [
        label_map[x] for x in link2["event_category"]
    ]
    targets = [label_map[x] for x in link1["event_category"]] + [
        label_map[x] for x in link2["medal_type"]
    ]
    values = list(link1["count"]) + list(link2["count"])

    # Plot Sankey Diagram
    fig_sankey = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=25,
                    thickness=25,
                    line=dict(color="black", width=0.5),
                    label=labels,
                    color=[color_map[l] for l in labels],
                ),
                link=dict(source=sources, target=targets, value=values),
            )
        ]
    )

    fig_sankey.update_layout(
        title_text="Flow of Medals from Gender to Event Category and Medal Type",
        height=550,
    )
    st.plotly_chart(fig_sankey, width="stretch")