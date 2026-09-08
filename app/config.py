import os

# basic config for the flask app
# TODO: move secret key to env var for production

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-later")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024   # 5 MB max upload
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")

    # make sure uploads folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
