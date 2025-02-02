import pandas as pd

# Load the data files
file_path_2018 = "CleanedPopulationData2018.csv"  # Update with your local path if needed
file_path_2022 = "CleanedPopulationData2022.csv"  # Update with your local path if needed

df_2018 = pd.read_csv(file_path_2018)
df_2022 = pd.read_csv(file_path_2022)

# Standardizing column names and values for consistency
df_2018.columns = df_2018.columns.str.strip()
df_2022.columns = df_2022.columns.str.strip()

df_2018['Age Group'] = df_2018['Age Group'].str.replace(' ', '')
df_2022['Age Group'] = df_2022['Age Group'].str.replace(' ', '')

df_2018['Sex'] = df_2018['Sex'].str.strip().str.lower()
df_2022['Sex'] = df_2022['Sex'].str.strip().str.lower()

# Standardizing 'Sex' values to avoid mismatches
df_2018['Sex'] = df_2018['Sex'].replace({'males': 'male', 'females': 'female'})
df_2022['Sex'] = df_2022['Sex'].replace({'males': 'male', 'females': 'female'})

# Renaming population columns to indicate their source year
df_2018.rename(columns={'Population': 'Population_2018'}, inplace=True)
df_2022.rename(columns={'Population': 'Population_2022'}, inplace=True)

# Merging datasets on 'Age Group', 'Sex', and 'Year'
merged_df = pd.merge(df_2018, df_2022, on=['Age Group', 'Sex', 'Year'], how='outer')

# Filtering for years between 2022 and 2060
merged_df = merged_df[(merged_df['Year'] >= 2022) & (merged_df['Year'] <= 2060)]

# Multiplying Population_2018 by 1000
merged_df['Population_2018'] = merged_df['Population_2018'] * 1000

# Calculating the population difference
merged_df['Population_Difference'] = merged_df['Population_2022'] - merged_df['Population_2018']

# Calculating the percentage difference
merged_df['Percentage_Difference'] = (merged_df['Population_Difference'] / merged_df['Population_2018']) * 100

# Save to CSV or print for review
output_file = "Merged_Population_Analysis.csv"
merged_df.to_csv(output_file, index=False)

print(f"Analysis completed. Data saved to {output_file}")
