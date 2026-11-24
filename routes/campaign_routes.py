from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from config import Config
from models.campaign import list_user_campaigns, get_campaign_by_id
from models.donation import list_user_donations
from services.auth_service import login_required
from services.campaign_service import validate_and_create_campaign, validate_and_update_campaign
from services.fraud_service import analyze_campaign_fraud

campaign_bp = Blueprint("campaign", __name__)


@campaign_bp.route("/dashboard")
@login_required
def user_dashboard():
    user_id = session["user_id"]
    my_campaigns = list_user_campaigns(user_id)
    my_donations = list_user_donations(user_id)
    return render_template(
        "dashboard/user_dashboard.html",
        campaigns=my_campaigns,
        donations=my_donations,
    )


@campaign_bp.route("/campaigns/create", methods=["GET", "POST"])
@login_required
def create_campaign_view():
    if request.method == "POST":
        campaign_id, error = validate_and_create_campaign(
            user_id=session["user_id"],
            form_data=request.form,
            files=request.files,
        )
        if error:
            flash(error, "danger")
            return render_template(
                "dashboard/create_campaign.html",
                categories=Config.CATEGORIES,
                form_data=request.form,
            )

        # Run ML Fraud Detection immediately on submission
        analysis = analyze_campaign_fraud(campaign_id)
        flash(
            f"Campaign submitted for review! Automated Risk Assessment: "
            f"{analysis['risk_category']} ({analysis['risk_score']}/100).",
            "success",
        )
        return redirect(url_for("campaign.user_dashboard"))

    return render_template(
        "dashboard/create_campaign.html",
        categories=Config.CATEGORIES,
        form_data={},
    )


@campaign_bp.route("/campaign/<int:campaign_id>/edit", methods=["GET", "POST"])
@campaign_bp.route("/campaigns/<int:campaign_id>/edit", methods=["GET", "POST"])
@login_required
def edit_campaign_view(campaign_id: int):
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        abort(404)

    if campaign["user_id"] != session.get("user_id"):
        flash("You are not authorized to edit this campaign.", "danger")
        return redirect(url_for("campaign.user_dashboard"))

    if campaign["status"] != "info_requested":
        flash('Only campaigns with "Info Requested" status can be edited.', "warning")
        return redirect(url_for("public.campaign_detail", campaign_id=campaign_id))

    if request.method == "POST":
        err = validate_and_update_campaign(
            campaign_id=campaign_id,
            user_id=session["user_id"],
            form_data=request.form,
            files=request.files,
        )
        if err:
            flash(err, "danger")
            return render_template(
                "dashboard/edit_campaign.html",
                campaign=campaign,
                categories=Config.CATEGORIES,
                form_data=request.form,
            )

        # Rerun ML Fraud Risk Analysis on resubmission
        try:
            analysis = analyze_campaign_fraud(campaign_id)
            flash(
                f"Campaign updated and resubmitted for admin review! Automated Risk Assessment: "
                f"{analysis['risk_category']} ({analysis['risk_score']}/100).",
                "success",
            )
        except Exception as e:
            flash("Campaign updated and resubmitted for admin review!", "success")

        return redirect(url_for("campaign.user_dashboard"))

    return render_template(
        "dashboard/edit_campaign.html",
        campaign=campaign,
        categories=Config.CATEGORIES,
        form_data=campaign,
    )
