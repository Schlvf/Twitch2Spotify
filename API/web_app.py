from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from API.models.twitch.cache import OauthToken
from API.models.user.cache import UserCache
from API.routers.spotify import spotify_router
from API.routers.twitch import eventsub_router
from Core.redis_controller import RedisHandler

# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()
app.include_router(eventsub_router.router)
app.include_router(spotify_router.router)

origins = [
    "http://localhost",
    "http://localhost:5000",
]
origin_regex = ".*:*"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_origin_regex=origin_regex,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(HTTPSRedirectMiddleware)


@app.get("/")
async def root():
    return {"message": "Hello world"}


@app.get("/ping")
async def ping():
    # x = OauthToken(access_token="value", expires_in=1313, token_type="type")
    # RedisHandler().set_dict(name="twitch_oauth",payload=x.model_dump())
    res = RedisHandler().get_dict(name="twitch_oauth", class_type=OauthToken)
    print(type(res))
    # RedisHandler().set_expire(key="twitch_oauth",seconds=10)
    # print(RedisHandler().ping())
    return {"message": "Pong!"}


@app.delete("/redis_cache")
async def flush_cache():
    # RedisHandler().set_dict(name="twitch_oauth",payload=x.model_dump())
    RedisHandler().flush_all()
    # RedisHandler().set_expire(key="twitch_oauth",seconds=10)
    # print(RedisHandler().ping())
    return {"message": "Flushed cache"}


@app.get("/redis_cache")
async def scan_cache():
    res = RedisHandler().count()
    return {"Status": f"Found {res} documents"}


@app.get("/user_cache")
async def get_user_cache(user_name: str):
    user_cache = RedisHandler().get_dict(name=user_name, class_type=UserCache)
    if user_cache:
        return user_cache.model_dump()
    return {"Status": "No user cache found"}
