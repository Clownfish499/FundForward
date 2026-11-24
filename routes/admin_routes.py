import json
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from models.campaign import (
    get_campaign_by_id,
    get_category_breakdown,
    get_platform_stats,
    list_all_campaigns,
    update_campaign_status,
)
from models.donation import list_all_donations
from models.fraud import (
    create_review,
    get_risk_distribution,
    list_campaign_reviews,
    list_fraud_monitoring_campaigns,
)
from models.user import increment_suspicious_count, list_all_users, toggle_user_active
from services.auth_service import admin_required
from services.fraud_service import analyze_campaign_fraud, get_model_metrics

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@admin_required
def dashboard():
    stats = get_platform_stats()
    risk_dist = get_risk_distribution()
    category_breakdown = get_category_breakdown()
    pending_campaigns = list_all_campaigns(status_filter="pending")
    all_campaigns = list_all_campaigns()
    metrics = get_model_metrics()

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        risk_dist=risk_dist,
        category_breakdown=category_breakdown,
        pending_campaigns=pending_campaigns,
        all_campaigns=all_campaigns,
        metrics=metrics,
    )


@admin_bp.route("/fraud-monitoring")
@admin_required
def fraud_monitoring():
    risk_filter = request.args.get("risk", "").strip()
    campaigns = list_fraud_monitoring_campaigns(risk_filter=risk_filter)
    for c in campaigns:
        c["reasons"] = json.loads(c["reasons_json"]) if c.get("reasons_json") else []
    risk_dist = get_risk_distribution()
    metrics = get_model_metrics()
    return render_template(
        "admin/fraud_monitoring.html",
        campaigns=campaigns,
        risk_filter=risk_filter,
        risk_dist=risk_dist,
        metrics=metrics,
    )


@admin_bp.route("/campaigns/<int:campaign_id>")
@admin_required
def inspect_campaign(campaign_id):
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        abort(404)
    reasons = json.loads(campaign["reasons_json"]) if campaign.get("reasons_json") else []
    features = json.loads(campaign["features_json"]) if campaign.get("features_json") else {}
    reviews = list_campaign_reviews(campaign_id)
    return render_template(
        "admin/inspect_campaign.html",
        campaign=campaign,
        reasons=reasons,
        features=features,
        reviews=reviews,
    )


@admin_bp.route("/campaigns/<int:campaign_id>/action", methods=["POST"])
@admin_required
def campaign_action(campaign_id):
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        abort(404)

    action = request.form.get("action", "").strip()
    notes = request.form.get("notes", "").strip()
    admin_id = session["user_id"]

    if action == "approve":
        update_campaign_status(campaign_id, "active")
        create_review(campaign_id, admin_id, "approved", notes or "Approved by administrator.")
        flash(f"Campaign '{campaign['title']}' has been approved and is now active.", "success")
    elif action == "reject":
        update_campaign_status(campaign_id, "rejected")
        if campaign.get("risk_category") == "High Risk":
            increment_suspicious_count(campaign["user_id"])
        create_review(campaign_id, admin_id, "rejected", notes or "Rejected by administrator.")
        flash(f"Campaign '{campaign['title']}' has been rejected.", "warning")
    elif action == "request_info":
        update_campaign_status(campaign_id, "info_requested")
        create_review(
            campaign_id,
            admin_id,
            "info_requested",
            notes or "Additional verification documents requested.",
        )
        flash(f"Requested additional information for '{campaign['title']}'.", "info")
    elif action == "rerun_ml":
        result = analyze_campaign_fraud(campaign_id)
        flash(
            f"ML Fraud Analysis updated: {result['risk_category']} ({result['risk_score']}/100).",
            "success",
        )
    else:
        flash("Invalid administrative action.", "danger")

    return redirect(url_for("admin.inspect_campaign", campaign_id=campaign_id))


@admin_bp.route("/users")
@admin_required
def users():
    all_users = list_all_users()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@admin_required
def toggle_user(user_id):
    toggle_user_active(user_id)
    flash("User account status updated.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/donations")
@admin_required
def donations():
    all_donations = list_all_donations()
    return render_template("admin/donations.html", donations=all_donations)
