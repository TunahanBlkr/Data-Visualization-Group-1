"""
#cluster countries resemble winning medals at alike sport categories")
#will use k-means ml algorithm bases on oclid formula, which represents distances between two points")
#d(A,B) = sqrt((a1-b1)^2 + (a2-b2)^2 + ...)")
#ml algo will calculate distances between a country and k clusters and cluster countries whose distances are lower than their distances to other clusters")
#main aim of this ml is to show resembles between countries by showing their successes at sport areas
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

df = pd.read_csv("medallists.csv",  usecols=["country", "discipline", "event", "medal_type"])

#########################
#ARE THERE NA
print(df.isna().sum())   
# missing values per column 0 for each column

#######################
#STRIP TEXT PROBLEMS
#first of all we should clean the dataset to overcome ml errors
for col in ["country", "discipline", "event", "medal_type"]:
   df[col] = df[col].str.strip()
print(df["medal_type"].unique())
print(df["country"].unique())
#AIN bireysel tarafsız sporcular
#EOR mülteci olimpiyat takımı
print(df["event"].unique())
print(df["discipline"].unique())
key = ["country", "discipline", "event", "medal_type"]
cnt = df.groupby(key).size()
print(cnt[cnt > 1].sort_values(ascending=False))

########################
#DROP DUPLICATED AND TEAM MEMBER ISSUED DATA
#how many duplicated "same" rows are there
print(df.duplicated().sum())
#drop team medals counted more than one. eg: for basketball it's written 12 but for one country it must be written 1.
df = df.drop_duplicates(subset=["country", "discipline", "event", "medal_type"])
#control team member medal confusion
per_event = df.groupby(["discipline", "event", "medal_type"]).size().unstack(fill_value=0)
bad = per_event[(per_event["Gold Medal"] != 1)
                | (per_event["Silver Medal"] != 1)
                | (~per_event["Bronze Medal"].isin([1, 2]))]
print(len(per_event), "events")
print("control after team member medal elimination\n", bad)
#Swimming   Men's 100m Breaststroke             0           1             2
    #for this event there was a tie and 2 got 2 silver medals
print(cnt[cnt > 1].reset_index()["event"].unique())

###################
#there are too many categories and many countries. if we try to ensure resemblence between
#too many elements of country vectors make our resemblence job harder
#so we need to cummulate some sports under same categories
family = {
    "Swimming": "Aquatics", "Marathon Swimming": "Aquatics", "Diving": "Aquatics",
    "Artistic Swimming": "Aquatics", "Water Polo": "Aquatics",
    "Athletics": "Athletics",
    "Boxing": "Combat", "Judo": "Combat", "Taekwondo": "Combat",
    "Wrestling": "Combat", "Fencing": "Combat",
    "Basketball": "Team ball", "3x3 Basketball": "Team ball", "Football": "Team ball",
    "Handball": "Team ball", "Hockey": "Team ball", "Rugby Sevens": "Team ball",
    "Volleyball": "Team ball", "Beach Volleyball": "Team ball",
    "Badminton": "Racket", "Table Tennis": "Racket", "Tennis": "Racket",
    "Cycling BMX Freestyle": "Cycling", "Cycling BMX Racing": "Cycling",
    "Cycling Mountain Bike": "Cycling", "Cycling Road": "Cycling", "Cycling Track": "Cycling",
    "Artistic Gymnastics": "Gymnastics", "Rhythmic Gymnastics": "Gymnastics",
    "Trampoline Gymnastics": "Gymnastics",
    "Rowing": "Water craft", "Sailing": "Water craft", "Canoe Slalom": "Water craft",
    "Canoe Sprint": "Water craft", "Surfing": "Water craft",
    "Archery": "Target", "Shooting": "Target", "Golf": "Target",
    "Weightlifting": "Weightlifting",
    "Breaking": "Other", "Skateboarding": "Other", "Sport Climbing": "Other",
    "Equestrian": "Other", "Modern Pentathlon": "Other", "Triathlon": "Other",
}
df["family"] = df["discipline"].map(family)   # family: a dictionary, discipline -> family
print(df["family"].isna().sum())               # must be 0

##########################
#TO LOOK RESEMBLANCE MAKE SUM OF MEDALS EQUAL TO 1
#we should also consider some countries wins much more medals than others, so we need to change medal numbers to individual ratios to all medals")
table = pd.crosstab(df["country"], df["family"])
#remove countries has less than 5 medals, not reliable for ml
#our threshold here is 5 because median of medal number per country is 5
table = table[table.sum(axis=1) >= 5]
#now sum of each row is 1 and all columns' sum makes 1
profile = table.div(table.sum(axis=1), axis=0)

########################################
#K-MEANS
#i want to show both silhoutte optimization result and inertia elbow result
best_silhouette = -1
best_k_silhouette = None
km_silhouette = None
inertias = {}
models = {}
for k in range(2, 10):
    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(profile)
        #n_init: start with 10 different starting clusters and chose the best resulting one
        #random_state: seed
        #fit runs algorithm on profile table
            #results
                #km.labels_	cluster number of all countries [2, 0, 1, 2, ...]
                #km.cluster_centers_ center of all clusters
                #km.inertia_ total of squares of distances between all countries and their cluster's center
                    #while k grows inertia gets smaller but you can't call take the smallest inertia because when you make k = 49, inertia becomes 0
                    #insted we need to look the elbow, the point where decreasing starts to slow down
    silhouette = silhouette_score(profile, km.labels_)
    inertias[k] = km.inertia_
    models[k] = km
    print(f"k={k}  inertia={km.inertia_:.2f}  silhouette={silhouette_score(profile, km.labels_):.2f}")
        #silhoutte
            # s = ((countries' mean distance to the countries at the cluster which is nearest to it's cluster) - (countries' mean distance to the countries at it's cluster)) / max(a, b)
            #to understand if the country is at true cluster. -1 0 1
            #silhoutte_score
                #mean of the silhouttes of all the countries
    if silhouette > best_silhouette:
        best_silhouette = silhouette
        best_k_silhouette = k
        km_silhouette = km
#####################################
#SAVE BEST K
print("best k (silhouette):", best_k_silhouette)
#find elbow of inertia curve
#change k and inertia to range 0-1 and they'll have same scales
#draw a line from first to last point
#elbow is the largest distance to this line
    #not only way to find the inertia
k_values = list(inertias.keys())
first_k = k_values[0]
last_k = k_values[-1]
highest_inertia = inertias[first_k]
lowest_inertia = inertias[last_k]
best_distance = -1
best_k_elbow = None
for k in k_values:
    x = (k - first_k) / (last_k - first_k)
    y = (inertias[k] - lowest_inertia) / (highest_inertia - lowest_inertia)
    distance = (1 - x - y) / (2 ** 0.5)   # distance from the point (x, y) to the line x + y = 1
    print(f"k={k}  x={x:.2f}  y={y:.2f}  distance={distance:.3f}")
    if distance > best_distance:
        best_distance = distance
        best_k_elbow = k
km_elbow = models[best_k_elbow]
print("best k (elbow):", best_k_elbow)
result = table.copy()
result["cluster_silhouette"] = km_silhouette.labels_
result["cluster_elbow"] = km_elbow.labels_
result.to_csv("country_clusters.csv")
"""
####################
#TURN TO MEKKO TABLE
"""result = pd.read_csv("country_clusters.csv", index_col="country")
# Use only the sport family columns. Do not add the cluster columns.
family_columns = result.columns.drop(["cluster_silhouette", "cluster_elbow"])
mekko_elbow = result.groupby("cluster_elbow")[family_columns].sum()
mekko_silhouette = result.groupby("cluster_silhouette")[family_columns].sum()"""
#interactive
    #choose best k between elbow or silhoutte
