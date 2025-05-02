# src/models.py
import pandas as pd
from sklearn.cluster import KMeans
import joblib

def train_clustering_model(input_path="data/processed/engineered_nepal_dataset.csv", n_clusters=4):
    # Load engineered dataset
    df = pd.read_csv(input_path)

    # Select only numeric features
    numeric_df = df.select_dtypes(include=["number"]).copy()

    # Drop any rows with NaN (if any remain)
    numeric_df = numeric_df.dropna()

    # Train KMeans model
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df.loc[numeric_df.index, 'Cluster'] = kmeans.fit_predict(numeric_df)

    # Save the model
    joblib.dump(kmeans, "models/clustering/kmeans_model.joblib")

    # Save clustered dataset
    df.to_csv("data/processed/clustered_nepal_dataset.csv", index=False)
    print("✅ Clustered dataset saved as 'data/processed/clustered_nepal_dataset.csv'")
    print("✅ KMeans model saved as 'models/clustering/kmeans_model.joblib'")

if __name__ == "__main__":
    train_clustering_model()
