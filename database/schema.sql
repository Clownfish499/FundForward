PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    account_age_days INTEGER NOT NULL DEFAULT 1,
    previous_suspicious_count INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    short_summary TEXT NOT NULL,
    description TEXT NOT NULL,
    goal_amount REAL NOT NULL CHECK (goal_amount > 0),
    raised_amount REAL NOT NULL DEFAULT 0.0 CHECK (raised_amount >= 0),
    duration_days INTEGER NOT NULL CHECK (duration_days BETWEEN 5 AND 180),
    location TEXT NOT NULL DEFAULT '',
    beneficiary_name TEXT NOT NULL DEFAULT '',
    contact_phone TEXT NOT NULL DEFAULT '',
    image_filename TEXT DEFAULT '',
    document_filename TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending' CHECK (
        status IN ('pending', 'approved', 'rejected', 'active', 'completed', 'info_requested')
    ),
    is_featured INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    donor_user_id INTEGER,
    donor_name TEXT NOT NULL,
    donor_email TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    message TEXT DEFAULT '',
    payment_method TEXT NOT NULL DEFAULT 'Simulated Card',
    payment_reference TEXT NOT NULL UNIQUE,
    is_simulated INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (campaign_id) REFERENCES campaigns (id) ON DELETE CASCADE,
    FOREIGN KEY (donor_user_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS fraud_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL UNIQUE,
    risk_score REAL NOT NULL CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_category TEXT NOT NULL CHECK (risk_category IN ('Low Risk', 'Medium Risk', 'High Risk')),
    fraud_probability REAL NOT NULL CHECK (fraud_probability >= 0 AND fraud_probability <= 1),
    reasons_json TEXT NOT NULL,
    features_json TEXT NOT NULL,
    model_version TEXT NOT NULL DEFAULT 'RandomForest-v1',
    analyzed_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (campaign_id) REFERENCES campaigns (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS campaign_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    admin_id INTEGER NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('approved', 'rejected', 'info_requested', 'featured', 'unfeatured')),
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (campaign_id) REFERENCES campaigns (id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_category ON campaigns(category);
CREATE INDEX IF NOT EXISTS idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX IF NOT EXISTS idx_donations_campaign_id ON donations(campaign_id);
CREATE INDEX IF NOT EXISTS idx_fraud_risk_category ON fraud_analysis(risk_category);
