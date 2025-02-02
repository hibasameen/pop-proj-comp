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

# Function to calculate global x-axis range for Chart 2
def get_global_x_axis_range(df, variable):
    global_min = df[variable].min()
    global_max = df[variable].max()

    # Add padding to ensure the bars are not too close to the edges
    padding = (global_max - global_min) * 0.1
    return [global_min - padding, global_max + padding]

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
            marker=dict(color="purple"),  # Custom color for males
        )
    )

    # Add females
    fig.add_trace(
        go.Bar(
            x=df[df["Value"] > 0]["Value"],
            y=df[df["Value"] > 0]["Age"],
            orientation="h",
            name="Females",
            marker=dict(color="teal"),  # Custom color for females
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

# Function to plot a population pyramid with a fixed global x-axis for Chart 2
def plot_population_pyramid_fixed(df, variable, year, x_axis_range, sex):
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
            marker=dict(color="purple"),  # Custom color for decrease/males
        )
    )

    # Add increase (or females)
    fig.add_trace(
        go.Bar(
            x=df[df["Value"] > 0]["Value"],
            y=df[df["Value"] > 0]["Age"],
            orientation="h",
            name=label_increase,
            marker=dict(color="teal"),  # Custom color for increase/females
        )
    )

    # Update layout to display all age groups and use the fixed global x-axis range
    fig.update_layout(
        title=f"{variable} - Year {year}",
        barmode="overlay",
        xaxis=dict(title=variable, range=x_axis_range),  # Fixed global x-axis range
        yaxis=dict(
            title="Age Group",
            categoryorder="array",
            categoryarray=age_group_order,  # Explicit order of age groups
            tickmode="array",
            tickvals=age_group_order,  # Force all labels to display
        ),
    )

    return fig


# --- Title and Instructions ---
st.title("Population Projections Visualiser")
st.markdown("""
Welcome to the **Population Projections Visualiser**!

This app allows you to explore population data and differences between ONS Principal Population Projections between 2018 and 2022. Here's how to use it:
- **Chart 1**: Select a dataset (2018 or 2022 projections), sex, and year to visualize the population pyramid.
- **Chart 2**: View the population difference or percentage change by selecting a variable, sex, and year.
- Use the sliders and dropdowns to control the charts interactively, and select a category from the legend on the chart to visualise one category only.
""")

# --- Chart 1: Population Projections ---
st.header("ONS Principal Population Projections")
st.sidebar.subheader("Chart 1: Population Projections Pyramid")

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
st.header("Difference between ONS Principal Population Projections from 2018 and 2022")
st.sidebar.subheader("Chart 2: Population Difference and Percentage Change")

# Inputs for chart 2 with default values
variable_chart2 = st.sidebar.radio(
    "Select Variable (Chart 2)",
    ["Population Difference", "Percentage Difference"],
    index=0  # Default to "Population Difference"
)
sex_chart2 = st.sidebar.selectbox(
    "Select Sex (Chart 2)",
    ["Males and Females (Combined)", "Persons"],
    index=1  # Default to "Persons"
)
selected_year_chart2 = st.slider(
    "Select Year (Chart 2)",
    min_value=min(years_chart1),
    max_value=max(years_chart1),
    value=min(years_chart1)  # Default to the earliest year
)

# Precompute global x-axis range for the selected variable
x_axis_range_chart2 = get_global_x_axis_range(df, variable_chart2.replace(" ", "_"))

# Filter and display chart 2
df_chart2 = filter_data(df, sex_chart2, variable_chart2.replace(" ", "_"))
df_selected_year_chart2 = df_chart2[df_chart2["Year"] == selected_year_chart2]
fig_chart2 = plot_population_pyramid_fixed(
    df_selected_year_chart2, variable_chart2, selected_year_chart2, x_axis_range_chart2, sex_chart2
)
st.plotly_chart(fig_chart2, key="chart2")