# Mekko chart page: the medal profiles of the K-Means country clusters.
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.decomposition import PCA
from plotly.subplots import make_subplots
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.tree import DecisionTreeClassifier
# Categorical colors in a fixed order. These 8 colors pass the colorblind check.
COLORS_LIGHT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
COLORS_DARK = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"]
# Color of the percent labels in the segments: near-black on yellow (slot 4), white on the other colors.
LABEL_COLORS = ["#ffffff", "#ffffff", "#ffffff", "#0b0b0b", "#ffffff", "#ffffff", "#ffffff", "#ffffff"]

CLUSTER_COLUMNS = ["cluster_silhouette", "cluster_elbow"]
MAX_SEGMENTS = 8        # The palette has 8 colors. Put the smallest sport families into "Other".
FOCUS_SHARE = 0.6       # If one family has 60% or more of the medals of a cluster, call it "<family> focused".
MIN_LABEL_SHARE = 0.08  # Show a percent label only on a segment of 8% or more.


@st.cache_data
def load_clusters(path="country_clusters.csv"):
    return pd.read_csv(path, index_col="country")


def name_cluster(medals):
    # medals: the medal count of each sport family for one cluster.
    shares = (medals / medals.sum()).sort_values(ascending=False)
    if shares.iloc[0] >= FOCUS_SHARE:
        return f"{shares.index[0]} focused"
    return f"{shares.index[0]} + {shares.index[1]}"


