# src/feature_engineering.py
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

def engineer_features(input_path="data/processed/merged_nepal_dataset.csv",
                      output_path="data/processed/engineered_nepal_dataset.csv"):
    # Load dataset
    df = pd.read_csv(input_path)

    # Handle missing values
    for col in ['Glaciers Number', 'Glaciers Area (sq. km)', 'Glacial Lakes Number', 'Glacial Lakes Area (sq. km)']:
        if col in df.columns:
            df[col] = df.groupby('Basin')[col].transform(lambda x: x.fillna(x.mean()))
    df = df.dropna(subset=['Basin'])

    # Encode categorical features
    if 'Basin' in df.columns:
        le = LabelEncoder()
        df['Basin_Encoded'] = le.fit_transform(df['Basin'])
    df = df.drop(columns=[col for col in ['Districts', 'Basin'] if col in df.columns])

    # Clean numeric columns
    numeric_cols = [
        'Winter_Trend', 'Monsoon_Trend', 'Annual_Trend',
        'Glaciers Number', 'Glaciers Area (sq. km)',
        'Glacial Lakes Number', 'Glacial Lakes Area (sq. km)'
    ]
    numeric_cols = [col for col in numeric_cols if col in df.columns]

    for col in numeric_cols:
        df[col] = df[col].astype(str).str.replace('+', '', regex=False).str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(df[col].mean())

    # Create interaction and ratio features
    if 'Monsoon_Trend' in df.columns and 'Glaciers Area (sq. km)' in df.columns:
        df['Monsoon_Glacier_Interaction'] = df['Monsoon_Trend'] * df['Glaciers Area (sq. km)']
    if 'Glaciers Area (sq. km)' in df.columns and 'Glacial Lakes Area (sq. km)' in df.columns:
        df['Glacier_Lake_Ratio'] = df['Glaciers Area (sq. km)'] / (df['Glacial Lakes Area (sq. km)'] + 1e-6)

    # Normalize numeric features
    updated_numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    scaler = StandardScaler()
    df[updated_numeric_cols] = scaler.fit_transform(df[updated_numeric_cols])

    # Drop constant columns
    constant_cols = df.columns[df.nunique() == 1]
    df = df.drop(columns=constant_cols)

    # Aggregated features
    possible_trend_cols = ['Winter_Trend', 'Monsoon_Trend', 'Pre_Monsoon_Trend', 'Post_Monsoon_Trend', 'Annual_Trend']
    trend_cols = [col for col in possible_trend_cols if col in df.columns]
    df['Total_Trend_Magnitude'] = df[trend_cols].abs().sum(axis=1) if trend_cols else 0

    if 'Glaciers Area (sq. km)' in df.columns and 'Glacial Lakes Area (sq. km)' in df.columns:
        df['Total_Glacial_Resources'] = df['Glaciers Area (sq. km)'] + df['Glacial Lakes Area (sq. km)']
    else:
        df['Total_Glacial_Resources'] = 0

    # Domain-specific features
    if 'Monsoon_Trend' in df.columns:
        df['High_Monsoon_Trend'] = (df['Monsoon_Trend'] > df['Monsoon_Trend'].median()).astype(int)
    else:
        df['High_Monsoon_Trend'] = 0

    if 'Glaciers Area (sq. km)' in df.columns:
        df['Glacial_Dependency'] = df['Glaciers Area (sq. km)'] / df['Glaciers Area (sq. km)'].max()
    else:
        df['Glacial_Dependency'] = 0

    # Select only numeric data before correlation
    numeric_df = df.select_dtypes(include=['number'])
    corr_matrix = numeric_df.corr()

    # Drop highly correlated features
    high_corr = set()
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if abs(corr_matrix.iloc[i, j]) > 0.8:
                high_corr.add(corr_matrix.columns[i])
    df = df.drop(columns=list(high_corr))

    # Save the final engineered dataset
    df.to_csv(output_path, index=False)
    print(f"✅ Engineered dataset saved to: {output_path}")

if __name__ == "__main__":
    engineer_features()
