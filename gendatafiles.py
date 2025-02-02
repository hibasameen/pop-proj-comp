import pandas as pd

# File paths
file_2022_path = "en_ppp_machine_readable.xlsx"  # Raw Excel file with population projections

# Load the Excel file
xls = pd.ExcelFile(file_2022_path)

# Load the relevant sheet that contains the age group population projections
df_2022_to_2060 = pd.read_excel(xls, sheet_name="Population_in_age_groups")

# Extract relevant columns for years 2022-2060
columns_to_extract = ['Sex', 'Age'] + [year for year in range(2022, 2061)]
df_2022_to_2060 = df_2022_to_2060[columns_to_extract]

# Reshape data to long format
df_2022_to_2060 = df_2022_to_2060.melt(id_vars=['Sex', 'Age'], var_name='Year', value_name='Population')
df_2022_to_2060.columns = ['Sex', 'Age Group', 'Year', 'Population']

# Standardize age group labels
df_2022_to_2060['Age Group'] = df_2022_to_2060['Age Group'].replace({
    '100 - 104': '100-104',
    '105 and over': '105 & over'
})

# Sum the population counts for "100-104" and "105 & over" into "100 & over"
df_100_over = df_2022_to_2060[df_2022_to_2060['Age Group'].isin(['100-104', '105 & over'])]
df_100_over = df_100_over.groupby(['Sex', 'Year'], as_index=False).agg({'Population': 'sum'})
df_100_over['Age Group'] = '100 & over'

# Remove the original "100-104" and "105 & over" rows
df_2022_to_2060 = df_2022_to_2060[~df_2022_to_2060['Age Group'].isin(['100-104', '105 & over'])]

# Append the new "100 & over" category
df_2022_to_2060 = pd.concat([df_2022_to_2060, df_100_over], ignore_index=True)

# Define the custom sorting order for age groups
age_order = [
    '0 - 4', '5 - 9', '10 - 14', '15 - 19', '20 - 24', '25 - 29', '30 - 34', 
    '35 - 39', '40 - 44', '45 - 49', '50 - 54', '55 - 59', '60 - 64', '65 - 69', 
    '70 - 74', '75 - 79', '80 - 84', '85 - 89', '90 - 94', '95 - 99', '100 & over'
]

# Convert age group to categorical type for correct sorting
df_2022_to_2060['Age Group'] = pd.Categorical(df_2022_to_2060['Age Group'], categories=age_order, ordered=True)

# Sort by Sex, Year, and Age Group
df_2022_to_2060 = df_2022_to_2060.sort_values(by=['Sex', 'Year', 'Age Group'])

# Save the final dataset
output_file = "CleanedPopulationData2022_2060_Sorted.csv"
df_2022_to_2060.to_csv(output_file, index=False)

print(f"Processed data saved to {output_file}")
