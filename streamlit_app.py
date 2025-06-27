import streamlit as st

import pandas as pd
import altair as alt

# Read in dataset and drop rows w/missing values
df = pd.read_csv("listings.csv")
df["price_num"] = df["price"].replace(r"[\$,]", "", regex=True).astype(float)
df.dropna(subset=["price_num", "review_scores_rating", "beds"], inplace=True)

st.title("Data Dashboard for Boston Airbnb Listings")

st.subheader("Rating vs. Price/Number of Beds Scatterplot")

measure_options = {
    "Price": "price_num",
    "Number of Beds": "beds"
}
selected_measure = st.selectbox("Select Measure: ", list(measure_options.keys()))
x_field = measure_options[selected_measure]

scatter = alt.Chart(df).mark_circle().encode(
    x=alt.X(f"{x_field}:Q", title=selected_measure),
    y=alt.Y("review_scores_rating:Q", title="Rating"),
    tooltip=["neighbourhood_cleansed:N", "price_num:Q", "review_scores_rating:Q"]
).interactive()

st.altair_chart(scatter, use_container_width=True)

st.subheader("Rating Distribution by Neighborhood")

df.dropna(subset=["neighbourhood_cleansed"], inplace=True)
df_subset = df.query("review_scores_rating >= 3")

box = alt.Chart(df_subset).mark_boxplot().encode(
    x=alt.X("neighbourhood_cleansed:N",title="Neighborhood"),
    y=alt.Y("review_scores_rating:Q", title="Rating", scale=alt.Scale(domain=[3, 5])),
    tooltip=["neighbourhood_cleansed", "review_scores_rating"]
).properties(width=450)

st.altair_chart(box, use_container_width=True)

st.subheader("Neighborhood Median Price + Rating")

df_median = df.groupby("neighbourhood_cleansed", as_index=False)["price_num"].median().rename(columns={"price_num": "median_price"})

selection = alt.selection_point(
    fields=["neighbourhood_cleansed"],
    bind="legend",
    on="click",
    toggle=True
)
zoom = alt.selection_interval(bind='scales')

bar = alt.Chart(df_median).mark_bar().encode(
    x=alt.X("median_price:Q", title="Median Price"),
    y=alt.Y("neighbourhood_cleansed:N", sort="-x", title="Neighborhood"),
    color=alt.condition(selection, alt.value("steelblue"), alt.value("lightgray")),
    tooltip=["neighbourhood_cleansed:N", "median_price:Q"]
).add_params(selection)

overall_median = df["price_num"].median()
df_overall = pd.DataFrame({"overall_median": [overall_median]})

median_line = alt.Chart(df_overall).mark_rule(color="red").encode(x="overall_median:Q")

# st.altair_chart(bar + median_line, use_container_width=True)

scatter2 = alt.Chart(df).mark_circle().encode(
    x=alt.X("price_num:Q", title="Price"),
    y=alt.Y("review_scores_rating:Q", title="Rating"),
    color=alt.condition(selection, alt.value("steelblue"), alt.value("lightgray")),
    tooltip=["neighbourhood_cleansed:N", "price_num:Q", "review_scores_rating:Q"]
).transform_filter(selection).add_params(selection, zoom)

st.altair_chart((bar + median_line) & scatter2, use_container_width=True)