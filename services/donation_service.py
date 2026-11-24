import re
import uuid

from models.campaign import get_campaign_by_id, update_raised_amount
from models.donation import create_donation


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def process_simulated_donation(campaign_id: int, donor_user_id, form_data: dict):
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return None, "Campaign not found."
    if campaign["status"] not in ("approved", "active"):
        return None, "This campaign is not currently accepting donations."

    donor_name = (form_data.get("donor_name") or "").strip()
    donor_email = (form_data.get("donor_email") or "").strip().lower()
    message = (form_data.get("message") or "").strip()[:300]
    payment_method = (form_data.get("payment_method") or "Simulated Card").strip()

    if len(donor_name) < 2:
        return None, "Please enter your name (at least 2 characters)."
    if not EMAIL_REGEX.match(donor_email):
        return None, "Please enter a valid email address for the simulated receipt."

    try:
        amount = round(float(form_data.get("amount", 0)), 2)
    except (TypeError, ValueError):
        return None, "Please enter a valid donation amount."

    if amount < 1 or amount > 100000:
        return None, "Donation amount must be between $1 and $100,000."

    if payment_method not in ("Simulated Card", "Simulated UPI", "Simulated Bank Transfer"):
        payment_method = "Simulated Card"

    reference = f"FF-SIM-{uuid.uuid4().hex[:8].upper()}"

    create_donation(
        {
            "campaign_id": campaign_id,
            "donor_user_id": donor_user_id,
            "donor_name": donor_name,
            "donor_email": donor_email,
            "amount": amount,
            "message": message,
            "payment_method": payment_method,
            "payment_reference": reference,
        }
    )
    update_raised_amount(campaign_id, amount)
    return reference, None
