import base64
import re
import time

from api import return_status_response
from core import EnvWrapper
from core import make_request
from modules.redis import RedisHandler
from modules.redis import UserCache

REDIRECT_URI = f"{EnvWrapper().GRIMM_SUBDOMAIN}/spotify/user_authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"


def get_user_auth_params():
    return {
        "client_id": EnvWrapper().SPOTIFY_APP_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "user-modify-playback-state user-read-playback-state",
    }


def make_spotify_request(
    method: str,
    url: str,
    headers: dict = None,
    body: dict = None,
    params: dict = None,
    user_name: str = None,
):
    if not headers:
        user_cache = RedisHandler().get_dict(name=user_name, class_type=UserCache)
        if not user_cache:
            return_status_response(
                status_code=400,
                custom_message="Please re-authorize twitch before performing this action",
            )
        if not user_cache.spotify_auth_token:
            return_status_response(
                status_code=400,
                custom_message="Please re-authorize spotify and valide the code before performing this action",
            )
        if token_is_expired(user_cache=user_cache):
            print("Spotify token expired, refreshing...")
            user_cache = refresh_access_token(user_cache=user_cache)
        headers = get_headers(user_cache=user_cache)

    res = make_request(
        method=method,
        url=url,
        headers=headers,
        body=body,
        params=params,
    )
    print(">>>", res.status_code)
    if res.status_code == 200:
        print("SPOTI REQUEST CONTENT:", res.content)
        # checking for string due to spotify api issue
        try:
            return res.json()
        except Exception:
            print("Spotify API is still fucked")
            return
        # return res.json()
    if res.status_code == 204:
        print("Song added to queue")
        return
    if res.status_code == 401:
        print("Token invalid...")
    print("ERROR LOG", res.json())
    return res.json()


def refresh_access_token(user_cache: UserCache):
    current_ts = time.time()
    body = {
        "grant_type": "refresh_token",
        "refresh_token": user_cache.spotify_refresh_token,
    }
    res = make_spotify_request(
        method="POST",
        url=TOKEN_URL,
        headers=get_auth_headers(),
        body=body,
    )
    user_cache.spotify_auth_token = res.get("access_token")
    user_cache.spotify_expire_ts = current_ts + res.get("expires_in")
    RedisHandler().set_dict(
        name=user_cache.twitch_channel_name,
        payload=user_cache.model_dump(exclude_none=True),
    )
    return user_cache


def get_new_access_token(code: str, user_name: str):
    current_ts = time.time()
    body = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    res = make_spotify_request(
        method="POST",
        url=TOKEN_URL,
        headers=get_auth_headers(),
        body=body,
    )

    if res.get("error"):
        return_status_response(
            status_code=400,
            custom_message="There was a problem with the code - Please try with a new one",
        )

    user_cache = RedisHandler().get_dict(name=user_name, class_type=UserCache)
    if not user_cache:
        return_status_response(
            status_code=400,
            custom_message="Please re-authorize twitch before performing this action",
        )

    user_cache.spotify_auth_token = res.get("access_token")
    user_cache.spotify_refresh_token = res.get("refresh_token")
    user_cache.spotify_expire_ts = current_ts + res.get("expires_in")
    RedisHandler().set_dict(
        name=user_name,
        payload=user_cache.model_dump(exclude_none=True),
    )


def get_auth_headers():
    auth_str = str.format(
        "{0}:{1}",
        EnvWrapper().SPOTIFY_APP_ID,
        EnvWrapper().SPOTIFY_APP_SECRET,
    )
    return {
        "Authorization": f"Basic {str_to_base64(auth_str)}",
        "Content-Type": "application/x-www-form-urlencoded",
    }


def get_headers(user_cache: UserCache):
    return {
        "Authorization": f"Bearer {user_cache.spotify_auth_token}",
    }


def str_to_base64(text: str):
    base64_bytes = base64.b64encode(bytes(text, "utf-8"))
    base64_str = base64_bytes.decode("utf-8")
    return base64_str.replace("=", "")


def parse_link_to_uri(link: str):
    split = link.split(sep="/")
    id = re.findall("([a-zA-Z0-9]+)", split[-1])
    return f"spotify:track:{id[0]}"


def token_is_expired(user_cache: UserCache):
    current_ts = time.time()
    return current_ts >= user_cache.spotify_expire_ts
