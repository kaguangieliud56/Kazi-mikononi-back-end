from app import create_app
from extensions import socketio

app = create_app()

@app.route("/ping")
def ping():
    return {"status": "alive"}

if __name__ == "__main__":
    socketio.run(app, debug=True)