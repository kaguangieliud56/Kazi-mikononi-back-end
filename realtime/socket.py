from extensions import socketio
from realtime.events import handle_events

def init_socket(app):
    handle_events(socketio)
    