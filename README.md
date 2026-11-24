# FundForward — Crowdfunding Platform with ML Fraud Detection

FundForward is a full-stack academic software engineering project built with **Python Flask**, **SQLite**, **Scikit-learn**, **Pandas**, **NumPy**, and **Chart.js**. It demonstrates how a modern crowdfunding platform can integrate an interpretable Machine Learning fraud risk engine directly into campaign submission and administrator review workflows.

## Key Features
- **Public Crowdfunding Portal**: Hero landing page, featured campaigns, category browsing, search & filtering, About, and How It Works pages.
- **Authentication & RBAC**: Secure registration/login with `werkzeug.security` password hashing, HTTP-only sessions, and User/Admin role-based access control.
- **Campaign Management**: Create campaigns with image/document uploads (5 MB limit, extension validation), progress tracking, and creator dashboards.
- **Simulated Donations**: Preset and custom donation amounts, optional donor messages, automatic campaign progress updates, and simulated payment receipts (no real money is transferred).
- **ML Fraud Detection (`Scikit-learn` Random Forest)**:
  - Synthetic dataset (`ml/dataset.csv`, 1,200 records) with 9 engineered features (`goal_amount`, `description_length`, `document_available`, `creator_account_age_days`, `completeness_score`, `previous_suspicious_count`, `duration_days`, `donation_velocity_anomaly`, `urgent_keyword_ratio`).
  - Outputs a **0–100 Risk Score**, classification (**0–30 Low Risk**, **31–60 Medium Risk**, **61–100 High Risk**), and explainable human-readable reasons.
- **Admin & Fraud Monitoring Dashboards**: KPI cards, Chart.js visualizations, filterable suspicious campaign queue, deep campaign inspection, and Approve / Reject / Request Additional Info workflows.

## Installation (Windows)
```powershell
cd fundforward
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Train the ML Model & Initialize Database
```powershell
python ml\generate_dataset.py
python ml\train_model.py
python init_db.py
```

## Run the Application
```powershell
python app.py
```
Open `http://127.0.0.1:5000` in your browser.

## Demonstration Login Credentials
- **Administrator**: `admin@fundforward.edu` / `Admin@123`
- **Standard User**: `priya@example.com` / `User@123`
- **Flagged/New User**: `vikram@example.com` / `User@123`

## Automated Tests
```powershell
pytest -v
```
Or using Python's built-in `unittest`:
```powershell
python -m unittest discover -s tests -v
```

## Disclosures & Known Limitations
- **Synthetic Training Data**: The Random Forest model is trained on synthetic demonstration data (`ml/dataset.csv`). Risk scores and thresholds (0–30 / 31–60 / 61–100) are academic demonstration indicators and **do not constitute proof of fraud**.
- **Simulated Payments**: All donations are simulated and recorded in SQLite without real payment gateway integration.
- **Local Storage**: Uploaded files and SQLite database are stored locally for academic demonstration.
