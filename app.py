from flask import Flask
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


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    cors.init_app(app, resources={r"/*": {"origins": "*"}})
    mail.init_app(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLACKLIST

    # load models
    import models

    # register blueprints
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

    # register socket events
    from realtime.socket import init_socket
    init_socket(app)

    @app.route("/")
    def home():
        return {
            "message": "Kazi Mikononi backend running"
        }

    return app