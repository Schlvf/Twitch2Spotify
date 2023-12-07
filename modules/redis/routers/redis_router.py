from fastapi import APIRouter

from modules.redis.handlers.redis_controller import RedisHandler

router = APIRouter(prefix="/eventsub")


@router.delete("/redis_cache")
async def flush_cache():
    # RedisHandler().set_dict(name="twitch_oauth",payload=x.model_dump())
    RedisHandler().flush_all()
    # RedisHandler().set_expire(key="twitch_oauth",seconds=10)
    # print(RedisHandler().ping())
    return {"message": "Flushed cache"}


@router.get("/redis_cache")
async def scan_cache():
    res = RedisHandler().count()
    return {"Status": f"Found {res} documents"}
