from fastapi import FastAPI

from modules.redis.routers import redis_router
from modules.spotify.routers import spotify_router
from modules.twitch.routers import eventsub_router

app = FastAPI()
app.include_router(eventsub_router.router)
app.include_router(spotify_router.router)
app.include_router(redis_router.router)


@app.get("/ping")
async def ping():
    return {"message": "Pong!"}
