import json
import os
from flask import Flask, render_template, session

from config import Config
from database.db import init_schema
from init_db import seed_database
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp
from routes.campaign_routes import campaign_bp
from routes.donation_routes import donation_bp
from routes.public_routes import public_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["CAMPAIGN_IMAGE_FOLDER"], exist_ok=True)
    os.makedirs(app.config["DOCUMENT_FOLDER"], exist_ok=True)

    # Ensure SQLite schema exists on startup
    if not os.path.exists(app.config["DATABASE_PATH"]):
        seed_database(app.config["DATABASE_PATH"])
    else:
        init_schema(app.config["DATABASE_PATH"])

    # Register blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(campaign_bp)
    app.register_blueprint(donation_bp)
    app.register_blueprint(admin_bp)

    # Template context & filters
    @app.context_processor
    def inject_globals():
        return {
            "current_user_id": session.get("user_id"),
            "current_user_name": session.get("user_name"),
            "current_user_role": session.get("user_role"),
        }

    @app.template_filter("currency")
    def format_currency(value):
        try:
            return f"${float(value):,.2f}"
        except (TypeError, ValueError):
            return "$0.00"

    @app.template_filter("from_json")
    def from_json_filter(value):
        try:
            return json.loads(value) if value else []
        except Exception:
            return []

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def file_too_large(e):
        return render_template("errors/413.html"), 413

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, host="127.0.0.1", port=5000)
