from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.templating import Jinja2Templates

from api import get_spotify_auth_url
from api import ResponseMessage
from api import sudo_auth

from .spotify_handler import add_song_to_queue
from .spotify_utils import get_new_access_token

router = APIRouter(prefix="/spotify")
templates = Jinja2Templates(directory="dist")


@router.get("/auth")
async def spotify_authorization(request: Request, code: str = None, error: str = None):
    if error:
        return ResponseMessage.send_code_error(error=error)
    if code:
        return templates.TemplateResponse(
            request=request,
            name="spotify_code.html",
            context={"spotify_code": code},
        )


@router.get("/user_authorize")
async def user_authorization():
    return {"redirect_url": get_spotify_auth_url()}


@router.get("/validate_code/{channel_name}")
async def generate_access_token(channel_name: str, code: str):
    get_new_access_token(code=code, user_name=channel_name)
    return ResponseMessage.get_successful_auth_message()


@router.get("/request_song", dependencies=[Depends(sudo_auth)])
async def request_song(link: str, user_name: str):
    response = add_song_to_queue(link=link, user_name=user_name)
    if response.get("error"):
        return response
    return {
        "Sent": link,
    }
