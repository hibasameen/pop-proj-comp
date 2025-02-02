import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
start_year, end_year = st.sidebar.select_slider(
    "Select Time Period",
    options=range(2022, 2061),
    value=(2022, 2060)
)
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
def filter_data(df, sex, start_year, end_year):
    df_filtered = df[(df["Sex"] == sex.lower()) & (df["Year"].between(start_year, end_year))]
    return df_filtered

df_filtered = filter_data(df, sex, start_year, end_year)

# Plot population pyramid
def plot_pyramid(df, year, variable):
    df_year = df[df["Year"] == year].set_index("Age")
    col_name = variable_mapping[variable]  # Map user-friendly name to dataset column name
    if col_name not in df_year.columns:
        st.error(f"Column '{col_name}' not found in dataset.")
        return None
    values = df_year[col_name]
    colors = ["blue" if v >= 0 else "red" for v in values]
    fig, ax = plt.subplots(figsize=(8, 10))
    ax.barh(df_year.index, values, color=colors)
    ax.set_xlabel(variable)
    ax.set_title(f"{variable} - {year}")
    plt.gca().invert_yaxis()
    return fig

# Display title and description
st.title("Population Pyramid Visualization")
st.write(f"Visualizing: **{variable}** for **{sex}** from **{start_year}** to **{end_year}**")

# Generate and display plots for each year
for year in range(start_year, end_year + 1):
    st.write(f"### Year: {year}")
    st.pyplot(plot_pyramid(df_filtered, year, variable))
