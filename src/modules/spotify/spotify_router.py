from fastapi import APIRouter
from fastapi import Depends

from api import ResponseMessage
from api import sudo_auth
from api import url_encode_params

from .spotify_handler import add_song_to_queue
from .spotify_utils import get_new_access_token
from .spotify_utils import get_user_auth_params

router = APIRouter(prefix="/spotify")


@router.get("/user_authorize")
async def user_authorization(code: str = None, error: str = None):
    if error:
        return ResponseMessage.send_code_error(error=error)
    if code:
        return ResponseMessage.send_code_message(code=code)

    url = "https://accounts.spotify.com/authorize"
    params = get_user_auth_params()
    return {"redirect_url": url + url_encode_params(params=params)}


@router.get("/validate_code/{channel_name}")
async def generate_access_token(channel_name: str, code: str):
    get_new_access_token(code=code, user_name=channel_name)
    return ResponseMessage.get_successful_auth_message()


@router.get("/request_song", dependencies=[Depends(sudo_auth)])
async def request_song(link: str, user_name: str):
    add_song_to_queue(link=link, user_name=user_name)
    return {
        "Sent": link,
    }
