import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache
def load_data():
    # Replace with the correct file path
    df = pd.read_csv("path/to/population_difference_2018_vs_2022.csv")
    return df

df = load_data()

# Sidebar for user input
st.sidebar.title("Population Pyramid Visualizer")
sex = st.sidebar.selectbox("Select Sex", ["Males", "Females", "Persons"])
variable = st.sidebar.selectbox(
    "Select Variable",
    [
        "Population (2018 Projections)",
        "Population (2022 Projections)",
        "Population Difference",
        "Percentage Difference",
    ]
)

# Map user-friendly variable names to dataset column names
variable_mapping = {
    "Population (2018 Projections)": "Population_2018",
    "Population (2022 Projections)": "Population_2022",
    "Population Difference": "Population_Difference",
    "Percentage Difference": "Percentage_Change"
}

# Filter data based on user input
@st.cache
def filter_data(df, sex, variable):
    col_name = variable_mapping[variable]
    df_filtered = df[df["Sex"] == sex.lower()][["Year", "Age", col_name]].copy()
    df_filtered.rename(columns={col_name: "Value"}, inplace=True)
    return df_filtered

df_filtered = filter_data(df, sex, variable)

# Create an animated population pyramid
def plot_animated_pyramid(df, variable):
    fig = px.bar(
        df,
        x="Value",
        y="Age",
        color="Value",
        animation_frame="Year",
        orientation="h",
        title=f"{variable} Over Time",
        labels={"Value": variable, "Age": "Age Group"},
        color_continuous_scale=["red", "blue"],  # Red for negative, blue for positive
    )
    fig.update_layout(
        xaxis=dict(title=variable),
        yaxis=dict(title="Age Group", categoryorder="total ascending"),
        coloraxis_showscale=False,
    )
    return fig

# Display the interactive animation
st.title("Interactive Animated Population Pyramid")
st.write(f"Visualizing: **{variable}** for **{sex}**")
fig = plot_animated_pyramid(df_filtered, variable)
st.plotly_chart(fig)
