import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load data
@st.cache
def load_data():
    # Replace with the correct file path
    df = pd.read_csv("path/to/population_difference_2018_vs_2022.csv")
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
@st.cache
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

# Create an animated population pyramid
def plot_animated_pyramid(df, variable, sex):
    frames = []
    years = df["Year"].unique()
    for year in years:
        df_year = df[df["Year"] == year]
        frames.append(
            go.Frame(
                data=[
                    go.Bar(
                        x=df_year[df_year["Value"] < 0]["Value"],  # Males (negative)
                        y=df_year[df_year["Value"] < 0]["Age"],
                        orientation="h",
                        name="Males",
                        marker=dict(color="blue"),
                    ),
                    go.Bar(
                        x=df_year[df_year["Value"] > 0]["Value"],  # Females (positive)
                        y=df_year[df_year["Value"] > 0]["Age"],
                        orientation="h",
                        name="Females",
                        marker=dict(color="red"),
                    ),
                ],
                name=str(year),
            )
        )

    fig = go.Figure(
        data=[
            go.Bar(
                x=df[df["Value"] < 0]["Value"],
                y=df[df["Value"] < 0]["Age"],
                orientation="h",
                name="Males",
                marker=dict(color="blue"),
            ),
            go.Bar(
                x=df[df["Value"] > 0]["Value"],
                y=df[df["Value"] > 0]["Age"],
                orientation="h",
                name="Females",
                marker=dict(color="red"),
            ),
        ],
        layout=go.Layout(
            title=f"{variable} Over Time",
            barmode="overlay",
            xaxis=dict(title=variable),
            yaxis=dict(title="Age Group", categoryorder="total ascending"),
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    buttons=[
                        dict(
                            label="Play",
                            method="animate",
                            args=[None, dict(frame=dict(duration=500, redraw=True), fromcurrent=True)],
                        ),
                        dict(
                            label="Pause",
                            method="animate",
                            args=[[None], dict(frame=dict(duration=0, redraw=False)]],  # Fixed parenthesis
                        ),
                    ],
                )
            ],
        ),
        frames=frames,
    )
    return fig

# Display the interactive animation
st.title("Animated Population Pyramid Visualization")
st.write(f"Visualizing: **{variable}** for **{sex}**")
fig = plot_animated_pyramid(df_filtered, variable, sex)
st.plotly_chart(fig)
