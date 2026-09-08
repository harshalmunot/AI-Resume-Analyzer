from flask import Flask
from flask_cors import CORS
from app.config import Config
import nltk

# make sure nltk data is downloaded (first time only)
# had issue when deploying without this - kept crashing
for pkg in ["punkt", "punkt_tab", "stopwords"]:
    try:
        if "punkt" in pkg:
            nltk.data.find(f"tokenizers/{pkg}")
        else:
            nltk.data.find(f"corpora/{pkg}")
    except LookupError:
        nltk.download(pkg, quiet=True)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)  # needed for API calls from frontend

    # register routes
    from app.routes import bp
    app.register_blueprint(bp)

    return app