def build_mekko(result, cluster_column, dark=False):
    family_columns = result.columns.drop(CLUSTER_COLUMNS)

    # 1. Medal counts: one row for each cluster, one column for each sport family.
    counts = result.groupby(cluster_column)[family_columns].sum()

    # 2. Give a name to each cluster. Use all 11 families, before the "Other" step.
    #    If two clusters get the same name, add the cluster number.
    names = counts.apply(name_cluster, axis=1)
    same = names.duplicated(keep=False)
    names[same] = names[same] + " (" + names.index[same].astype(str) + ")"

    # 3. Keep the 7 largest families. Put the remaining families into "Other".
    #    Use the totals of all the countries. Then each family keeps its color for the two K values.
    family_totals = result[family_columns].sum().sort_values(ascending=False)
    kept = [f for f in family_totals.index if f != "Other"][:MAX_SEGMENTS - 1]
    folded = [f for f in family_columns if f not in kept]
    shown = counts[kept].copy()
    shown["Other"] = counts[folded].sum(axis=1)
    order = kept + ["Other"]

    # 4. Put the largest cluster on the left.
    shown = shown.loc[shown.sum(axis=1).sort_values(ascending=False).index]
    widths = shown.sum(axis=1)             # bar width = number of medals of the cluster
    lefts = widths.cumsum() - widths       # left edge of each bar
    shares = shown.div(widths, axis=0)     # segment height = share of the family in the cluster
    countries = result[cluster_column].value_counts()

    # 5. Small empty spaces between the bars and between the segments.
    gap_x = widths.sum() * 0.004
    gap_y = 0.005

    # 6. Hover text for the "Other" segment: the families in it.
    other_detail = counts.loc[shown.index, folded].apply(
        lambda row: "<br>".join(f"{'Other sports' if f == 'Other' else f}: {v}"
                                for f, v in row.items() if v > 0), axis=1)

    colors = COLORS_DARK if dark else COLORS_LIGHT
    fig = go.Figure()
    bottom = pd.Series(0.0, index=shown.index)
    for i, family in enumerate(order):
        share = shares[family]
        detail = other_detail if family == "Other" else pd.Series("", index=shown.index)
        fig.add_bar(
            name=family,
            x=lefts + gap_x / 2,
            width=widths - gap_x,
            offset=0,
            base=bottom + gap_y / 2,
            y=(share - gap_y).clip(lower=0),
            marker_color=colors[i],
            text=[f"{s:.0%}" if s >= MIN_LABEL_SHARE else "" for s in share],
            textposition="inside",
            insidetextanchor="middle",
            textfont_color=LABEL_COLORS[i],
            customdata=list(zip(names[shown.index], countries[shown.index], shown[family], share, detail)),
            hovertemplate=(
                "<b>%{customdata[0]}</b> (%{customdata[1]} countries)<br>"
                + family + ": %{customdata[2]} medals (%{customdata[3]:.0%})<br>"
                + "%{customdata[4]}<extra></extra>"
            ),
        )
        bottom = bottom + share

    fig.update_layout(
        barmode="overlay",
        height=560,
        title="Which sport families bring the medals of each country cluster?",
        xaxis=dict(
            title="Clusters (bar width = number of medals)",
            tickvals=list(lefts + widths / 2),
            ticktext=list(names[shown.index]),
            tickangle=-45,
            range=[0, widths.sum()],
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(title="Share of the medals of the cluster", tickformat=".0%", range=[0, 1], dtick=0.25),
        legend=dict(title="Sport family", traceorder="reversed"),
        uniformtext=dict(minsize=10, mode="hide"),
        margin=dict(b=130),
    )
    return fig, names, counts, list(shown.index), folded


def show_mekko_page():
    st.subheader("Medal Profiles of Country Clusters (K-Means + Mekko Chart)")
    result = load_clusters()
    st.caption(
        f"K-Means put the {len(result)} countries that have 5 or more medals into clusters. "
        "It compared the share of the medals of each country in 11 sport families. "
        "Each bar is one cluster. The bar width shows the number of medals of the cluster. "
        "The segments show the share of each sport family."
    )

    cluster_column = choose_cluster_column()

    dark = st.context.theme.type == "dark"
    fig, names, counts, order, folded = build_mekko(result, cluster_column, dark)
    st.plotly_chart(fig)
    st.caption(
        f"K = {len(order)}. The palette has 8 colors, so 'Other' also contains: "
        + ", ".join(f for f in folded if f != "Other")
        + ". Move the pointer on a segment to see the details. Click a legend item to hide a family."
    )

    with st.expander("Show the data table"):
        members = result.reset_index().groupby(cluster_column)["country"].agg(", ".join)
        summary = pd.DataFrame({
            "Cluster": names[order],
            "Countries": result[cluster_column].value_counts()[order],
            "Medals": counts.loc[order].sum(axis=1),
            "Members": members[order],
        })
        st.dataframe(summary, hide_index=True)
        st.dataframe(counts.loc[order].set_axis(names[order], axis=0))
"""
Combat focused (69 medals): Türkiye, Azerbaycan, Gürcistan, İran, Kazakistan, Kırgızistan, Özbekistan, Küba. %90 of medals combat sports
Athletics focused (17 medals): Jamaika, Kenya, madalyaların %100 athletics medals
Combat + Aquatics (325 medals): Çin, Japonya, Fransa, Kore... Combat %32, Target (%11)....
Aquatics + Water craft (536 medals): ABD, Büyük Britanya, Avustralya, Hollanda...
"""
def build_cluster_map(result, cluster_column, names, counts, mekko_fig, dark=False):
    family_columns = result.columns.drop(CLUSTER_COLUMNS)
    profile = result[family_columns].div(result[family_columns].sum(axis=1), axis=0)

    # 1. PCA: change the 11 medal shares of each country into 2 numbers (x, y).
    #    K-Means used the same 11 shares. Countries that are near each other have similar profiles.
    pca = PCA(n_components=2)
    xy = pca.fit_transform(profile)

    # 2. On each axis, show the family with the most negative weight and the family with the most positive weight.
    def axis_title(i):
        weights = pd.Series(pca.components_[i], index=family_columns)
        explained = pca.explained_variance_ratio_[i]
        return f"PC{i + 1} ({explained:.0%} of the variance): {weights.idxmin()} ← → {weights.idxmax()}"

    points = pd.DataFrame({
        "x": xy[:, 0],
        "y": xy[:, 1],
        "cluster": result[cluster_column],
        "medals": result[family_columns].sum(axis=1),
        "top_family": profile.idxmax(axis=1),
        "top_share": profile.max(axis=1),
    }, index=result.index)

    # 3. Some countries have the same profile (for example 100% Combat). Their points are at the same place.
    #    Show them as one larger point. The hover shows all the country names.
    points["place"] = points["x"].round(6).astype(str) + "|" + points["y"].round(6).astype(str)
    groups = points.reset_index().groupby(["cluster", "place"]).agg(
        countries=("country", ", ".join),
        n=("country", "size"),
        medals=("medals", "sum"),
        x=("x", "first"),
        y=("y", "first"),
        top_family=("top_family", "first"),
        top_share=("top_share", "first"),
    ).reset_index()

    # 4. Point color = the main sport family of the cluster, with the same colors as the Mekko chart.
    #    Point shape: diamond = one family has 60% or more of the medals ("focused"), circle = mixed.
    family_color = {trace.name: trace.marker.color for trace in mekko_fig.data}
    main_family = counts.idxmax(axis=1)
    ring = "#0e1117" if dark else "#ffffff"
    label_background = "rgba(14, 17, 23, 0.75)" if dark else "rgba(255, 255, 255, 0.75)"

    fig = go.Figure()
    for cluster_id in names.index:
        name = names[cluster_id]
        group = groups[groups["cluster"] == cluster_id]
        fig.add_scatter(
            x=group["x"],
            y=group["y"],
            mode="markers",
            name=name,
            marker=dict(
                color=family_color.get(main_family[cluster_id], family_color["Other"]),
                symbol="diamond" if " focused" in name else "circle",
                size=10 + 3 * (group["n"] - 1),
                opacity=1,   # Plotly makes points with different sizes 70% transparent. Use full color.
                line=dict(width=1.5, color=ring),
            ),
            customdata=list(zip(group["countries"], group["medals"], group["top_family"], group["top_share"])),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                + "Cluster: " + name + "<br>"
                + "Medals: %{customdata[1]}<br>"
                + "Main sport family: %{customdata[2]} (%{customdata[3]:.0%})<extra></extra>"
            ),
        )
        # Write the cluster name near the center of its points.
        center = points.loc[points["cluster"] == cluster_id, ["x", "y"]].mean()
        fig.add_annotation(x=center["x"], y=center["y"], text=name, showarrow=False,
                           yshift=22, bgcolor=label_background, font=dict(size=12))

    fig.update_layout(
        height=560,
        title="Where is each country? A 2D map of the medal profiles (PCA)",
        xaxis=dict(title=axis_title(0), zeroline=False),
        yaxis=dict(title=axis_title(1), zeroline=False),
        legend=dict(title="Cluster"),
        hovermode="closest",
        hoverdistance=30,
    )
    return fig, points

