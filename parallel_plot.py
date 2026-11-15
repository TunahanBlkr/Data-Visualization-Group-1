import pandas as pd
import streamlit as st
import plotly.graph_objects as go

def _medal_counts(sub):
    return (
        (sub["medal_type"] == "Gold Medal").sum(),
        (sub["medal_type"] == "Silver Medal").sum(),
        (sub["medal_type"] == "Bronze Medal").sum(),
    )

@st.dialog("Node Details & Full Medal List", width="large")
def _show_node_details_dialog(axis_label, category_val, node_df):
    g, s, b = _medal_counts(node_df)
    st.markdown(f"### {axis_label}: `{category_val}`")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Medals", len(node_df))
    c2.metric("Gold", g)
    c3.metric("Silver", s)
    c4.metric("Bronze", b)
    st.divider()

    f1, f2, f3 = st.columns([2, 1.5, 1.5])
    query = f1.text_input("Search Athlete or Discipline:", placeholder="Type a name or sport...")
    medals = f2.multiselect(
        "Filter by Medal:",
        ["Gold Medal", "Silver Medal", "Bronze Medal"],
        default=["Gold Medal", "Silver Medal", "Bronze Medal"]
    )
    countries = sorted(node_df["country_code"].unique())
    selected_c = f3.multiselect("Filter by Country:", countries, default=countries)

    filtered = node_df[node_df["medal_type"].isin(medals) & node_df["country_code"].isin(selected_c)]
    if query.strip():
        q = query.strip().lower()
        filtered = filtered[
            filtered["name"].str.lower().str.contains(q) |
            filtered["discipline"].str.lower().str.contains(q)
        ]

    display_df = (
        filtered.sort_values(["medal_day", "name"])
        [["name", "country_code", "gender_short", "medal_day", "discipline", "medal_type", "event_type"]]
        .rename(columns={
            "name": "Athlete Name", "country_code": "Country", "gender_short": "Gender",
            "medal_day": "Day", "discipline": "Discipline", "medal_type": "Medal", "event_type": "Event Type"
        })
    )
    st.caption(f"Showing **{len(display_df)}** of **{len(node_df)}** records")
    st.dataframe(display_df, width="stretch", hide_index=True, height=380)


def _build_hover(col_name, label, val, sub):
    g, s, b = _medal_counts(sub)
    lines = [
        f"• <b>{r['name']}</b> ({r['country_code']}, {r['gender_short']}) | {r['medal_day']} | {r['discipline']} | <b>{r['medal_type']}</b> ({r['event_type']})"
        for _, r in sub.sort_values(["medal_day", "name"]).head(15).iterrows()
    ]
    if len(sub) > 15:
        lines.append(f"<i>... and {len(sub) - 15} more (Click node for full list)</i>")
    extra = f" ({sub.iloc[0]['country_code']}, {sub.iloc[0]['gender_short']})" if col_name == "name" else ""
    return (
        f"<b>{label}: {val}{extra}</b><br>"
        f"Gold: {g} | Silver: {s} | Bronze: {b} (Total: {len(sub)})<br>"
        f"──────────────────────────────<br>" + "<br>".join(lines)
    )


