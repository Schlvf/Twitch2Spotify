from fastapi import APIRouter

from api import ResponseMessage
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
    return {"redirect_url": f"{url}{url_encode_params(params=params)}"}


@router.post("/access_token")
async def generate_access_token(code: str, user_name: str):
    get_new_access_token(code=code, user_name=user_name)

    return ResponseMessage.get_successful_auth_message()


@router.get("/request_song")
async def request_song(link: str, user_name: str):
    add_song_to_queue(link=link, user_name=user_name)
    return {
        "Sent": link,
    }
