from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from models.campaign import get_campaign_by_id
from models.donation import get_donation_by_reference
from services.donation_service import process_simulated_donation
from services.fraud_service import analyze_campaign_fraud

donation_bp = Blueprint("donation", __name__)


@donation_bp.route("/campaigns/<int:campaign_id>/donate", methods=["GET", "POST"])
def donate(campaign_id):
    campaign = get_campaign_by_id(campaign_id)
    if not campaign or campaign["status"] not in ("approved", "active"):
        abort(404)

    if request.method == "POST":
        donor_user_id = session.get("user_id")
        reference, error = process_simulated_donation(
            campaign_id=campaign_id,
            donor_user_id=donor_user_id,
            form_data=request.form,
        )
        if error:
            flash(error, "danger")
            return render_template(
                "donations/donate.html",
                campaign=campaign,
                form_data=request.form,
            )

        # Re-evaluate campaign fraud risk with updated donation patterns
        try:
            analyze_campaign_fraud(campaign_id)
        except Exception:
            pass

        flash("Simulated donation completed successfully! No real money was transferred.", "success")
        return redirect(url_for("donation.confirmation", reference=reference))

    return render_template("donations/donate.html", campaign=campaign, form_data={})


@donation_bp.route("/donations/confirmation/<reference>")
def confirmation(reference):
    donation = get_donation_by_reference(reference)
    if not donation:
        abort(404)
    return render_template("donations/confirmation.html", donation=donation)
