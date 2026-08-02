from dotenv import load_dotenv
from flask import Flask

from app.routes import main


def create_app() -> Flask:
    app = Flask(__name__)

    load_dotenv()

    app.register_blueprint(main)

    return app
