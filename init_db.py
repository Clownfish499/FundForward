"""
Database Initialization & Demonstration Seeder for FundForward.

Creates all SQLite tables and populates realistic demonstration users,
campaigns, donations, fraud analysis records, and admin reviews.
"""

import json
import os
import sys
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import Config
from database.db import get_db_connection, init_schema


def seed_database(db_path=None):
    init_schema(db_path)
    conn = get_db_connection(db_path)
    try:
        existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if existing > 0:
            print("Database already initialized with users. Skipping seed.")
            return

        # 1. Seed Users (1 Admin, 4 Regular Users)
        users_data = [
            (
                "Aarav Mehta (Admin)",
                "admin@fundforward.edu",
                generate_password_hash("Admin@123"),
                "admin",
                540,
                0,
            ),
            (
                "Priya Sharma",
                "priya@example.com",
                generate_password_hash("User@123"),
                "user",
                365,
                0,
            ),
            (
                "Rohan Kulkarni",
                "rohan@example.com",
                generate_password_hash("User@123"),
                "user",
                180,
                0,
            ),
            (
                "Vikram Nair",
                "vikram@example.com",
                generate_password_hash("User@123"),
                "user",
                12,
                1,
            ),
            (
                "Elena Vance",
                "elena@example.com",
                generate_password_hash("User@123"),
                "user",
                420,
                0,
            ),
        ]

        conn.executemany(
            """
            INSERT INTO users (full_name, email, password_hash, role, account_age_days, previous_suspicious_count)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            users_data,
        )

        # 2. Seed Campaigns (Active, Pending, Completed, Rejected)
        campaigns_data = [
            (
                2,
                "Rural Clinic Solar Microgrid Initiative",
                "Environment & Sustainability",
                "Providing reliable 24/7 solar electricity to three rural primary health clinics.",
                (
                    "Access to uninterrupted electricity is critical for vaccine refrigeration, "
                    "maternal care, and emergency lighting in rural clinics. Our engineering team "
                    "has partnered with local health authorities to install 15kW solar microgrids "
                    "with lithium-iron-phosphate battery storage across three community clinics. "
                    "Funds cover solar panels, inverters, certified installation, and 3-year local "
                    "technician maintenance training."
                ),
                12000.0,
                8450.0,
                45,
                "Mysuru, Karnataka",
                "Rural Health Trust",
                "+91-98450-11223",
                "",
                "clinic_microgrid_proposal.pdf",
                "active",
                1,
            ),
            (
                3,
                "OpenSTEM Robotics Kits for Public Schools",
                "Education",
                "Equipping 10 underserved high schools with hands-on robotics and coding kits.",
                (
                    "Many public high school students have strong interest in engineering but lack "
                    "access to hardware lab equipment. OpenSTEM builds modular microcontroller and "
                    "sensor kits paired with an open-source curriculum. Each $450 kit serves a "
                    "classroom team of 5 students for an entire academic year. All components are "
                    "sourced transparently with itemized vendor quotes attached."
                ),
                9000.0,
                5200.0,
                60,
                "Pune, Maharashtra",
                "OpenSTEM Education Foundation",
                "+91-98220-44556",
                "",
                "openstem_budget_breakdown.pdf",
                "active",
                1,
            ),
            (
                5,
                "Pediatric Cardiac Surgery Support for Baby Ananya",
                "Medical & Health",
                "Helping cover hospital surgery and post-operative ICU care expenses.",
                (
                    "Ananya is a 14-month-old diagnosed with a congenital ventricular septal defect "
                    "requiring corrective pediatric cardiac surgery. Her family has exhausted personal "
                    "savings and partial insurance coverage. Hospital cost estimates and attending "
                    "cardiologist verification letters have been submitted for platform review. "
                    "Every contribution goes directly toward surgical consumables and ICU recovery."
                ),
                15000.0,
                15000.0,
                30,
                "Bengaluru, Karnataka",
                "Ananya Family Medical Fund",
                "+91-99001-77889",
                "",
                "hospital_estimate_letter.pdf",
                "completed",
                1,
            ),
            (
                4,
                "URGENT Guaranteed 300% Return AI Crypto Relief",
                "Technology & Innovation",
                "Send immediately to double your impact in 48 hours.",
                "Urgent wire needed now. Guaranteed miracle returns and secret project.",
                95000.0,
                1200.0,
                7,
                "",
                "",
                "",
                "",
                "",
                "pending",
                0,
            ),
            (
                2,
                "Neighborhood Urban Tree Canopy & Rain Gardens",
                "Community & Social",
                "Planting 400 native shade trees and building stormwater rain gardens.",
                (
                    "Urban heat islands and seasonal street flooding affect our neighborhood every "
                    "summer and monsoon. Working with local arborists and municipal volunteers, "
                    "we will plant 400 native saplings with protective tree guards and construct "
                    "six bioswale rain gardens along school routes. Quarterly progress photos and "
                    "nursery receipts will be published to all donors."
                ),
                6500.0,
                1950.0,
                50,
                "Chennai, Tamil Nadu",
                "GreenWardens Collective",
                "+91-98400-33445",
                "",
                "arborist_site_plan.pdf",
                "pending",
                0,
            ),
            (
                4,
                "Emergency Relief Fund — Act Now",
                "Emergency Relief",
                "Immediate funds required.",
                "Need money fast for emergency. No documents right now.",
                50000.0,
                0.0,
                10,
                "",
                "",
                "",
                "",
                "",
                "rejected",
                0,
            ),
        ]

        conn.executemany(
            """
            INSERT INTO campaigns (
                user_id, title, category, short_summary, description, goal_amount,
                raised_amount, duration_days, location, beneficiary_name, contact_phone,
                image_filename, document_filename, status, is_featured
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            campaigns_data,
        )

        # 3. Seed Donations
        donations_data = [
            (1, 3, "Rohan Kulkarni", "rohan@example.com", 250.0, "Great initiative for rural healthcare!", "Simulated Card", "FF-SIM-100001"),
            (1, 5, "Elena Vance", "elena@example.com", 500.0, "Clean energy saves lives.", "Simulated UPI", "FF-SIM-100002"),
            (1, None, "Anonymous Supporter", "supporter1@example.com", 7700.0, "Matching grant for microgrid hardware.", "Simulated Bank Transfer", "FF-SIM-100003"),
            (2, 2, "Priya Sharma", "priya@example.com", 450.0, "Sponsoring one full classroom kit!", "Simulated Card", "FF-SIM-100004"),
            (2, None, "Tech Alumni Group", "alumni@example.com", 4750.0, "Empowering public school students.", "Simulated Bank Transfer", "FF-SIM-100005"),
            (3, 2, "Priya Sharma", "priya@example.com", 1000.0, "Wishing Ananya a speedy recovery.", "Simulated Card", "FF-SIM-100006"),
            (3, None, "Community Donors", "donors@example.com", 14000.0, "Full surgical goal reached!", "Simulated Bank Transfer", "FF-SIM-100007"),
            (5, 3, "Rohan Kulkarni", "rohan@example.com", 150.0, "Looking forward to greener streets.", "Simulated UPI", "FF-SIM-100008"),
            (5, None, "Meera Krishnan", "meera@example.com", 1800.0, "Support for local rain gardens.", "Simulated Card", "FF-SIM-100009"),
            (4, None, "Test Donor", "testdonor@example.com", 1200.0, "Early transfer", "Simulated Card", "FF-SIM-100010"),
        ]

        conn.executemany(
            """
            INSERT INTO donations (
                campaign_id, donor_user_id, donor_name, donor_email, amount,
                message, payment_method, payment_reference
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            donations_data,
        )

        # 4. Seed Fraud Analysis Records (consistent with ML risk categories)
        fraud_records = [
            (
                1,
                14.2,
                "Low Risk",
                0.142,
                json.dumps([
                    "Supporting verification document provided",
                    "Creator account established (365 days)",
                    "High campaign information completeness (83%)",
                ]),
                json.dumps({"goal_amount": 12000, "description_length": 442, "document_available": 1}),
            ),
            (
                2,
                16.8,
                "Low Risk",
                0.168,
                json.dumps([
                    "Supporting verification document provided",
                    "Detailed campaign description (398 chars)",
                    "Reasonable fundraising target ($9,000)",
                ]),
                json.dumps({"goal_amount": 9000, "description_length": 398, "document_available": 1}),
            ),
            (
                3,
                12.5,
                "Low Risk",
                0.125,
                json.dumps([
                    "Supporting verification document provided",
                    "Creator account established (420 days)",
                    "No prior suspicious activity on account",
                ]),
                json.dumps({"goal_amount": 15000, "description_length": 412, "document_available": 1}),
            ),
            (
                4,
                88.4,
                "High Risk",
                0.884,
                json.dumps([
                    "High fundraising goal ($95,000) with minimal narrative (71 chars)",
                    "No supporting verification document uploaded",
                    "New creator account (12 days old) with 1 prior flag",
                    "High-urgency / promotional phrasing detected",
                ]),
                json.dumps({"goal_amount": 95000, "description_length": 71, "document_available": 0}),
            ),
            (
                5,
                19.4,
                "Low Risk",
                0.194,
                json.dumps([
                    "Supporting verification document provided",
                    "High campaign information completeness (83%)",
                    "Established creator account (365 days)",
                ]),
                json.dumps({"goal_amount": 6500, "description_length": 415, "document_available": 1}),
            ),
            (
                6,
                82.7,
                "High Risk",
                0.827,
                json.dumps([
                    "No supporting verification document uploaded",
                    "Very short campaign description (53 chars)",
                    "New creator account (12 days old) with prior suspicious flag",
                    "Low campaign information completeness (33%)",
                ]),
                json.dumps({"goal_amount": 50000, "description_length": 53, "document_available": 0}),
            ),
        ]

        conn.executemany(
            """
            INSERT INTO fraud_analysis (
                campaign_id, risk_score, risk_category, fraud_probability,
                reasons_json, features_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            fraud_records,
        )

        # 5. Seed Admin Reviews
        reviews_data = [
            (1, 1, "approved", "Verified clinic partnership document and budget."),
            (2, 1, "approved", "OpenSTEM vendor quotes and curriculum verified."),
            (3, 1, "approved", "Hospital estimate letter confirmed."),
            (6, 1, "rejected", "Insufficient documentation and unverifiable emergency claim."),
        ]
        conn.executemany(
            """
            INSERT INTO campaign_reviews (campaign_id, admin_id, action, notes)
            VALUES (?, ?, ?, ?)
            """,
            reviews_data,
        )

        conn.commit()
        print("FundForward SQLite database initialized and seeded successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    seed_database(Config.DATABASE_PATH)
