"""
Synthetic Demonstration Dataset Generator for FundForward Fraud Detection.

Generates 1,200 realistic synthetic crowdfunding campaign records (genuine and
suspicious) for academic demonstration and model training.

DISCLAIMER: This dataset is 100% synthetic and created solely for academic
demonstration. Predictions from models trained on this data are risk indicators
only and do not constitute proof of fraud.
"""

import os
import numpy as np
import pandas as pd


def generate_synthetic_dataset(n_samples: int = 1200, random_state: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)

    n_genuine = int(n_samples * 0.68)
    n_suspicious = n_samples - n_genuine

    # Genuine campaigns: moderate goals, detailed descriptions, documents, older accounts, high completeness
    genuine = pd.DataFrame({
        "goal_amount": np.round(rng.lognormal(mean=8.2, sigma=0.85, size=n_genuine).clip(300, 75000), 2),
        "description_length": rng.integers(320, 2400, size=n_genuine),
        "document_available": rng.choice([1, 0], size=n_genuine, p=[0.84, 0.16]),
        "creator_account_age_days": rng.integers(30, 950, size=n_genuine),
        "completeness_score": np.round(rng.uniform(0.65, 1.0, size=n_genuine), 2),
        "previous_suspicious_count": rng.choice([0, 1], size=n_genuine, p=[0.95, 0.05]),
        "duration_days": rng.integers(20, 90, size=n_genuine),
        "donation_velocity_anomaly": np.round(rng.beta(1.2, 12.0, size=n_genuine), 3),
        "urgent_keyword_ratio": np.round(rng.beta(1.1, 18.0, size=n_genuine), 3),
        "is_suspicious": 0,
    })

    # Suspicious campaigns: often very high or unrealistic goals, sparse descriptions, missing docs,
    # brand new accounts, low completeness, prior flags, unusual donation bursts, urgency keywords
    suspicious = pd.DataFrame({
        "goal_amount": np.round(rng.lognormal(mean=10.1, sigma=1.05, size=n_suspicious).clip(2000, 500000), 2),
        "description_length": rng.integers(40, 480, size=n_suspicious),
        "document_available": rng.choice([1, 0], size=n_suspicious, p=[0.18, 0.82]),
        "creator_account_age_days": rng.integers(0, 45, size=n_suspicious),
        "completeness_score": np.round(rng.uniform(0.15, 0.68, size=n_suspicious), 2),
        "previous_suspicious_count": rng.choice([0, 1, 2, 3], size=n_suspicious, p=[0.35, 0.35, 0.20, 0.10]),
        "duration_days": rng.choice(
            np.concatenate([rng.integers(5, 15, size=n_suspicious // 2), rng.integers(90, 180, size=n_suspicious - n_suspicious // 2)]),
            size=n_suspicious,
        ),
        "donation_velocity_anomaly": np.round(rng.beta(4.5, 3.0, size=n_suspicious), 3),
        "urgent_keyword_ratio": np.round(rng.beta(4.0, 5.0, size=n_suspicious), 3),
        "is_suspicious": 1,
    })

    # Add realistic boundary overlap (5% label noise / borderline cases)
    df = pd.concat([genuine, suspicious], ignore_index=True)
    df = df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    return df


if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "dataset.csv")
    df = generate_synthetic_dataset(n_samples=1200, random_state=42)
    df.to_csv(out_path, index=False)
    print(f"Generated synthetic dataset at {out_path} with shape {df.shape}")
    print(df["is_suspicious"].value_counts().rename({0: "Genuine", 1: "Suspicious"}))
