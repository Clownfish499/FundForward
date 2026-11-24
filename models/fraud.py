from database.db import get_db_connection


def upsert_fraud_analysis(
    campaign_id: int,
    risk_score: float,
    risk_category: str,
    fraud_probability: float,
    reasons_json: str,
    features_json: str,
    model_version: str = "RandomForest-v1",
    db_path=None,
):
    conn = get_db_connection(db_path)
    try:
        conn.execute(
            """
            INSERT INTO fraud_analysis (
                campaign_id, risk_score, risk_category, fraud_probability,
                reasons_json, features_json, model_version, analyzed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(campaign_id) DO UPDATE SET
                risk_score = excluded.risk_score,
                risk_category = excluded.risk_category,
                fraud_probability = excluded.fraud_probability,
                reasons_json = excluded.reasons_json,
                features_json = excluded.features_json,
                model_version = excluded.model_version,
                analyzed_at = datetime('now')
            """,
            (
                campaign_id,
                risk_score,
                risk_category,
                fraud_probability,
                reasons_json,
                features_json,
                model_version,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def list_fraud_monitoring_campaigns(risk_filter: str = "", db_path=None):
    conn = get_db_connection(db_path)
    try:
        query = """
            SELECT c.id, c.title, c.category, c.goal_amount, c.raised_amount,
                   c.status, c.document_filename, c.created_at,
                   u.full_name AS creator_name, u.email AS creator_email,
                   u.account_age_days, u.previous_suspicious_count,
                   fa.risk_score, fa.risk_category, fa.fraud_probability,
                   fa.reasons_json, fa.analyzed_at
            FROM campaigns c
            JOIN users u ON u.id = c.user_id
            LEFT JOIN fraud_analysis fa ON fa.campaign_id = c.id
        """
        params = []
        if risk_filter:
            query += " WHERE fa.risk_category = ?"
            params.append(risk_filter)
        query += " ORDER BY COALESCE(fa.risk_score, 0) DESC, c.created_at DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_risk_distribution(db_path=None) -> dict:
    conn = get_db_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT risk_category, COUNT(*) AS count
            FROM fraud_analysis
            GROUP BY risk_category
            """
        ).fetchall()
        dist = {"Low Risk": 0, "Medium Risk": 0, "High Risk": 0}
        for r in rows:
            dist[r["risk_category"]] = r["count"]
        return dist
    finally:
        conn.close()


def create_review(campaign_id: int, admin_id: int, action: str, notes: str, db_path=None):
    conn = get_db_connection(db_path)
    try:
        conn.execute(
            """
            INSERT INTO campaign_reviews (campaign_id, admin_id, action, notes)
            VALUES (?, ?, ?, ?)
            """,
            (campaign_id, admin_id, action, notes),
        )
        conn.commit()
    finally:
        conn.close()


def list_campaign_reviews(campaign_id: int, db_path=None):
    conn = get_db_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT cr.*, u.full_name AS admin_name
            FROM campaign_reviews cr
            JOIN users u ON u.id = cr.admin_id
            WHERE cr.campaign_id = ?
            ORDER BY cr.created_at DESC
            """,
            (campaign_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
