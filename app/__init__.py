import logging
from flask import Flask
from routes.auth_routes import auth_bp

from .config import Config
import os
from .extension import db, migrate, mail, configure_redis
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=app.config.get("CORS_ALLOWED_ORIGINS", "*"))

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app) 
    configure_redis(app)
    app.register_blueprint(auth_bp, url_prefix='/api')  # Prefixing all routes with /api
    

    # Configure logging
    debug_mode = app.config.get("DEBUG_MODE", False)
    log_level = logging.DEBUG if debug_mode else logging.WARNING
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    return app
