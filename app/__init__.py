import logging
import time
import uuid
from flask import Flask, g, request
from routes.auth_routes import auth_bp

from .config import Config
import os
from .extension import db, migrate, mail, configure_redis
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix


def _is_insecure_secret(value: str, placeholders: set[str]) -> bool:
    if not value:
        return True
    candidate = str(value).strip()
    if candidate in placeholders:
        return True
    return len(candidate) < 32


def _validate_production_config(app: Flask) -> None:
    app_env = str(app.config.get("APP_ENV", "development")).lower()
    is_production = app_env in {"prod", "production"}
    if not is_production:
        return
    weak_secret = _is_insecure_secret(
        app.config.get("SECRET_KEY", ""),
        {"dev-secret-change-me", "changeme"},
    )
    weak_jwt_secret = _is_insecure_secret(
        app.config.get("JWT_SECRET_KEY", ""),
        {"dev-jwt-secret-change-me", "dev", "changeme"},
    )
    if weak_secret or weak_jwt_secret:
        raise RuntimeError(
            "In production, SECRET_KEY and JWT_SECRET_KEY must be strong non-default values with length >= 32."
        )

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    _validate_production_config(app)
    if app.config.get("TRUST_PROXY", True):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    CORS(app, origins=app.config.get("CORS_ALLOWED_ORIGINS", "*"))

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app) 
    configure_redis(app)
    app.register_blueprint(auth_bp, url_prefix='/api')  # Prefixing all routes with /api

    @app.before_request
    def _start_request_timer():
        g.request_start_ts = time.perf_counter()
        incoming_request_id = (
            request.headers.get("X-Request-Id")
            or request.headers.get("X-Correlation-Id")
        )
        g.request_id = incoming_request_id or str(uuid.uuid4())

    @app.after_request
    def _attach_response_metadata(response):
        response.headers["X-Request-Id"] = getattr(g, "request_id", "")
        response.headers.setdefault(
            "Cache-Control",
            app.config.get("API_DEFAULT_CACHE_CONTROL", "no-store"),
        )
        if app.config.get("API_ENABLE_TIMING_HEADERS", True):
            start_ts = getattr(g, "request_start_ts", None)
            if start_ts is not None:
                elapsed_ms = (time.perf_counter() - start_ts) * 1000.0
                response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
                slow_ms = int(app.config.get("API_SLOW_REQUEST_MS", 120) or 120)
                if elapsed_ms >= slow_ms:
                    app.logger.warning(
                        "slow_request request_id=%s method=%s path=%s status=%s elapsed_ms=%.2f",
                        getattr(g, "request_id", "-"),
                        request.method,
                        request.path,
                        response.status_code,
                        elapsed_ms,
                    )
        return response

    # Configure logging
    debug_mode = app.config.get("DEBUG_MODE", False)
    log_level = logging.DEBUG if debug_mode else logging.WARNING
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    return app