def choose_cluster_column():
    # The Mekko page and the PCA page use this radio with the same key.
    # When you go to the other page, the choice of K stays the same.
    method = st.radio(
        "Choose the number of clusters (K) by:",
        ["Elbow of the inertia curve", "Highest silhouette score"],
        horizontal=True,
        key="k_method",
    )
    return "cluster_elbow" if method.startswith("Elbow") else "cluster_silhouette"

def show_scatter_plot():
    st.subheader("Countries by Medal Profile (PCA Scatter Plot of K-Means Clusters)")
    result = load_clusters()
    st.caption(
        f"Each point is one of the {len(result)} countries that have 5 or more medals. "
        "PCA changed the 11 medal shares of each country into 2 numbers. "
        "Countries that are near each other won their medals in similar sport families."
    )
    cluster_column = choose_cluster_column()
    dark = st.context.theme.type == "dark"

    # The scatter plot uses the cluster names and the family colors of the Mekko chart.
    # Make the Mekko data first, but do not show the Mekko chart on this page.
    mekko_fig, names, counts, order, folded = build_mekko(result, cluster_column, dark)
    fig, points = build_cluster_map(result, cluster_column, names[order], counts, mekko_fig, dark)
    st.plotly_chart(fig)
    st.caption(
        f"K = {len(order)}. Color = the main sport family of the cluster (the same colors as the Mekko chart). "
        "Shape: diamond = one family has 60% or more of the medals, circle = mixed. "
        "A larger point = more than one country with the same profile."
    )

    with st.expander("Show the data table"):
        table = pd.DataFrame({
            "Cluster": points["cluster"].map(names),
            "Medals": points["medals"],
            "Main sport family": points["top_family"],
            "Share of the main family": points["top_share"].map("{:.0%}".format),
            "PC1": points["x"].round(2),
            "PC2": points["y"].round(2),
        })
        st.dataframe(table.sort_values(["Cluster", "Medals"], ascending=[True, False]))

