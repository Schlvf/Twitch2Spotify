from fastapi import APIRouter
from fastapi import Depends

from API.utils.router_dependencies import sudo_auth
from modules.redis.handlers.redis_controller import RedisHandler

router = APIRouter(prefix="/redis", dependencies=[Depends(sudo_auth)])


@router.delete("/flush")
async def flush_cache():
    RedisHandler().flush_all()
    return {"message": "Flushed cache"}


@router.get("/count")
async def scan_cache():
    res = RedisHandler().count()
    return {"Status": f"Found {res} documents"}


@router.get("/key")
async def get_keys(pattern: str | None = None, count: int | None = 1):
    res = RedisHandler().get_keys(pattern=pattern, count=count)
    return {"Keys": res}


@router.delete("/key")
async def delete_keys(pattern: str | None = None, count: int | None = 1):
    res = RedisHandler().delete_keys(pattern=pattern, count=count)
    return {"Deleted": res}
