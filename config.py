import os
from datetime import timedelta


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get("SECRET_KEY", "fundforward-dev-secret-key-change-in-production")

    # SQLite Database
    DATABASE_PATH = os.environ.get(
        "DATABASE_PATH", os.path.join(BASE_DIR, "database", "fundforward.db")
    )

    # File Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    CAMPAIGN_IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, "campaigns")
    DOCUMENT_FOLDER = os.path.join(UPLOAD_FOLDER, "documents")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload size

    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "doc", "docx", "txt"}

    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # ML Model Artifacts
    ML_DIR = os.path.join(BASE_DIR, "ml")
    MODEL_PATH = os.path.join(ML_DIR, "model_artifacts", "fraud_model.pkl")
    SCALER_PATH = os.path.join(ML_DIR, "model_artifacts", "scaler.pkl")
    METRICS_PATH = os.path.join(ML_DIR, "model_artifacts", "metrics.json")
    DATASET_PATH = os.path.join(ML_DIR, "dataset.csv")

    # Risk Score Demonstration Thresholds (0-100)
    LOW_RISK_MAX = 30
    MEDIUM_RISK_MAX = 60

    # Campaign Categories
    CATEGORIES = [
        "Medical & Health",
        "Education",
        "Technology & Innovation",
        "Community & Social",
        "Environment & Sustainability",
        "Emergency Relief",
        "Arts & Culture",
        "Small Business",
    ]


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
