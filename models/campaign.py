from database.db import get_db_connection


def create_campaign(data: dict, db_path=None) -> int:
    conn = get_db_connection(db_path)
    try:
        cur = conn.execute(
            """
            INSERT INTO campaigns (
                user_id, title, category, short_summary, description, goal_amount,
                raised_amount, duration_days, location, beneficiary_name, contact_phone,
                image_filename, document_filename, status, is_featured
            ) VALUES (?, ?, ?, ?, ?, ?, 0.0, ?, ?, ?, ?, ?, ?, 'pending', 0)
            """,
            (
                data["user_id"],
                data["title"],
                data["category"],
                data["short_summary"],
                data["description"],
                float(data["goal_amount"]),
                int(data["duration_days"]),
                data.get("location", ""),
                data.get("beneficiary_name", ""),
                data.get("contact_phone", ""),
                data.get("image_filename", ""),
                data.get("document_filename", ""),
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_campaign_by_id(campaign_id: int, db_path=None):
    conn = get_db_connection(db_path)
    try:
        row = conn.execute(
            """
            SELECT c.*, u.full_name AS creator_name, u.email AS creator_email,
                   u.account_age_days AS creator_account_age_days,
                   u.previous_suspicious_count AS creator_suspicious_count,
                   fa.risk_score, fa.risk_category, fa.fraud_probability,
                   fa.reasons_json, fa.features_json, fa.analyzed_at,
                   (SELECT notes FROM campaign_reviews WHERE campaign_id = c.id AND action = 'info_requested' ORDER BY created_at DESC LIMIT 1) AS admin_review_note
            FROM campaigns c
            JOIN users u ON u.id = c.user_id
            LEFT JOIN fraud_analysis fa ON fa.campaign_id = c.id
            WHERE c.id = ?
            """,
            (campaign_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_public_campaigns(search: str = "", category: str = "", sort: str = "newest", db_path=None):
    conn = get_db_connection(db_path)
    try:
        query = """
            SELECT c.*, u.full_name AS creator_name,
                   COUNT(d.id) AS donor_count
            FROM campaigns c
            JOIN users u ON u.id = c.user_id
            LEFT JOIN donations d ON d.campaign_id = c.id
            WHERE c.status IN ('approved', 'active', 'completed')
        """
        params = []
        if search:
            query += " AND (LOWER(c.title) LIKE ? OR LOWER(c.short_summary) LIKE ? OR LOWER(c.description) LIKE ?)"
            like_q = f"%{search.lower().strip()}%"
            params.extend([like_q, like_q, like_q])
        if category:
            query += " AND c.category = ?"
            params.append(category)

        query += " GROUP BY c.id"

        if sort == "most_funded":
            query += " ORDER BY c.raised_amount DESC"
        elif sort == "goal_low":
            query += " ORDER BY c.goal_amount ASC"
        else:
            query += " ORDER BY c.is_featured DESC, c.created_at DESC"

        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_featured_campaigns(limit: int = 3, db_path=None):
    conn = get_db_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT c.*, u.full_name AS creator_name, COUNT(d.id) AS donor_count
            FROM campaigns c
            JOIN users u ON u.id = c.user_id
            LEFT JOIN donations d ON d.campaign_id = c.id
            WHERE c.status IN ('approved', 'active', 'completed')
            GROUP BY c.id
            ORDER BY c.is_featured DESC, c.raised_amount DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_user_campaigns(user_id: int, db_path=None):
    conn = get_db_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT c.*, fa.risk_score, fa.risk_category, fa.reasons_json
            FROM campaigns c
            LEFT JOIN fraud_analysis fa ON fa.campaign_id = c.id
            WHERE c.user_id = ?
            ORDER BY c.created_at DESC
            """,
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_all_campaigns(status_filter: str = "", db_path=None):
    conn = get_db_connection(db_path)
    try:
        query = """
            SELECT c.*, u.full_name AS creator_name, u.email AS creator_email,
                   fa.risk_score, fa.risk_category
            FROM campaigns c
            JOIN users u ON u.id = c.user_id
            LEFT JOIN fraud_analysis fa ON fa.campaign_id = c.id
        """
        params = []
        if status_filter:
            query += " WHERE c.status = ?"
            params.append(status_filter)
        query += " ORDER BY c.created_at DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_campaign_status(campaign_id: int, status: str, db_path=None):
    conn = get_db_connection(db_path)
    try:
        conn.execute(
            "UPDATE campaigns SET status = ?, updated_at = datetime('now') WHERE id = ?",
            (status, campaign_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_raised_amount(campaign_id: int, amount: float, db_path=None):
    conn = get_db_connection(db_path)
    try:
        conn.execute(
            """
            UPDATE campaigns
            SET raised_amount = raised_amount + ?,
                status = CASE
                    WHEN (raised_amount + ?) >= goal_amount AND status IN ('approved', 'active') THEN 'completed'
                    ELSE status
                END,
                updated_at = datetime('now')
            WHERE id = ?
            """,
            (amount, amount, campaign_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_platform_stats(db_path=None) -> dict:
    conn = get_db_connection(db_path)
    try:
        users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        campaigns_count = conn.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0]
        donations_count = conn.execute("SELECT COUNT(*) FROM donations").fetchone()[0]
        total_collected = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM donations").fetchone()[0]
        pending_count = conn.execute("SELECT COUNT(*) FROM campaigns WHERE status IN ('pending', 'info_requested')").fetchone()[0]
        approved_count = conn.execute("SELECT COUNT(*) FROM campaigns WHERE status IN ('approved', 'active', 'completed')").fetchone()[0]
        rejected_count = conn.execute("SELECT COUNT(*) FROM campaigns WHERE status = 'rejected'").fetchone()[0]
        return {
            "total_users": users_count,
            "total_campaigns": campaigns_count,
            "total_donations": donations_count,
            "total_collected": round(float(total_collected), 2),
            "pending_campaigns": pending_count,
            "approved_campaigns": approved_count,
            "rejected_campaigns": rejected_count,
        }
    finally:
        conn.close()


def get_category_breakdown(db_path=None):
    conn = get_db_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT category, COUNT(*) AS count, COALESCE(SUM(raised_amount), 0) AS total_raised
            FROM campaigns
            GROUP BY category
            ORDER BY count DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_campaign(campaign_id: int, data: dict, db_path=None):
    conn = get_db_connection(db_path)
    try:
        fields = [
            "title = ?", "category = ?", "short_summary = ?",
            "description = ?", "goal_amount = ?", "duration_days = ?",
            "location = ?", "beneficiary_name = ?", "contact_phone = ?",
            "status = 'pending'", "updated_at = datetime('now')"
        ]
        params = [
            data["title"], data["category"], data["short_summary"],
            data["description"], float(data["goal_amount"]), int(data["duration_days"]),
            data.get("location", ""), data.get("beneficiary_name", ""), data.get("contact_phone", "")
        ]
        if data.get("image_filename") is not None:
            fields.append("image_filename = ?")
            params.append(data["image_filename"])
        if data.get("document_filename") is not None:
            fields.append("document_filename = ?")
            params.append(data["document_filename"])

        params.append(campaign_id)
        sql = f"UPDATE campaigns SET {', '.join(fields)} WHERE id = ?"
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()
