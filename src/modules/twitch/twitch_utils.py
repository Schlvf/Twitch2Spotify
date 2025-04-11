import hashlib
import hmac

from fastapi import Request

from api import OauthToken
from api import return_status_response
from api import url_encode_params
from core import EnvWrapper
from core import make_request
from modules.redis import RedisHandler
from modules.redis import UserCache

from .eventsub_models import Event
from .eventsub_models import TwitchUser

TWITCH_MESSAGE_ID = "twitch-eventsub-message-id"
TWITCH_MESSAGE_TIMESTAMP = "twitch-eventsub-message-timestamp"
TWITCH_MESSAGE_SIGNATURE = "twitch-eventsub-message-signature"
HMAC_PREFIX = "sha256="
REDIRECT_URI = f"{EnvWrapper().GRIMM_SUBDOMAIN}/eventsub/auth"


def get_hmac_message(request: Request, rawbody: str):
    if request:
        return f"{request.headers.get(TWITCH_MESSAGE_ID)}{request.headers.get(TWITCH_MESSAGE_TIMESTAMP)}{rawbody}"


def get_hmac(secret, message):
    digest = hmac.HMAC(
        key=bytes(secret, "UTF-8"),
        msg=bytes(message, "UTF-8"),
        digestmod=hashlib.sha256,
    )

    return digest.hexdigest()


def authenticate_hmac(request: Request, rawbody: str):
    message = get_hmac_message(request=request, rawbody=rawbody)
    hmac = f"{HMAC_PREFIX}{get_hmac(EnvWrapper().TWITCH_HMAC_SECRET, message=message)}"
    signature = request.headers.get(TWITCH_MESSAGE_SIGNATURE)
    return signature == hmac


def check_dup_events(event: Event):
    if event.event:
        dup = RedisHandler().get_pair(name=event.event.id)
        if dup:
            return True
        RedisHandler().set_pair(name=event.event.id, value=1, expiration=300)


def get_user_token_params(code=str):
    return {
        "client_id": EnvWrapper().TWITCH_APP_ID,
        "client_secret": EnvWrapper().TWITCH_APP_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }


def get_app_token_params():
    return {
        "client_id": EnvWrapper().TWITCH_APP_ID,
        "client_secret": EnvWrapper().TWITCH_APP_SECRET,
        "grant_type": "client_credentials",
    }


def get_access_token():
    token = RedisHandler().get_pair(name="twitch_oauth")
    if token:
        return token

    url = "https://id.twitch.tv/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = get_app_token_params()

    token = make_request(
        method="POST",
        url=url,
        headers=headers,
        body=body,
        class_type=OauthToken,
    )
    RedisHandler().set_pair(
        name="twitch_oauth",
        value=token.access_token,
        expiration=token.expires_in,
    )
    print("New app access token generated")
    return token.access_token


def get_user_access_token(code: str) -> OauthToken:
    url = "https://id.twitch.tv/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = get_user_token_params(code=code)

    token = make_request(
        method="POST",
        url=url,
        headers=headers,
        body=body,
        class_type=OauthToken,
    )
    if not isinstance(token, OauthToken):
        return_status_response(
            status_code=400,
            custom_message="There was a problem authorizing twitch or your session has ended",
        )

    print("New user access token generated")
    return token


def get_user_auth_params():
    return {
        "client_id": EnvWrapper().TWITCH_APP_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "channel:manage:redemptions",
    }


def get_user_cache(channel_name: str) -> UserCache:
    user_cache = RedisHandler().get_dict(name=channel_name, class_type=UserCache)
    if not user_cache:
        return_status_response(
            status_code=400,
            custom_message="Please re-authorize twitch before performing this action",
        )
    return user_cache


def get_subscription_body(user_id: str, event_name: str, reward_id: str | None = None):
    event_info = get_events_info(event_name)
    conditions = {
        f"{event_info['type']}": f"{user_id}",
    }
    if reward_id:
        conditions["reward_id"] = reward_id

    return {
        "type": f"{event_name}",
        "version": "1",
        "condition": conditions,
        "transport": {
            "method": "webhook",
            "callback": f"{EnvWrapper().GRIMM_SUBDOMAIN}/eventsub/callback",
            "secret": EnvWrapper().TWITCH_HMAC_SECRET,
        },
    }


def get_headers():
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "Client-Id": EnvWrapper().TWITCH_APP_ID,
        "Content-Type": "application/json",
    }


def get_events_info(event_name: str):
    events = {
        "channel.channel_points_custom_reward_redemption.add": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:redemptions"],
        },
    }
    return events.get(event_name)


def parse_user_data_into_cache(
    new_user: TwitchUser,
    new_token: OauthToken,
    current_ts: float,
) -> UserCache:
    return UserCache(
        twitch_channel_name=new_user.login,
        twitch_channel_id=new_user.id,
        twitch_user_token=new_token.access_token,
        twitch_user_refresh_token=new_token.refresh_token,
        twitch_user_token_expiration=current_ts + new_token.expires_in,
    )


def parse_token_data_into_cache(
    user_cache: UserCache,
    new_token: OauthToken,
    current_ts: float,
) -> UserCache:
    user_cache.twitch_user_token = new_token.access_token
    user_cache.twitch_user_refresh_token = new_token.refresh_token
    user_cache.twitch_user_token_expiration = current_ts + new_token.expires_in

    return user_cache


def get_twitch_auth_url() -> str:
    url = "https://id.twitch.tv/oauth2/authorize"
    params = get_user_auth_params()
    return url + url_encode_params(params=params)


def get_enable_url(channel_name: str) -> str:
    return f"{EnvWrapper().GRIMM_SUBDOMAIN}/eventsub/enable_integration/{channel_name}"


def get_disable_url(channel_name: str) -> str:
    return f"{EnvWrapper().GRIMM_SUBDOMAIN}/eventsub/disable_integration/{channel_name}"
