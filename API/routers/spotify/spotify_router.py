from fastapi import APIRouter

from API.handlers.spotify import spotify_handler
from API.utils import general_utils
from API.utils import spotify_utils

router = APIRouter(prefix="/spotify")


@router.get("/user_authorize")
async def user_authorization(code: str = None, error: str = None):
    if error:
        return general_utils.send_code_error(error=error)
    if code:
        return general_utils.send_code_message(code=code)

    url = "https://accounts.spotify.com/authorize"
    params = spotify_utils.get_user_auth_params()
    return {"redirect_url": url + general_utils.url_encode_params(params=params)}


@router.post("/access_token")
async def generate_access_token(code: str, user_name: str):
    res = spotify_utils.get_new_access_token(code=code, user_name=user_name)

    if res:
        return general_utils.get_unsuccessful_auth_message()
    return general_utils.get_successful_auth_message()


@router.get("/request_song")
async def add_song_to_queue(link: str, user_name: str):
    spotify_handler.add_song_to_queue(link=link, user_name=user_name)
    return {
        "Sent": link,
    }