# Olympic (IOC) country codes that are not the same as the ISO-3 codes of the Plotly map.
# Example: IOC "BRN" is Bahrain, but ISO "BRN" is Brunei.
IOC_TO_ISO = {
    "ALG": "DZA", "BOT": "BWA", "BRN": "BHR", "BUL": "BGR", "CHI": "CHL", "CRO": "HRV",
    "DEN": "DNK", "FIJ": "FJI", "GER": "DEU", "GRE": "GRC", "GRN": "GRD", "GUA": "GTM",
    "INA": "IDN", "IRI": "IRN", "KOS": "XKX", "MAS": "MYS", "MGL": "MNG", "NED": "NLD",
    "PHI": "PHL", "POR": "PRT", "PUR": "PRI", "RSA": "ZAF", "SLO": "SVN", "SUI": "CHE",
    "TPE": "TWN", "ZAM": "ZMB",
}
NOT_COUNTRIES = ["AIN", "EOR"]   # These teams have no country on the map.


@st.cache_data
def load_medal_countries(path="medallists.csv"):
    # One row for each country that won a medal: the ISO code and the number of medals.
    df = pd.read_csv(path, usecols=["country", "country_code", "discipline", "event", "medal_type"])
    df = df.drop_duplicates(subset=["country", "discipline", "event", "medal_type"])
    df = df[~df["country_code"].isin(NOT_COUNTRIES)]
    medals = df.groupby(["country", "country_code"]).size().reset_index(name="medals")
    medals["iso_code"] = medals["country_code"].replace(IOC_TO_ISO)
    return medals.set_index("country")


