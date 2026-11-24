import os
import tempfile
import unittest

from ml.generate_dataset import generate_synthetic_dataset
from ml.train_model import train_and_save_model
from services.fraud_service import build_explainable_reasons, classify_risk


class TestMLPipeline(unittest.TestCase):
    def test_synthetic_dataset_shape_and_labels(self):
        df = generate_synthetic_dataset(n_samples=200, random_state=42)
        self.assertEqual(len(df), 200)
        self.assertIn("is_suspicious", df.columns)
        self.assertTrue(set(df["is_suspicious"].unique()).issubset({0, 1}))

    def test_risk_classification_thresholds(self):
        self.assertEqual(classify_risk(0), "Low Risk")
        self.assertEqual(classify_risk(30), "Low Risk")
        self.assertEqual(classify_risk(30.1), "Medium Risk")
        self.assertEqual(classify_risk(60), "Medium Risk")
        self.assertEqual(classify_risk(60.1), "High Risk")
        self.assertEqual(classify_risk(100), "High Risk")

    def test_explainable_reasons_generation(self):
        features = {
            "goal_amount": 80000.0,
            "description_length": 60,
            "document_available": 0,
            "creator_account_age_days": 2,
            "completeness_score": 0.25,
            "previous_suspicious_count": 2,
            "duration_days": 7,
            "donation_velocity_anomaly": 0.75,
            "urgent_keyword_ratio": 0.5,
        }
        reasons = build_explainable_reasons(features, "High Risk")
        self.assertGreaterEqual(len(reasons), 5)

    def test_model_training_and_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_path = os.path.join(tmpdir, "dataset.csv")
            artifacts_dir = os.path.join(tmpdir, "artifacts")
            df = generate_synthetic_dataset(n_samples=300, random_state=42)
            df.to_csv(dataset_path, index=False)

            metrics = train_and_save_model(dataset_path=dataset_path, artifacts_dir=artifacts_dir)
            self.assertGreater(metrics["accuracy"], 0.80)
            self.assertTrue(os.path.exists(os.path.join(artifacts_dir, "fraud_model.pkl")))
            self.assertTrue(os.path.exists(os.path.join(artifacts_dir, "scaler.pkl")))
            self.assertTrue(os.path.exists(os.path.join(artifacts_dir, "metrics.json")))


if __name__ == "__main__":
    unittest.main()
