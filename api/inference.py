import os
import pickle
import numpy as np
import tensorflow as tf
from dotenv import load_dotenv
from src.infrastructure.custom_layers import SpatialDensityEmbedding, zonasi_custom_loss, RoundedMAE

load_dotenv()

def run_inference():
    # 1. Load Model & Scaler
    try:
        model = tf.keras.models.load_model(
            "models/zonify_model.keras",
            custom_objects={
                "SpatialDensityEmbedding": SpatialDensityEmbedding,
                "zonasi_custom_loss": zonasi_custom_loss,
                "RoundedMAE": RoundedMAE,
            },
        )
        with open("models/scaler.pkl", "rb") as f:
            scaler = pickle.load(f)
        print("✅ Model & Scaler loaded successfully.")
    except Exception as e:
        print(f"❌ Failed to load model/scaler: {e}")
        return

    # 2. Sample Inference Process
    # Features: [lat, long, density, dist_comp, h2h, dist_mkt, cluster_macro, cluster_hotspot]
    sample_input = np.array([[-6.2363, 106.8568, 5, 162.63, 0, 144.52, 4, -1]], dtype=np.float32)
    
    try:
        scaled_input = scaler.transform(sample_input)
        probability = float(model.predict(scaled_input, verbose=0)[0][0])

        print("-" * 30)
        print(f"Probabilitas Pelanggaran: {probability:.4f}")
        print(f"Status: {'⚠️ PELANGGARAN' if probability >= 0.5 else '✅ PATUH'}")
        print("-" * 30)
    except Exception as e:
        print(f"❌ Inference error: {e}")

if __name__ == "__main__":
    run_inference()
