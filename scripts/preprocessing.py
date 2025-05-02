# scripts/preprocessing.py
import pandas as pd

def merge_datasets():
    # Load datasets
    precip_df = pd.read_csv("data/raw/cleaned_district_precipitation_trends.csv")
    glacial_df = pd.read_csv("data/raw/cleaned_glacial_data.csv")
    agri_df = pd.read_csv("data/raw/cleaned_agriculture-and-rural-development_npl.csv")
    mapping_df = pd.read_csv("data/raw/district_basin_mapping.csv")

    # Clean precipitation data
    precip_numeric_cols = ['Winter_Trend', 'Monsoon_Trend', 'Annual_Trend']
    for col in precip_numeric_cols:
        if col in precip_df.columns:
            precip_df[col] = precip_df[col].astype(str).str.replace(r'\+', '', regex=True).str.strip()
            precip_df[col] = precip_df[col].replace(r'^\s*\+?\s*$', '0', regex=True)
            precip_df[col] = precip_df[col].replace('', '0')
            precip_df[col] = pd.to_numeric(precip_df[col], errors='coerce')
            precip_df[col] = precip_df[col].fillna(precip_df[col].mean())
            precip_df[col] = precip_df[col].astype('float64')

    # Clean glacial data
    glacial_numeric_cols = ['Glaciers Number', 'Glaciers Area (sq. km)', 'Glacial Lakes Number', 'Glacial Lakes Area (sq. km)']
    glacial_df = glacial_df[glacial_df['Basins'] != 'Total']
    for col in glacial_numeric_cols:
        if col in glacial_df.columns:
            glacial_df[col] = glacial_df[col].astype(str).str.replace(r'\+', '', regex=True).str.strip()
            glacial_df[col] = glacial_df[col].replace(r'^\s*\+?\s*$', '0', regex=True)
            glacial_df[col] = glacial_df[col].replace('', '0')
            glacial_df[col] = pd.to_numeric(glacial_df[col], errors='coerce')
            glacial_df[col] = glacial_df[col].fillna(glacial_df[col].mean())
            glacial_df[col] = glacial_df[col].astype('float64')

    # Filter and pivot agricultural data for 2020
    agri_2020 = agri_df[agri_df['year'] == 2020].pivot_table(
        index='year', columns='indicator_name', values='value', aggfunc='first'
    ).reset_index()
    agri_2020 = agri_2020[[
        'year', 'Cereal yield (kg per hectare)', 'Agricultural land (% of land area)',
        'Rural population (% of total population)'
    ]]
    # Clean agricultural data
    agri_numeric_cols = ['Cereal yield (kg per hectare)', 'Agricultural land (% of land area)', 'Rural population (% of total population)']
    for col in agri_numeric_cols:
        if col in agri_2020.columns:
            agri_2020[col] = agri_2020[col].astype(str).str.replace(r'\+', '', regex=True).str.strip()
            agri_2020[col] = agri_2020[col].replace(r'^\s*\+?\s*$', '0', regex=True)
            agri_2020[col] = agri_2020[col].replace('', '0')
            agri_2020[col] = pd.to_numeric(agri_2020[col], errors='coerce')
            agri_2020[col] = agri_2020[col].fillna(agri_2020[col].mean())
            agri_2020[col] = agri_2020[col].astype('float64')

    # Merge datasets
    merged_df = precip_df.merge(mapping_df, left_on='Districts', right_on='District', how='left')
    merged_df = merged_df.merge(glacial_df, left_on='Basin', right_on='Basins', how='left')
    merged_df['key'] = 1
    agri_2020['key'] = 1
    final_df = merged_df.merge(agri_2020, on='key', how='left').drop(columns=['key', 'year', 'District', 'Basins'])

    # Save merged dataset
    final_df.to_csv("data/processed/merged_nepal_dataset.csv", index=False)
    print("Merged dataset saved as 'data/processed/merged_nepal_dataset.csv'")

if __name__ == "__main__":
    merge_datasets()