import json
import os
import re
import joblib
import numpy as np
import pandas as pd

from config import Config
from ml import FEATURE_COLUMNS
from ml.train_model import train_and_save_model
from models.campaign import get_campaign_by_id
from models.donation import list_campaign_donations
from models.fraud import upsert_fraud_analysis

URGENT_KEYWORDS = [
    "urgent",
    "guaranteed",
    "100% return",
    "double your",
    "send immediately",
    "act now",
    "wire",
    "miracle",
    "secret",
    "crypto",
    "no questions",
    "limited time",
]

_MODEL_CACHE = {"model": None, "scaler": None}


def _load_model_and_scaler():
    if _MODEL_CACHE["model"] is not None and _MODEL_CACHE["scaler"] is not None:
        return _MODEL_CACHE["model"], _MODEL_CACHE["scaler"]

    if not (os.path.exists(Config.MODEL_PATH) and os.path.exists(Config.SCALER_PATH)):
        train_and_save_model(Config.DATASET_PATH, os.path.dirname(Config.MODEL_PATH))

    _MODEL_CACHE["model"] = joblib.load(Config.MODEL_PATH)
    _MODEL_CACHE["scaler"] = joblib.load(Config.SCALER_PATH)
    return _MODEL_CACHE["model"], _MODEL_CACHE["scaler"]


def get_model_metrics() -> dict:
    if not os.path.exists(Config.METRICS_PATH):
        return train_and_save_model(Config.DATASET_PATH, os.path.dirname(Config.MODEL_PATH))
    with open(Config.METRICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_completeness_score(campaign: dict) -> float:
    checks = [
        bool((campaign.get("location") or "").strip()),
        bool((campaign.get("beneficiary_name") or "").strip()),
        bool((campaign.get("contact_phone") or "").strip()),
        bool((campaign.get("image_filename") or "").strip()),
        bool((campaign.get("document_filename") or "").strip()),
        len((campaign.get("short_summary") or "").strip()) >= 20,
    ]
    return round(sum(checks) / len(checks), 2)


def compute_urgent_keyword_ratio(title: str, description: str) -> float:
    text = f"{title} {description}".lower()
    words = re.findall(r"\w+", text)
    if not words:
        return 0.0
    hits = sum(1 for kw in URGENT_KEYWORDS if kw in text)
    return round(min(1.0, hits / 4.0), 3)


def compute_donation_velocity_anomaly(campaign_id: int, goal_amount: float) -> float:
    donations = list_campaign_donations(campaign_id)
    if not donations:
        return 0.0
    amounts = [d["amount"] for d in donations]
    max_single = max(amounts)
    # High concentration in a single donation relative to goal or total
    if goal_amount > 0 and (max_single / goal_amount) > 0.65 and len(donations) <= 2:
        return 0.72
    if len(donations) >= 3:
        mean_amt = float(np.mean(amounts))
        std_amt = float(np.std(amounts))
        if mean_amt > 0 and (std_amt / mean_amt) > 1.8:
            return 0.58
    return 0.08


def extract_campaign_features(campaign: dict) -> dict:
    doc_available = 1 if (campaign.get("document_filename") or "").strip() else 0
    desc_len = len((campaign.get("description") or "").strip())
    completeness = compute_completeness_score(campaign)
    urgent_ratio = compute_urgent_keyword_ratio(
        campaign.get("title", ""), campaign.get("description", "")
    )
    velocity_anomaly = compute_donation_velocity_anomaly(
        campaign["id"], float(campaign.get("goal_amount", 1.0))
    )

    return {
        "goal_amount": float(campaign["goal_amount"]),
        "description_length": int(desc_len),
        "document_available": int(doc_available),
        "creator_account_age_days": int(campaign.get("creator_account_age_days", 1)),
        "completeness_score": float(completeness),
        "previous_suspicious_count": int(campaign.get("creator_suspicious_count", 0)),
        "duration_days": int(campaign.get("duration_days", 30)),
        "donation_velocity_anomaly": float(velocity_anomaly),
        "urgent_keyword_ratio": float(urgent_ratio),
    }


def classify_risk(risk_score: float) -> str:
    if risk_score <= Config.LOW_RISK_MAX:
        return "Low Risk"
    if risk_score <= Config.MEDIUM_RISK_MAX:
        return "Medium Risk"
    return "High Risk"


def build_explainable_reasons(features: dict, risk_category: str) -> list:
    reasons = []
    if features["document_available"] == 0:
        reasons.append("No supporting verification document was uploaded.")
    else:
        reasons.append("Supporting verification document is attached.")

    if features["description_length"] < 150:
        reasons.append(
            f"Campaign description is unusually brief ({features['description_length']} characters)."
        )
    elif features["description_length"] >= 300:
        reasons.append(
            f"Detailed campaign narrative provided ({features['description_length']} characters)."
        )

    if features["goal_amount"] >= 40000:
        reasons.append(f"High fundraising target (${features['goal_amount']:,.0f}) increases review sensitivity.")

    if features["creator_account_age_days"] < 14:
        reasons.append(
            f"Creator account is newly registered ({features['creator_account_age_days']} days old)."
        )
    elif features["creator_account_age_days"] >= 90:
        reasons.append(
            f"Established creator account ({features['creator_account_age_days']} days old)."
        )

    if features["completeness_score"] < 0.5:
        reasons.append(
            f"Low campaign profile completeness ({int(features['completeness_score'] * 100)}%)."
        )
    elif features["completeness_score"] >= 0.8:
        reasons.append(
            f"High campaign profile completeness ({int(features['completeness_score'] * 100)}%)."
        )

    if features["previous_suspicious_count"] > 0:
        reasons.append(
            f"Creator account has {features['previous_suspicious_count']} prior suspicious activity flag(s)."
        )

    if features["urgent_keyword_ratio"] >= 0.25:
        reasons.append("High-urgency or promotional claim keywords detected in campaign text.")

    if features["donation_velocity_anomaly"] >= 0.5:
        reasons.append("Unusual donation concentration or velocity pattern observed.")

    if features["duration_days"] <= 10 or features["duration_days"] >= 120:
        reasons.append(f"Unusual campaign duration ({features['duration_days']} days).")

    if not reasons:
        reasons.append(f"Overall campaign profile aligns with {risk_category.lower()} patterns.")
    return reasons


def analyze_campaign_fraud(campaign_id: int, db_path=None) -> dict:
    """Run trained Random Forest model on a campaign and persist results to SQLite."""
    campaign = get_campaign_by_id(campaign_id, db_path=db_path)
    if not campaign:
        raise ValueError(f"Campaign {campaign_id} not found.")

    features = extract_campaign_features(campaign)
    model, scaler = _load_model_and_scaler()

    feature_df = pd.DataFrame([[features[col] for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
    scaled_X = scaler.transform(feature_df)

    # Probability of class 1 (suspicious)
    fraud_prob = float(model.predict_proba(scaled_X)[0][1])
    risk_score = round(fraud_prob * 100.0, 1)
    risk_category = classify_risk(risk_score)
    reasons = build_explainable_reasons(features, risk_category)

    upsert_fraud_analysis(
        campaign_id=campaign_id,
        risk_score=risk_score,
        risk_category=risk_category,
        fraud_probability=round(fraud_prob, 4),
        reasons_json=json.dumps(reasons),
        features_json=json.dumps(features),
        model_version="RandomForest-v1",
        db_path=db_path,
    )

    return {
        "campaign_id": campaign_id,
        "risk_score": risk_score,
        "risk_category": risk_category,
        "fraud_probability": round(fraud_prob, 4),
        "reasons": reasons,
        "features": features,
    }
