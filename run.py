# main entry point
# just run this file to start the app
# - Harshal

from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # take port from env if deployed, else use 5000 locally
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
