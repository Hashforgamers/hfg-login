import logging
from flask import Flask
from routes.auth_routes import auth_bp

from .config import Config
import os
from .extension import db, migrate, configure_redis

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    configure_redis(app)
    app.register_blueprint(auth_bp, url_prefix='/api')  # Prefixing all routes with /api
    

    # Configure logging
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    log_level = logging.DEBUG if debug_mode else logging.WARNING
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    return app