def fit_tree(profile, labels, names, depth):
    # Decision Tree (classification): learn simple if-then rules that give the K-Means cluster of a country.
    tree = DecisionTreeClassifier(max_depth=depth, random_state=0).fit(profile, labels)
    train_accuracy = tree.score(profile, labels)

    # Leave-one-out test: train without one country, then predict that country. Do this for each country.
    test_accuracy = cross_val_score(DecisionTreeClassifier(max_depth=depth, random_state=0),
                                    profile, labels, cv=LeaveOneOut()).mean()

    # Write the rule of each country: the tests on its path from the top of the tree to a leaf.
    # If the path tests the same family two times, keep only the tightest lower and upper limits.
    path = tree.decision_path(profile)
    rules = []
    for row in range(len(profile)):
        nodes = path.indices[path.indptr[row]:path.indptr[row + 1]]
        lower, upper, families = {}, {}, []
        for node in nodes[:-1]:   # The last node is the leaf. A leaf has no test.
            family = profile.columns[tree.tree_.feature[node]]
            limit = tree.tree_.threshold[node]
            if family not in families:
                families.append(family)
            if profile.iloc[row][family] <= limit:
                upper[family] = min(limit, upper.get(family, 1.0))
            else:
                lower[family] = max(limit, lower.get(family, 0.0))
        tests = []
        for family in families:
            if family in lower and family in upper:
                tests.append(f"{lower[family]:.1%} < {family} ≤ {upper[family]:.1%}")
            elif family in lower:
                tests.append(f"{family} > {lower[family]:.1%}")
            else:
                tests.append(f"{family} ≤ {upper[family]:.1%}")
        rules.append(" and ".join(tests) if tests else "(all countries)")

    rules = pd.Series(rules, index=profile.index)
    predicted = pd.Series(tree.predict(profile), index=profile.index).map(names)
    return rules, predicted, train_accuracy, test_accuracy


