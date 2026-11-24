import os
import uuid
from werkzeug.utils import secure_filename

from config import Config
from models.campaign import create_campaign, get_campaign_by_id, update_campaign


def _allowed_file(filename: str, allowed_extensions: set) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def save_uploaded_file(file_storage, target_folder: str, allowed_extensions: set):
    """Validate and save an uploaded file with a UUID prefix to prevent collisions."""
    if not file_storage or not file_storage.filename:
        return "", None
    original = secure_filename(file_storage.filename)
    if not original or not _allowed_file(original, allowed_extensions):
        allowed_str = ", ".join(sorted(allowed_extensions))
        return None, f"Unsupported file type '{file_storage.filename}'. Allowed: {allowed_str}"

    os.makedirs(target_folder, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex[:12]}_{original}"
    file_storage.save(os.path.join(target_folder, unique_name))
    return unique_name, None


def validate_and_create_campaign(user_id: int, form_data: dict, files: dict):
    title = (form_data.get("title") or "").strip()
    category = (form_data.get("category") or "").strip()
    short_summary = (form_data.get("short_summary") or "").strip()
    description = (form_data.get("description") or "").strip()
    location = (form_data.get("location") or "").strip()
    beneficiary_name = (form_data.get("beneficiary_name") or "").strip()
    contact_phone = (form_data.get("contact_phone") or "").strip()

    if len(title) < 5 or len(title) > 140:
        return None, "Campaign title must be between 5 and 140 characters."
    if category not in Config.CATEGORIES:
        return None, "Please select a valid campaign category."
    if len(short_summary) < 10 or len(short_summary) > 250:
        return None, "Short summary must be between 10 and 250 characters."
    if len(description) < 30:
        return None, "Campaign description must be at least 30 characters."

    try:
        goal_amount = float(form_data.get("goal_amount", 0))
    except (TypeError, ValueError):
        return None, "Fundraising goal must be a valid number."
    if goal_amount < 50 or goal_amount > 1000000:
        return None, "Fundraising goal must be between $50 and $1,000,000."

    try:
        duration_days = int(form_data.get("duration_days", 30))
    except (TypeError, ValueError):
        return None, "Duration must be a whole number of days."
    if duration_days < 5 or duration_days > 180:
        return None, "Campaign duration must be between 5 and 180 days."

    image_filename, img_err = save_uploaded_file(
        files.get("image"), Config.CAMPAIGN_IMAGE_FOLDER, Config.ALLOWED_IMAGE_EXTENSIONS
    )
    if img_err:
        return None, img_err

    doc_filename, doc_err = save_uploaded_file(
        files.get("document"), Config.DOCUMENT_FOLDER, Config.ALLOWED_DOCUMENT_EXTENSIONS
    )
    if doc_err:
        return None, doc_err

    campaign_id = create_campaign(
        {
            "user_id": user_id,
            "title": title,
            "category": category,
            "short_summary": short_summary,
            "description": description,
            "goal_amount": goal_amount,
            "duration_days": duration_days,
            "location": location,
            "beneficiary_name": beneficiary_name,
            "contact_phone": contact_phone,
            "image_filename": image_filename,
            "document_filename": doc_filename,
        }
    )
    return campaign_id, None


def user_owns_campaign(campaign_id: int, user_id: int, user_role: str = "user") -> bool:
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return False
    return user_role == "admin" or campaign["user_id"] == user_id


def validate_and_update_campaign(campaign_id: int, user_id: int, form_data: dict, files: dict):
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return "Campaign not found."
    if campaign["user_id"] != user_id:
        return "Unauthorized."

    title = (form_data.get("title") or "").strip()
    category = (form_data.get("category") or "").strip()
    short_summary = (form_data.get("short_summary") or "").strip()
    description = (form_data.get("description") or "").strip()
    location = (form_data.get("location") or "").strip()
    beneficiary_name = (form_data.get("beneficiary_name") or "").strip()
    contact_phone = (form_data.get("contact_phone") or "").strip()

    if len(title) < 5 or len(title) > 140:
        return "Campaign title must be between 5 and 140 characters."
    if category not in Config.CATEGORIES:
        return "Please select a valid campaign category."
    if len(short_summary) < 10 or len(short_summary) > 250:
        return "Short summary must be between 10 and 250 characters."
    if len(description) < 30:
        return "Campaign description must be at least 30 characters."

    try:
        goal_amount = float(form_data.get("goal_amount", 0))
    except (TypeError, ValueError):
        return "Fundraising goal must be a valid number."
    if goal_amount < 50 or goal_amount > 1000000:
        return "Fundraising goal must be between $50 and $1,000,000."

    try:
        duration_days = int(form_data.get("duration_days", 30))
    except (TypeError, ValueError):
        return "Duration must be a whole number of days."
    if duration_days < 5 or duration_days > 180:
        return "Campaign duration must be between 5 and 180 days."

    update_data = {
        "title": title,
        "category": category,
        "short_summary": short_summary,
        "description": description,
        "goal_amount": goal_amount,
        "duration_days": duration_days,
        "location": location,
        "beneficiary_name": beneficiary_name,
        "contact_phone": contact_phone,
    }

    # Handle image upload if a new file is chosen
    if "image" in files and files["image"] and files["image"].filename:
        image_filename, img_err = save_uploaded_file(
            files["image"], Config.CAMPAIGN_IMAGE_FOLDER, Config.ALLOWED_IMAGE_EXTENSIONS
        )
        if img_err:
            return img_err
        update_data["image_filename"] = image_filename

    # Handle document upload if a new file is chosen
    if "document" in files and files["document"] and files["document"].filename:
        doc_filename, doc_err = save_uploaded_file(
            files["document"], Config.DOCUMENT_FOLDER, Config.ALLOWED_DOCUMENT_EXTENSIONS
        )
        if doc_err:
            return doc_err
        update_data["document_filename"] = doc_filename

    update_campaign(campaign_id, update_data)
    return None
