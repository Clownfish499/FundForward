import os
import tempfile
import unittest

from app import create_app
from config import TestConfig
from init_db import seed_database


class TestFundForwardApp(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)

        class LocalTestConfig(TestConfig):
            DATABASE_PATH = self.db_path

        # Point Config.DATABASE_PATH for models/db helpers during test
        import config
        config.Config.DATABASE_PATH = self.db_path

        seed_database(self.db_path)
        self.app = create_app(LocalTestConfig)
        self.client = self.app.test_client()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_public_pages_load(self):
        for route in ["/", "/explore", "/about", "/how-it-works", "/login", "/register"]:
            resp = self.client.get(route)
            self.assertEqual(resp.status_code, 200, f"Failed on {route}")

    def test_admin_route_requires_admin(self):
        resp = self.client.get("/admin/", follow_redirects=False)
        self.assertEqual(resp.status_code, 302)

    def test_user_registration_and_campaign_submission_with_ml(self):
        # Register new user
        resp = self.client.post(
            "/register",
            data={
                "full_name": "Test Creator",
                "email": "creator_test@example.com",
                "password": "Password123",
                "confirm_password": "Password123",
            },
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Test Creator", resp.data)

        # Create campaign
        resp = self.client.post(
            "/campaigns/create",
            data={
                "title": "Community Library Solar Lights",
                "category": "Education",
                "short_summary": "Installing solar study lamps for evening library hours.",
                "description": (
                    "Our neighborhood community library serves 150 students every evening "
                    "but experiences frequent power outages. This project funds 20 solar "
                    "LED study stations with battery backup."
                ),
                "goal_amount": "4500",
                "duration_days": "45",
                "location": "Mysuru",
                "beneficiary_name": "Community Library Trust",
                "contact_phone": "9876543210",
            },
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Automated Risk Assessment", resp.data)

    def test_simulated_donation_updates_campaign(self):
        resp = self.client.post(
            "/campaigns/1/donate",
            data={
                "donor_name": "Unit Test Donor",
                "donor_email": "donor@example.com",
                "amount": "125",
                "payment_method": "Simulated Card",
                "message": "Keep up the great work!",
            },
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Simulated Payment Confirmed", resp.data)
        self.assertIn(b"$125.00", resp.data)

    def test_admin_login_and_fraud_monitoring(self):
        resp = self.client.post(
            "/login",
            data={"email": "admin@fundforward.edu", "password": "Admin@123"},
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Administrator Dashboard", resp.data)

        fraud_resp = self.client.get("/admin/fraud-monitoring")
        self.assertEqual(fraud_resp.status_code, 200)
        self.assertIn(b"ML Fraud Monitoring Center", fraud_resp.data)


if __name__ == "__main__":
    unittest.main()