def build_cluster_maps(medal_countries, cluster_of, names, counts, mekko_fig, rules, predicted, dark=False):
    # Small multiples: one world map for each cluster. The countries of the cluster are in color.
    # One map with K colors is not possible: past 3 colors, some pairs are too similar for colorblind people.
    family_color = {trace.name: trace.marker.color for trace in mekko_fig.data}
    main_family = counts.idxmax(axis=1)
    gray = "#5c5b57" if dark else "#c3c2b7"      # the other countries that won medals
    land = "#22252c" if dark else "#f0efec"      # the countries without medals
    border = "#0e1117" if dark else "#ffffff"

    data = medal_countries.copy()
    data["cluster"] = cluster_of.reindex(data.index)   # empty = fewer than 5 medals
    data["cluster_name"] = data["cluster"].map(names).fillna("Not clustered (fewer than 5 medals)")
    data["rule"] = rules.reindex(data.index).fillna("-")
    data["predicted"] = predicted.reindex(data.index).fillna("-")

    n_maps = len(names)
    n_cols = 2
    n_rows = -(-n_maps // n_cols)   # round up
    specs = [[{"type": "choropleth"} if r * n_cols + c < n_maps else None for c in range(n_cols)]
             for r in range(n_rows)]
    titles = [f"{names[c]} ({(data['cluster'] == c).sum()} countries)" for c in names.index]
    fig = make_subplots(rows=n_rows, cols=n_cols, specs=specs, subplot_titles=titles,
                        vertical_spacing=0.08, horizontal_spacing=0.02)

    for i, cluster_id in enumerate(names.index):
        inside = data["cluster"] == cluster_id
        color = family_color.get(main_family[cluster_id], family_color["Other"])
        for part, fill in [(data[~inside], gray), (data[inside], color)]:
            fig.add_choropleth(
                locations=part["iso_code"],
                locationmode="ISO-3",
                z=[1] * len(part),
                colorscale=[[0, fill], [1, fill]],
                showscale=False,
                marker_line_color=border,
                marker_line_width=0.5,
                customdata=list(zip(part.index, part["cluster_name"], part["medals"],
                                    part["rule"], part["predicted"])),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    + "K-Means cluster: %{customdata[1]}<br>"
                    + "Medals: %{customdata[2]}<br>"
                    + "Tree rule: %{customdata[3]}<br>"
                    + "Tree prediction: %{customdata[4]}<extra></extra>"
                ),
                row=i // n_cols + 1,
                col=i % n_cols + 1,
            )

    fig.update_geos(
        projection_type="natural earth",
        showframe=False,
        showcoastlines=False,
        showland=True,
        landcolor=land,
        showcountries=True,
        countrycolor=border,
        bgcolor="rgba(0,0,0,0)",
        lataxis_range=[-55, 80],
    )
    fig.update_layout(
        height=320 * n_rows + 60,
        title="Where are the countries of each K-Means cluster?",
        margin=dict(l=10, r=10, t=80, b=10),
    )
    return fig


def show_map_page():
    st.subheader("Where Are the Clusters? (Choropleth Maps + Decision Tree)")
    result = load_clusters()
    medal_countries = load_medal_countries()
    st.caption(
        "Each map shows the countries of one K-Means cluster in color. "
        "Gray = the other countries that won medals. "
        "A Decision Tree learns simple if-then rules that give the cluster of each country."
    )

    left, right = st.columns(2)
    with left:
        cluster_column = choose_cluster_column()
    with right:
        # Depth 4 has the best leave-one-out accuracy. A smaller depth gives simpler rules.
        depth = st.slider("Maximum depth of the decision tree", min_value=1, max_value=4, value=4)
    dark = st.context.theme.type == "dark"

    # Use the cluster names and the family colors of the Mekko chart.
    mekko_fig, names, counts, order, folded = build_mekko(result, cluster_column, dark)
    family_columns = result.columns.drop(CLUSTER_COLUMNS)
    profile = result[family_columns].div(result[family_columns].sum(axis=1), axis=0)
    rules, predicted, train_accuracy, test_accuracy = fit_tree(profile, result[cluster_column], names, depth)

    fig = build_cluster_maps(medal_countries, result[cluster_column], names[order], counts,
                             mekko_fig, rules, predicted, dark)
    st.plotly_chart(fig)
    st.caption("Move the pointer on a country to see its cluster, its number of medals and its tree rule. "
               "Use the mouse wheel to zoom and drag to move a map.")

    st.markdown("#### Decision Tree: if-then rules for the clusters")
    col1, col2 = st.columns(2)
    col1.metric("Training accuracy", f"{train_accuracy:.0%}",
                help="The share of the countries for which the tree gives the K-Means cluster.")
    col2.metric("Leave-one-out accuracy", f"{test_accuracy:.0%}",
                help="Train without one country, then predict it. Do this for each country.")

    table = pd.DataFrame({"rule": rules, "predicted": predicted, "cluster": result[cluster_column].map(names)})
    table["country"] = table.index
    table["correct"] = table["predicted"] == table["cluster"]
    leaves = table.groupby(["rule", "predicted"]).agg(
        countries=("country", "size"),
        correct=("correct", "sum"),
        members=("country", ", ".join),
    ).reset_index().sort_values("countries", ascending=False)
    leaves.columns = ["IF (rule)", "THEN (cluster)", "Countries", "Correct", "Members"]
    st.dataframe(leaves, hide_index=True)
