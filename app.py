from flask import Flask

from config import Config
from extensions import (
    db,
    migrate,
    jwt,
    socketio,
    cors
)
from blacklist import BLACKLIST
from extensions import mail

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):

        return jwt_payload["jti"] in BLACKLIST
    

    socketio.init_app(app)
    cors.init_app(app)
    mail.init_app(app)

    # load models
    import models

    # register blueprints
    from modules.jobs.routes import jobs_bp
    app.register_blueprint(jobs_bp)

    from modules.workers.routes import worker_bp
    app.register_blueprint(worker_bp, url_prefix="/workers")

    from modules.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.route("/")
    def home():
        return {
            "message": "Kazi Mikononi backend running"
        }

    return app