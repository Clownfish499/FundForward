import json
import os
from flask import Blueprint, abort, render_template, request, send_from_directory, session

from config import Config
from models.campaign import (
    get_campaign_by_id,
    get_platform_stats,
    list_featured_campaigns,
    list_public_campaigns,
)
from models.donation import list_campaign_donations

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    featured = list_featured_campaigns(limit=3)
    stats = get_platform_stats()
    return render_template(
        "index.html",
        featured_campaigns=featured,
        stats=stats,
        categories=Config.CATEGORIES,
    )


@public_bp.route("/explore")
def explore():
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    sort = request.args.get("sort", "newest").strip()
    campaigns = list_public_campaigns(search=search, category=category, sort=sort)
    return render_template(
        "explore.html",
        campaigns=campaigns,
        categories=Config.CATEGORIES,
        selected_category=category,
        search_query=search,
        selected_sort=sort,
    )


@public_bp.route("/about")
def about():
    return render_template("about.html")


@public_bp.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")


@public_bp.route("/campaign/<int:campaign_id>")
@public_bp.route("/campaigns/<int:campaign_id>")
def campaign_detail(campaign_id):
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        abort(404)

    # Restrict pending/rejected campaigns to creator or admin
    user_id = session.get("user_id")
    user_role = session.get("user_role")
    if campaign["status"] not in ("approved", "active", "completed"):
        if user_role != "admin" and campaign["user_id"] != user_id:
            abort(404)

    donations = list_campaign_donations(campaign_id)
    reasons = json.loads(campaign["reasons_json"]) if campaign.get("reasons_json") else []
    progress_pct = min(100, round((campaign["raised_amount"] / campaign["goal_amount"]) * 100, 1))

    return render_template(
        "campaign_detail.html",
        campaign=campaign,
        donations=donations,
        reasons=reasons,
        progress_pct=progress_pct,
    )


@public_bp.route("/uploads/<folder>/<filename>")
def uploaded_file(folder, filename):
    if folder == "campaigns":
        directory = Config.CAMPAIGN_IMAGE_FOLDER
    elif folder == "documents":
        directory = Config.DOCUMENT_FOLDER
    else:
        abort(404)

    safe_path = os.path.join(directory, filename)
    if not os.path.isfile(safe_path):
        abort(404)
    return send_from_directory(directory, filename)
