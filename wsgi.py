import eventlet
eventlet.monkey_patch()

from app import create_app
from extensions import socketio

app = create_app()

# IMPORTANT: expose SocketIO app for Gunicorn
app = socketio