from flask import Flask, jsonify
from config import Config
from extensions import (
    db,
    migrate,
    jwt,
    socketio,
    cors,
    mail
)
from blacklist import BLACKLIST
from flask_socketio import SocketIO
import os


def create_app():
    app = Flask(__name__, static_folder="static")

    # -------------------------
    # LOAD CONFIG FIRST
    # -------------------------
    app.config.from_object(Config)

    # -------------------------
    # NOW SAFE TO USE CONFIG
    # -------------------------
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # -------------------------
    # INIT EXTENSIONS
    # -------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # -------------------------
    # JWT ERROR HANDLERS
    # -------------------------
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "error": "Token expired",
            "code": "token_expired"
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "error": "Invalid token",
            "code": "token_invalid"
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "error": "Authorization token is missing",
            "code": "token_missing"
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "error": "Token has been revoked",
            "code": "token_revoked"
        }), 401

    # -------------------------
    # SOCKET + CORS + MAIL
    # -------------------------
    socketio.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})
    mail.init_app(app)

    # -------------------------
    # TOKEN BLACKLIST CHECK
    # -------------------------
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLACKLIST

    # -------------------------
    # IMPORT MODELS
    # -------------------------
    import models

    # -------------------------
    # REGISTER BLUEPRINTS
    # -------------------------
    from modules.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from modules.jobs.routes import jobs_bp
    app.register_blueprint(jobs_bp)

    from modules.applications.routes import applications_bp
    app.register_blueprint(applications_bp)

    from modules.ratings.routes import ratings_bp
    app.register_blueprint(ratings_bp)

    from modules.messages.routes import messages_bp
    app.register_blueprint(messages_bp)

    from modules.workers.routes import worker_bp
    app.register_blueprint(worker_bp, url_prefix="/workers")

    from modules.users.routes import users_bp
    app.register_blueprint(users_bp)

    # -------------------------
    # SOCKET EVENTS
    # -------------------------
    from realtime.socket import init_socket
    init_socket(app)

    # -------------------------
    # HOME ROUTE
    # -------------------------
    @app.route("/")
    def home():
        return {"message": "Kazi Mikononi backend running"}

    return app