from fastapi import APIRouter
from fastapi import Depends

from api import sudo_auth

from .redis_handler import RedisHandler

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
    return {"Status": f"Deleted {res} documents"}
