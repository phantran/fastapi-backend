import logging
import time
from datetime import timedelta
from typing import Optional

import redis.asyncio as aioredis

from core.config import config

redis = aioredis.from_url(
    url=f"redis://{config.REDIS_HOST}",
    encoding="utf-8",
    decode_responses=True,
)
logger = logging.getLogger(__name__)


async def is_revoked_token(token: str) -> bool:
    """
    Check if token is revoked
    """
    try:
        entry = await redis.get(token)
        return entry == "1"
    except Exception as e:
        logger.error(f"Can't check revoked token {str(e)}")
    return False


async def add_to_active_sessions(user_id: int, token: str) -> bool:
    """
    Add a new access token to set of active sessions
    """
    try:
        await redis.sadd(user_id, token)
    except Exception as e:
        logger.error(f"Can't add new session {str(e)}")
        return False


async def get_active_sessions(user_id: int) -> set:
    """
    Get all active tokens of user with id as user_id
    """
    try:
        res = await redis.smembers(user_id)
        return res
    except Exception as e:
        logger.error(f"Can't add new session {str(e)}")
        return set()


async def revoke_other_active_sessions(
    user_id: int, current_token: Optional[str] = None
) -> bool:
    """
    Remove all active sessions (tokens) in cache
    """
    try:
        active_sessions = await redis.smembers(user_id)
        pipeline = await redis.pipeline()
        if current_token:
            active_sessions.discard(current_token)
        for token in active_sessions:
            pipeline.setex(
                token,
                timedelta(seconds=config.JWT_EXPIRATION),
                "1",
            )
        pipeline.delete(user_id)
        if current_token:
            pipeline.sadd(user_id, current_token)
        await pipeline.execute()
    except Exception as e:
        logger.error(f"Can't add new session {str(e)}")
        return False


async def revoke_jwt_token(claims: dict, token: str) -> bool:
    """
    Perform token revoking by storing the token in Redis with expiration
    """
    try:
        expired_in = claims["exp"] - time.time()
        await redis.setex(
            token,
            timedelta(seconds=expired_in),
            "1",
        )
        return True
    except Exception as e:  # noqa
        logger.warning(f"Error while revoking token {str(e)}")
        return False
