"""
ML Model Training & Evaluation Script for FundForward Fraud Detection.

Pipeline:
1. Load synthetic dataset (generates it if missing).
2. Preprocess & select features.
3. Train/test split (80/20 stratified).
4. Scale numeric features with StandardScaler.
5. Train RandomForestClassifier.
6. Evaluate Accuracy, Precision, Recall, F1-score, and Confusion Matrix.
7. Serialize model, scaler, and evaluation metrics to ml/model_artifacts/.
"""

import json
import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Allow running directly as `python ml/train_model.py`
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml import FEATURE_COLUMNS
from ml.generate_dataset import generate_synthetic_dataset


def train_and_save_model(dataset_path: str = None, artifacts_dir: str = None) -> dict:
    ml_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = dataset_path or os.path.join(ml_dir, "dataset.csv")
    artifacts_dir = artifacts_dir or os.path.join(ml_dir, "model_artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    # 1. Data collection / generation
    if not os.path.exists(dataset_path):
        df = generate_synthetic_dataset(n_samples=1200, random_state=42)
        df.to_csv(dataset_path, index=False)
    else:
        df = pd.read_csv(dataset_path)

    # 2. Preprocessing & feature selection
    df = df.dropna(subset=FEATURE_COLUMNS + ["is_suspicious"]).copy()
    X = df[FEATURE_COLUMNS].astype(float)
    y = df["is_suspicious"].astype(int)

    # 3. Stratified Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # 4. Feature Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 5. Model Training (Random Forest Classifier)
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X_train_scaled, y_train)

    # 6. Evaluation
    y_pred = model.predict(X_test_scaled)
    cm = confusion_matrix(y_test, y_pred)

    feature_importances = {
        col: round(float(imp), 4)
        for col, imp in zip(FEATURE_COLUMNS, model.feature_importances_)
    }

    metrics = {
        "model_type": "RandomForestClassifier",
        "model_version": "RandomForest-v1",
        "dataset_size": int(len(df)),
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "confusion_matrix": {
            "tn": int(cm[0, 0]),
            "fp": int(cm[0, 1]),
            "fn": int(cm[1, 0]),
            "tp": int(cm[1, 1]),
        },
        "feature_importances": feature_importances,
        "thresholds": {
            "low_risk": "0-30",
            "medium_risk": "31-60",
            "high_risk": "61-100",
        },
        "disclaimer": (
            "Trained on synthetic demonstration data. Risk scores are probabilistic "
            "indicators for academic demonstration and do not constitute proof of fraud."
        ),
    }

    # 7. Model Serialization
    joblib.dump(model, os.path.join(artifacts_dir, "fraud_model.pkl"))
    joblib.dump(scaler, os.path.join(artifacts_dir, "scaler.pkl"))
    with open(os.path.join(artifacts_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("=== FundForward Fraud Detection Model Training Complete ===")
    print(f"Dataset samples : {metrics['dataset_size']} (Train: {metrics['train_size']}, Test: {metrics['test_size']})")
    print(f"Accuracy        : {metrics['accuracy']:.4f}")
    print(f"Precision       : {metrics['precision']:.4f}")
    print(f"Recall          : {metrics['recall']:.4f}")
    print(f"F1-Score        : {metrics['f1_score']:.4f}")
    print(f"Confusion Matrix: TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]}")
    print(f"Saved artifacts to: {artifacts_dir}")
    return metrics


if __name__ == "__main__":
    train_and_save_model()
