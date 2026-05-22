from app import create_app
from extensions import socketio


app = create_app()

<<<<<<< HEAD

if __name__ == "__main__":
    socketio.run(app, debug=True)
=======
# ❌ DO NOT use socketio.run here 
>>>>>>> 5bc75d2 (Disable email verification - SendGrid not configured)
