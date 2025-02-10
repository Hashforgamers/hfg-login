# app/extensions.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import redis

db = SQLAlchemy()
migrate = Migrate()


def configure_redis(app: Flask):
    """
    Configures the Redis client with the app configuration.
    """
    app.redis_client = redis.StrictRedis(
        host=app.config.get('REDIS_HOST', 'redis'),
        port=int(app.config.get('REDIS_PORT', 6379)),
        db=int(app.config.get('REDIS_DB', 0)),
        decode_responses=True  # Ensure values are strings, not bytes
    )