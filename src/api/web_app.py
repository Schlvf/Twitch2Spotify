from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from modules.redis import redis_router
from modules.spotify import spotify_router
from modules.twitch import eventsub_router
from modules.twitch import get_twitch_auth_url

templates = Jinja2Templates(directory="dist")

app = FastAPI()
app.mount("/static", StaticFiles(directory="dist"), name="static")
app.include_router(eventsub_router)
app.include_router(spotify_router)
app.include_router(redis_router)


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    twitch_auth_url = get_twitch_auth_url()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"twitch_auth_url": twitch_auth_url},
    )


@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="about.html",
    )


@app.get("/ping")
async def ping():
    return {"message": "Pong!"}


@app.get("/{file_path:path}")
async def redirect_to_static(file_path: str):
    return RedirectResponse(url=f"/static/{file_path}")
