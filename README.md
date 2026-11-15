# Summary, Context and Source of The Dataset

This study uses Petro Ivaniuk’s Paris 2024 Olympic `medallists.csv` dataset (2,315 records, 21 columns), covering
all medal-winning athletes and teams. Key attributes (e.g., name, gender, medal_type, discipline, medal_date,
birth_date, country) span demographic, geographic, and achievement-related values stored as strings, booleans,
dates, and integers. Redundant and non-analytical columns were removed to support exploratory visualization.

If you would like to explore the dataset in more detail, you can access the source via this link: https://www.kaggle.com/datasets/piterfm/paris-2024-olympic-summer-games?select=medallists.csv

The `country_clusters.csv` file was derived from the medallists.csv file by İsmail Kaya Yerlikaya. Visualization techniques Mekko Chart, PCA Scatter Plot and Cluster Maps utilize this file.

# Visualization Techniques

In this project, we employed nine visualization techniques (three per team member), as detailed below:

**Violin Plot:** Visualizes the probability density and age distribution of medalists across various disciplines, split
by gender

**Sankey Diagram:** Maps the proportional flow of medals from athlete gender through event categories to
medal tiers

**Stacked Bar Chart:** While ranking the countries that have won the most medals based on their total medal
count, it also displays the medal breakdown for each country in detail.

**Parallel Coordinates Plot:** It maps the medal achievements of the 5 most successful athletes from each
country and enables the creation of a detailed database that can be accessed by clicking on the nodes.

**Polar Area Chart:** When comparing the total number of medals across disciplines, it breaks them down into
categories: Gold, Silver and Bronze.

**Heatmap:** Tracks daily medal counts across countries. Featuring interactive filters by sports discipline and
medal type

**Mekko Chart (K-Means):** Shows the medal profile of each country cluster that K-Means found. Each bar is
one cluster, and the width of the bar shows the number of medals of the cluster. The colored segments show
the share of each sport family in the medals of the cluster.

**PCA Scatter Plot (K-Means):** Shows how similar the medal profiles of the countries are. PCA changes the 11
sport-family shares of each country into 2 numbers, so countries that are near each other won their medals in
similar sport families.

**Cluster Maps (Decision Tree):** Shows where the countries of each K-Means cluster are in the world, with one
small map for each cluster. A decision tree learns simple rules for the clusters, such as "Combat share >
64.3% → Combat focused", and shows its training and leave-one-out accuracy.

# Team Contributions

**Hasan Üstünsay:** Implementation of Violin Plot, Sankey Diagram and Stacked Bar Chart. Streamlit
dashboard architecture. Data cleaning and preprocessing.

**Tunahan Belikara:** Implementation of Parallel Coordinates Plot, Polar Area Chart and Heatmap. Github
repository documentation (README.md). Code editing

**İsmail Kaya Yerlikaya:** Implementation of Mekko Chart, PCA Scatter Plot and Cluster Maps. Machine
learning modeling (K-Means Clustering & Decision Tree). Report writing


# Project Setup and Run Guide

Follow the instructions below according to your operating system to set up the environment and run the application.

## Prerequisites

- Python 3.8 or higher installed on your system.

## For Windows Users

```
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\activate
pip install streamlit
pip install streamlit pandas
pip install streamlit plotly
pip install scikit-learn
streamlit run app.py
```
If your download speed is slow, you can use this instead of `pip install <library>`:

```
pip install streamlit -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install streamlit pandas -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install streamlit plotly -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install scikit-learn -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## For macOS/Linux Users

```
python3 -m venv venv
source venv/bin/activate
pip install streamlit
pip install streamlit pandas
pip install streamlit plotly
pip install scikit-learn
streamlit run app.py
```
If your download speed is slow, you can use this instead of `pip install <library>`:

```
pip install streamlit -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install streamlit pandas -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install streamlit plotly -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install scikit-learn -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## Deactivating the Virtual Environment

When you are finished working, you can deactivate the environment on any operating system by pressing `CTRL+C` or by closing the web page.