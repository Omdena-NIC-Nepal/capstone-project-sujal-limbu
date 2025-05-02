# src/dashboard.py
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Nepal Climate-Agriculture Dashboard", layout="wide")

# Load dataset
df = pd.read_csv("data/processed/engineered_nepal_dataset.csv")

# Title
st.title("📊 Nepal Climate-Agriculture Dashboard")

# Sidebar controls
st.sidebar.header("🎛️ Controls")

numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
all_columns = df.columns.tolist()

# Select X and Y axes
x_axis = st.sidebar.selectbox("📉 Select X-axis", numeric_columns, index=numeric_columns.index('Monsoon_Trend') if 'Monsoon_Trend' in numeric_columns else 0)
y_axis = st.sidebar.selectbox("📈 Select Y-axis", numeric_columns, index=numeric_columns.index('Glaciers Area (sq. km)') if 'Glaciers Area (sq. km)' in numeric_columns else 1)

# Hue and size selectors
use_hue = st.sidebar.checkbox("🎨 Add Hue (Color Grouping)", value='Basin_Encoded' in df.columns)
hue_col = None
if use_hue:
    hue_col = st.sidebar.selectbox("Choose hue column", [col for col in all_columns if df[col].nunique() < 20 and col != x_axis and col != y_axis])

use_size = st.sidebar.checkbox("🔘 Add Size (Bubble size)", value='Total_Glacial_Resources' in df.columns)
size_col = None
if use_size:
    size_col = st.sidebar.selectbox("Choose size column", [col for col in numeric_columns if col != x_axis and col != y_axis])

# Filter by Total_Glacial_Resources if present
df_filtered = df.copy()
if 'Total_Glacial_Resources' in df.columns:
    min_val = df['Total_Glacial_Resources'].min()
    max_val = df['Total_Glacial_Resources'].max()
    selected_range = st.sidebar.slider("🌊 Filter by Total Glacial Resources", min_val, max_val, (min_val, max_val))
    df_filtered = df[(df['Total_Glacial_Resources'] >= selected_range[0]) & (df['Total_Glacial_Resources'] <= selected_range[1])]
else:
    st.sidebar.warning("⚠️ 'Total_Glacial_Resources' not found in dataset.")

# Heatmap toggle
show_heatmap = st.sidebar.checkbox("🔍 Show Correlation Heatmap", value=True)

# Main plots
st.subheader("📌 Scatter Plot")
fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.scatterplot(
    data=df_filtered,
    x=x_axis,
    y=y_axis,
    hue=hue_col if use_hue else None,
    size=size_col if use_size else None,
    ax=ax1,
    sizes=(30, 200),
    palette="Set2"
)
plt.title(f"{y_axis} vs {x_axis}")
st.pyplot(fig1)

# Heatmap
if show_heatmap:
    st.subheader("🔗 Correlation Heatmap")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.heatmap(df_filtered.corr(numeric_only=True), annot=True, cmap='coolwarm', ax=ax2)
    st.pyplot(fig2)

# Download section
st.subheader("📥 Download Filtered Dataset")
csv = df_filtered.to_csv(index=False)
st.download_button(
    label="Download CSV File",
    data=csv,
    file_name="filtered_nepal_dataset.csv",
    mime="text/csv"
)
