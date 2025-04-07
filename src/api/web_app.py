from fastapi import FastAPI

from modules.redis import redis_router
from modules.spotify import spotify_router
from modules.twitch import eventsub_router

app = FastAPI()
app.include_router(eventsub_router)
app.include_router(spotify_router)
app.include_router(redis_router)


@app.get("/ping")
async def ping():
    return {"message": "Pong!"}
