import pandas as pd

# Reload the uploaded dataset
file_path = "population_difference_2018_vs_2022.csv"
df_difference = pd.read_csv(file_path)

# Step 1: Prepare the 2018 dataset
df_population_2018 = df_difference[["Year", "Age", "Sex", "Population_2018"]]
df_population_2018.rename(columns={"Population_2018": "Population"}, inplace=True)

# Step 2: Prepare the 2022 dataset
df_population_2022 = df_difference[["Year", "Age", "Sex", "Population_2022"]]
df_population_2022.rename(columns={"Population_2022": "Population"}, inplace=True)

# Step 3: Use the existing df_difference for population differences

# Save the datasets to CSV
file_2018 = "app/data/2018_projections.csv"
file_2022 = "app/data/2022_projections.csv"
file_difference = "app/data/population_difference_2018_vs_2022.csv"

df_population_2018.to_csv(file_2018, index=False)
df_population_2022.to_csv(file_2022, index=False)
df_difference.to_csv(file_difference, index=False)

file_2018, file_2022, file_difference
