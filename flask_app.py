from flask import Flask
from config import ProductionConfig
from flask_cors import CORS
# from yourapp import db, blueprints, etc.

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)

    # init db, register blueprints, etc.
    # db.init_app(app)
    # app.register_blueprint(...)

    return app
