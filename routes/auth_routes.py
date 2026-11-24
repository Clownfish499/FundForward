from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.auth_service import authenticate_user, register_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("campaign.user_dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        user_id, error = register_user(full_name, email, password, confirm_password)
        if error:
            flash(error, "danger")
            return render_template("auth/register.html", full_name=full_name, email=email)

        session.permanent = True
        session["user_id"] = user_id
        session["user_name"] = full_name.strip()
        session["user_role"] = "user"
        flash("Account created successfully! Welcome to FundForward.", "success")
        return redirect(url_for("campaign.user_dashboard"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        if session.get("user_role") == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("campaign.user_dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        user, error = authenticate_user(email, password)
        if error:
            flash(error, "danger")
            return render_template("auth/login.html", email=email)

        session.permanent = True
        session["user_id"] = user["id"]
        session["user_name"] = user["full_name"]
        session["user_role"] = user["role"]
        flash(f"Welcome back, {user['full_name']}!", "success")

        if user["role"] == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("campaign.user_dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out safely.", "info")
    return redirect(url_for("public.index"))
