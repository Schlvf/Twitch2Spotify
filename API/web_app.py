from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.spotify.routers import spotify_router
from modules.twitch.routers import eventsub_router

# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()
app.include_router(eventsub_router.router)
app.include_router(spotify_router.router)

origins = [
    "*",
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
    return {"message": "Pong!"}
