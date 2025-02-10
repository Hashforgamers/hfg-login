from flask import current_app
import redis
import json
from datetime import timedelta

# Set up Redis for token blacklisting
redis_client = redis.StrictRedis(
    host='localhost',  # Update with your Redis server configuration
    port=6379,
    db=0,
    decode_responses=True
)

def add_to_blacklist(token):
    """
    Add a token to the Redis blacklist.

    :param token: The JWT token to blacklist.
    :return: True if added successfully, False otherwise.
    """
    try:
        # Parse token expiration
        token_data = json.loads(token)  # Ensure token contains expiration
        exp = token_data.get('exp', 3600)  # Default expiry time in seconds
        ttl = timedelta(seconds=exp)
        
        # Store the token in Redis with its TTL
        redis_client.setex(f"blacklist:{token}", ttl, "invalid")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to add token to blacklist: {str(e)}")
        return False
