import redis
from pydantic import BaseSettings


class RedisConfig(BaseSettings):
    """Redis 설정"""
    host: str
    port: int

    class Config:
        env_file = "local.env"

def get_redis_config() -> RedisConfig:
    """redis 설정 로드"""
    return RedisConfig()

def get_redis_connection():
    """redis connection 생성"""
    redis_config = get_redis_config()
    return redis.Redis(host=redis_config.host, port=redis_config.port, db=0, decode_responses=True, charset="utf-8")
