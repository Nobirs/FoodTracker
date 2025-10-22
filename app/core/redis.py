from redis.asyncio import from_url

from app.config import settings

_redis = None


def get_redis_client():
    global _redis
    if not _redis:
        _redis = from_url(settings.REDIS_URL, decode_responses=True)
    return _redis
