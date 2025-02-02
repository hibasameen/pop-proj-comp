import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/population_difference_2018_vs_2022.csv")
    return df

df = load_data()

# Standardize age group labels
df["Age"] = df["Age"].str.strip().str.lower().replace({"100 and over": "100&over"})

# Define the explicit order of age groups
age_group_order = [
    "0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34",
    "35-39", "40-44", "45-49", "50-54", "55-59", "60-64",
    "65-69", "70-74", "75-79", "80-84", "85-89", "90-94",
    "95-99", "100&over"
]

# Function to filter data based on user input
@st.cache_data
def filter_data(df, sex, variable, dataset=None):
    if dataset:  # For Population Projections
        col_name = f"Population_{dataset}"
    else:  # For Difference/Percentage Change
        col_name = variable

    if sex == "Persons":
        df_filtered = df[df["Sex"] == "persons"][["Year", "Age", col_name]].copy()
        df_filtered.rename(columns={col_name: "Value"}, inplace=True)
    else:
        df_male = df[df["Sex"] == "male"][["Year", "Age", col_name]].copy()
        df_female = df[df["Sex"] == "female"][["Year", "Age", col_name]].copy()
        df_male["Value"] = -df_male[col_name]  # Negative for males
        df_female["Value"] = df_female[col_name]  # Positive for females
        df_filtered = pd.concat([df_male, df_female], ignore_index=True)

    # Ensure all age groups are present for each year
    all_years = df_filtered["Year"].unique()
    filled_data = []
    for year in all_years:
        for age_group in age_group_order:
            if not ((df_filtered["Year"] == year) & (df_filtered["Age"] == age_group)).any():
                filled_data.append({"Year": year, "Age": age_group, "Value": 0})
    df_filled = pd.concat([df_filtered, pd.DataFrame(filled_data)], ignore_index=True)

    # Ensure proper sorting
    df_filled["Age"] = pd.Categorical(df_filled["Age"], categories=age_group_order, ordered=True)
    df_filled = df_filled.sort_values(["Year", "Age"]).reset_index(drop=True)

    return df_filled

# Function to calculate the dynamic x-axis range for Chart 2
def get_dynamic_x_axis_range(df):
    min_value = df["Value"].min()
    max_value = df["Value"].max()

    # Add some padding to the range for better visualization
    padding = (max_value - min_value) * 0.1
    return [min_value - padding, max_value + padding]

# Function to plot a population pyramid
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
            categoryarray=age_group_order,  # Explicit order of age groups
            tickmode="array",
            tickvals=age_group_order,  # Force all labels to display
        ),
    )

    return fig

# Function to plot a population pyramid with a dynamic x-axis for Chart 2
def plot_population_pyramid_dynamic(df, variable, year, sex):
    fig = go.Figure()

    # Dynamic labels for Persons
    label_decrease = "Decrease" if sex == "Persons" else "Males"
    label_increase = "Increase" if sex == "Persons" else "Females"

    # Add decrease (or males)
    fig.add_trace(
        go.Bar(
            x=df[df["Value"] < 0]["Value"],
            y=df[df["Value"] < 0]["Age"],
            orientation="h",
            name=label_decrease,
            marker=dict(color="blue"),
        )
    )

    # Add increase (or females)
    fig.add_trace(
        go.Bar(
            x=df[df["Value"] > 0]["Value"],
            y=df[df["Value"] > 0]["Age"],
            orientation="h",
            name=label_increase,
            marker=dict(color="red"),
        )
    )

    # Calculate dynamic x-axis range
    x_axis_range = get_dynamic_x_axis_range(df)

    # Update layout to display all age groups and use dynamic x-axis range
    fig.update_layout(
        title=f"{variable} - Year {year}",
        barmode="overlay",
        xaxis=dict(title=variable, range=x_axis_range),  # Dynamic x-axis range
        yaxis=dict(
            title="Age Group",
            categoryorder="array",
            categoryarray=age_group_order,  # Explicit order of age groups
            tickmode="array",
            tickvals=age_group_order,  # Force all labels to display
        ),
    )

    return fig

# --- Chart 1: Population Projections ---
st.title("Population Projections")
st.sidebar.subheader("Chart 1: Population Projections")

# Inputs for chart 1
dataset = st.sidebar.radio("Select Dataset", ["2018 Projections", "2022 Projections"])
sex_chart1 = st.sidebar.selectbox("Select Sex (Chart 1)", ["Males and Females (Combined)", "Persons"])
years_chart1 = sorted(df["Year"].unique())
selected_year_chart1 = st.slider("Select Year (Chart 1)", min_value=min(years_chart1), max_value=max(years_chart1))

# Filter and display chart 1
df_chart1 = filter_data(df, sex_chart1, None, dataset=dataset.split()[0])
df_selected_year_chart1 = df_chart1[df_chart1["Year"] == selected_year_chart1]
fig_chart1 = plot_population_pyramid(df_selected_year_chart1, f"Population ({dataset})", selected_year_chart1)
st.plotly_chart(fig_chart1, key="chart1")

# --- Chart 2: Population Difference and Percentage Change ---
st.title("Population Difference and Percentage Change")
st.sidebar.subheader("Chart 2: Population Difference and Percentage Change")

# Inputs for chart 2
variable_chart2 = st.sidebar.radio("Select Variable (Chart 2)", ["Population Difference", "Percentage Difference"])
sex_chart2 = st.sidebar.selectbox("Select Sex (Chart 2)", ["Males and Females (Combined)", "Persons"])
selected_year_chart2 = st.slider("Select Year (Chart 2)", min_value=min(years_chart1), max_value=max(years_chart1))

# Filter and display chart 2
df_chart2 = filter_data(df, sex_chart2, variable_chart2.replace(" ", "_"))
df_selected_year_chart2 = df_chart2[df_chart2["Year"] == selected_year_chart2]
fig_chart2 = plot_population_pyramid_dynamic(
    df_selected_year_chart2, variable_chart2, selected_year_chart2, sex_chart2
)
st.plotly_chart(fig_chart2, key="chart2")
