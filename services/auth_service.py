import re
from functools import wraps
from flask import flash, redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from models.user import create_user, get_user_by_email, get_user_by_id


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def register_user(full_name: str, email: str, password: str, confirm_password: str):
    full_name = (full_name or "").strip()
    email = (email or "").strip().lower()

    if len(full_name) < 2:
        return None, "Full name must be at least 2 characters."
    if not EMAIL_REGEX.match(email):
        return None, "Please enter a valid email address."
    if len(password or "") < 6:
        return None, "Password must be at least 6 characters long."
    if password != confirm_password:
        return None, "Passwords do not match."
    if get_user_by_email(email):
        return None, "An account with this email already exists."

    pw_hash = generate_password_hash(password)
    user_id = create_user(full_name, email, pw_hash, role="user")
    return user_id, None


def authenticate_user(email: str, password: str):
    email = (email or "").strip().lower()
    user = get_user_by_email(email)
    if not user:
        return None, "Invalid email or password."
    if not user["is_active"]:
        return None, "This account has been deactivated. Please contact an administrator."
    if not check_password_hash(user["password_hash"], password or ""):
        return None, "Invalid email or password."
    return user, None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        user = get_user_by_id(session["user_id"])
        if not user or not user["is_active"]:
            session.clear()
            flash("Your session is no longer valid.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Administrator login required.", "warning")
            return redirect(url_for("auth.login"))
        user = get_user_by_id(session["user_id"])
        if not user or user["role"] != "admin":
            flash("Access denied: Administrator privileges required.", "danger")
            return redirect(url_for("public.index"))
        return view(*args, **kwargs)

    return wrapped
