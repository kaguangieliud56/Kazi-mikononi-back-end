from app import create_app
from extensions import socketio

app = create_app()

socketio.init_app(app)

# ❌ DO NOT use socketio.run here