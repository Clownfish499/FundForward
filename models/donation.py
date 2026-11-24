from database.db import get_db_connection


def create_donation(data: dict, db_path=None) -> int:
    conn = get_db_connection(db_path)
    try:
        cur = conn.execute(
            """
            INSERT INTO donations (
                campaign_id, donor_user_id, donor_name, donor_email,
                amount, message, payment_method, payment_reference, is_simulated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                data["campaign_id"],
                data.get("donor_user_id"),
                data["donor_name"],
                data["donor_email"],
                float(data["amount"]),
                data.get("message", ""),
                data.get("payment_method", "Simulated Card"),
                data["payment_reference"],
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_donation_by_reference(reference: str, db_path=None):
    conn = get_db_connection(db_path)
    try:
        row = conn.execute(
            """
            SELECT d.*, c.title AS campaign_title, c.category AS campaign_category
            FROM donations d
            JOIN campaigns c ON c.id = d.campaign_id
            WHERE d.payment_reference = ?
            """,
            (reference,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_campaign_donations(campaign_id: int, db_path=None):
    conn = get_db_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT * FROM donations
            WHERE campaign_id = ?
            ORDER BY created_at DESC
            """,
            (campaign_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_user_donations(user_id: int, db_path=None):
    conn = get_db_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT d.*, c.title AS campaign_title
            FROM donations d
            JOIN campaigns c ON c.id = d.campaign_id
            WHERE d.donor_user_id = ?
            ORDER BY d.created_at DESC
            """,
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_all_donations(db_path=None):
    conn = get_db_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT d.*, c.title AS campaign_title
            FROM donations d
            JOIN campaigns c ON c.id = d.campaign_id
            ORDER BY d.created_at DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
