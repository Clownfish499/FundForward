from database.db import get_db_connection


def create_user(full_name: str, email: str, password_hash: str, role: str = "user", db_path=None) -> int:
    conn = get_db_connection(db_path)
    try:
        cur = conn.execute(
            """
            INSERT INTO users (full_name, email, password_hash, role, account_age_days, previous_suspicious_count)
            VALUES (?, ?, ?, ?, 1, 0)
            """,
            (full_name, email.lower().strip(), password_hash, role),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_user_by_email(email: str, db_path=None):
    conn = get_db_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.lower().strip(),)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: int, db_path=None):
    conn = get_db_connection(db_path)
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_all_users(db_path=None):
    conn = get_db_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT u.id, u.full_name, u.email, u.role, u.account_age_days,
                   u.previous_suspicious_count, u.is_active, u.created_at,
                   COUNT(c.id) AS campaign_count
            FROM users u
            LEFT JOIN campaigns c ON c.user_id = u.id
            GROUP BY u.id
            ORDER BY u.created_at DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def toggle_user_active(user_id: int, db_path=None):
    conn = get_db_connection(db_path)
    try:
        conn.execute(
            "UPDATE users SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ? AND role != 'admin'",
            (user_id,),
        )
        conn.commit()
    finally:
        conn.close()


def increment_suspicious_count(user_id: int, db_path=None):
    conn = get_db_connection(db_path)
    try:
        conn.execute(
            "UPDATE users SET previous_suspicious_count = previous_suspicious_count + 1 WHERE id = ?",
            (user_id,),
        )
        conn.commit()
    finally:
        conn.close()