def show_parallel_plot(df):
    st.subheader("Top 5 Medallists Flow by Country (Interactive Parallel Coordinates)")

    if "chart_reset_key" not in st.session_state:
        st.session_state.chart_reset_key = 0

    req_cols = ["name", "country", "country_code", "medal_type", "discipline", "event_type", "gender", "medal_date"]
    par_df = df.dropna(subset=req_cols).copy()
    par_df["medal_day"] = par_df["medal_date"].dt.strftime("%Y-%m-%d")
    par_df["gender_short"] = par_df["gender"].map({"Female": "F", "Male": "M"}).fillna(par_df["gender"])

    all_countries = sorted(par_df["country"].unique())
    default_c = [c for c in ["United States", "France", "Spain"] if c in all_countries] or all_countries[:3]
    selected_countries = st.multiselect(
        "Select Countries (Top 5 medallists per country):",
        all_countries,
        default=default_c
    )

    if not selected_countries:
        st.warning("Please select at least one country to display the plot.")
        return

    filtered_par = par_df[par_df["country"].isin(selected_countries)]
    final_par_df = pd.concat([
        grp[grp["name"].isin(grp["name"].value_counts().head(5).index)]
        for _, grp in filtered_par.groupby("country")
    ], ignore_index=True)

    dims = ["name", "medal_day", "discipline", "medal_type", "event_type", "gender", "country_code"]
    titles = ["Athlete Name", "Day", "Discipline", "Medal", "Event Type", "Gender", "Country Code"]
    col_to_label = dict(zip(dims, titles))

    col_mappings = {}
    for col in dims:
        if col == "medal_type":
            vals = [m for m in ["Bronze Medal", "Silver Medal", "Gold Medal"] if m in final_par_df[col].unique()]
        else:
            vals = sorted(final_par_df[col].unique(), reverse=(col == "name"))
        n = len(vals)
        col_mappings[col] = {v: (0.5 if n == 1 else i / (n - 1)) for i, v in enumerate(vals)}

    fig_par = go.Figure()

    for i in range(len(dims)):
        fig_par.add_shape(
            type="line", x0=i, y0=-0.03, x1=i, y1=1.03,
            line=dict(color="rgba(150,150,150,0.5)", width=1.5), layer="below"
        )

    for athlete, grp in final_par_df.groupby("name", sort=False):
        hover = _build_hover("name", "Athlete", athlete, grp)
        xs, ys, texts = [], [], []
        for _, r in grp.iterrows():
            xs.extend(list(range(len(dims))) + [None])
            ys.extend([col_mappings[c][r[c]] for c in dims] + [None])
            texts.extend([hover] * len(dims) + [""])

        fig_par.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines",
            line=dict(color="rgba(255, 234, 0, 0.65)", width=2.5),
            text=texts, hovertemplate="%{text}<extra></extra>", showlegend=False
        ))

    for idx, (col, label) in enumerate(zip(dims, titles)):
        mapping = col_mappings[col]
        vals = list(mapping.keys())
        cdata = [[_build_hover(col, label, v, final_par_df[final_par_df[col] == v]), col, v] for v in vals]

        fig_par.add_trace(go.Scatter(
            x=[idx] * len(vals),
            y=list(mapping.values()),
            mode="markers+text",
            text=vals,
            textposition="middle left" if col == "name" else "middle right",
            textfont=dict(size=11.5),
            marker=dict(size=9, color="#FFEA00" if col == "name" else "#FFFFFF", line=dict(width=1.5, color="#333333")),
            unselected=dict(marker=dict(opacity=1.0), textfont=dict(color="rgba(235,235,235,1.0)")),
            customdata=cdata,
            hovertemplate="%{customdata[0]}<extra></extra>",
            showlegend=False
        ))

    fig_par.update_layout(
        title="Top 5 Medallists per Selected Country (Hover for Summary, Click Node for Details)",
        height=720,
        hovermode="closest",
        clickmode="event+select",
        showlegend=False,
        xaxis=dict(
            tickmode="array", tickvals=list(range(len(dims))), ticktext=titles,
            side="top", range=[-1.15, len(dims) - 0.15], showgrid=False, zeroline=False
        ),
        yaxis=dict(range=[-0.06, 1.06], showticklabels=False, showgrid=False, zeroline=False),
        margin=dict(l=40, r=40, t=90, b=30)
    )

    event = st.plotly_chart(
        fig_par,
        width="stretch",
        on_select="rerun",
        selection_mode="points",
        key=f"parcoords_chart_{st.session_state.chart_reset_key}"
    )

    pts = event.get("selection", {}).get("points", []) if event else []
    if pts and isinstance(pts[0].get("customdata"), list) and len(pts[0]["customdata"]) == 3:
        c_col, c_val = pts[0]["customdata"][1], pts[0]["customdata"][2]
        st.session_state.chart_reset_key += 1
        _show_node_details_dialog(col_to_label[c_col], c_val, final_par_df[final_par_df[c_col] == c_val])