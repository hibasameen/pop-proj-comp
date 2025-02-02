import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load data
@st.cache_data
def load_data():
    # Replace with the correct file path
    df = pd.read_csv("data/population_difference_2018_vs_2022.csv")
    return df

df = load_data()

# Sidebar for user input
st.sidebar.title("Population Pyramid Visualizer")
sex = st.sidebar.selectbox("Select Sex", ["Males and Females (Combined)", "Persons"])
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
@st.cache_data
def filter_data(df, sex, variable):
    col_name = variable_mapping[variable]
    if sex == "Persons":
        df_filtered = df[df["Sex"] == "persons"][["Year", "Age", col_name]].copy()
        df_filtered.rename(columns={col_name: "Value"}, inplace=True)
    else:
        df_male = df[df["Sex"] == "male"][["Year", "Age", col_name]].copy()
        df_female = df[df["Sex"] == "female"][["Year", "Age", col_name]].copy()
        df_male["Value"] = -df_male[col_name]  # Negative for males
        df_female["Value"] = df_female[col_name]  # Positive for females
        df_filtered = pd.concat([df_male, df_female], ignore_index=True)
    return df_filtered

df_filtered = filter_data(df, sex, variable)

# Get a list of unique years
years = sorted(df_filtered["Year"].unique())
age_groups = sorted(df_filtered["Age"].unique(), reverse=True)  # Ensure descending order

# Add a slider for selecting the year
selected_year = st.slider("Select Year", min_value=min(years), max_value=max(years), value=min(years))

# Filter data for the selected year
df_selected_year = df_filtered[df_filtered["Year"] == selected_year]

# Create a population pyramid for the selected year
def plot_population_pyramid(df, variable, year):
    fig = go.Figure()

    # Add males
    fig.add_trace(
        go.Bar(
            x=df[df["Value"] < 0]["Value"],
            y=df[df["Value"] < 0]["Age"],
            orientation="h",
            name="Males",
            marker=dict(color="blue"),
        )
    )

    # Add females
    fig.add_trace(
        go.Bar(
            x=df[df["Value"] > 0]["Value"],
            y=df[df["Value"] > 0]["Age"],
            orientation="h",
            name="Females",
            marker=dict(color="red"),
        )
    )

    # Update layout to display all age groups
    fig.update_layout(
        title=f"{variable} - Year {year}",
        barmode="overlay",
        xaxis=dict(title=variable),
        yaxis=dict(
            title="Age Group",
            categoryorder="array",
            categoryarray=age_groups,  # Use the full list of age groups
            tickmode="array",
            tickvals=age_groups,  # Show all age groups
        ),
    )

    return fig

# Display the population pyramid for the selected year
st.title("Population Pyramid Visualization")
st.write(f"Visualizing: **{variable}** for **{sex}** in **{selected_year}**")
fig = plot_population_pyramid(df_selected_year, variable, selected_year)
st.plotly_chart(fig)
