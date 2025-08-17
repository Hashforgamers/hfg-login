# app/config.py

import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev')

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        'postgresql://postgres:postgres@db:5432/vendor_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Add safe engine options for Neon / Postgres
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,    # Test connection before using
        "pool_recycle": 1800,     # Recycle every 30 minutes to avoid SSL timeouts
        "pool_size": 5,           # Keep a small pool
        "max_overflow": 10        # Allow bursts
    }

    # Redis Configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
