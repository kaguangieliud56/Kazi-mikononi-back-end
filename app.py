from flask import Flask

from config import Config
from extensions import (
    db,
    migrate,
    jwt,
    socketio,
    cors
)

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app)
    cors.init_app(app)

    # load models
    import models

    @app.route("/")
    def home():
        return {
            "message": "Kazi Mikononi backend running"
        }

    return app