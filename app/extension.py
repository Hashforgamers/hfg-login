# app/extensions.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
import redis

db = SQLAlchemy()
migrate = Migrate()
mail    = Mail()


def configure_redis(app: Flask):
    """
    Configures the Redis client with the app configuration.
    """
    redis_url = app.config.get("REDIS_URL")
    if redis_url:
        app.redis_client = redis.StrictRedis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            health_check_interval=30,
            retry_on_timeout=True,
        )
        return
    app.redis_client = redis.StrictRedis(
        host=app.config.get('REDIS_HOST', 'redis'),
        port=int(app.config.get('REDIS_PORT', 6379)),
        db=int(app.config.get('REDIS_DB', 0)),
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        health_check_interval=30,
        retry_on_timeout=True,
    )
