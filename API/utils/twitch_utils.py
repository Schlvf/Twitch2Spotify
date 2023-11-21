import hashlib
import hmac
import urllib.parse

from fastapi import Request

from API.models.twitch.cache import OauthToken
from API.models.twitch.events import Event
from API.models.user.cache import UserCache
from API.utils.env_wrapper import EnvWrapper
from Core.redis_controller import RedisHandler
from Core.rest_helper.request_utils import RestHandler

TWITCH_MESSAGE_ID = "twitch-eventsub-message-id"
TWITCH_MESSAGE_TIMESTAMP = "twitch-eventsub-message-timestamp"
TWITCH_MESSAGE_SIGNATURE = "twitch-eventsub-message-signature"
HMAC_PREFIX = "sha256="


def get_hmac_message(request: Request, rawbody: str):
    if request:
        return (
            request.headers.get(TWITCH_MESSAGE_ID)
            + request.headers.get(TWITCH_MESSAGE_TIMESTAMP)
            + rawbody
        )


def get_hmac(secret, message):
    digest = hmac.HMAC(
        key=bytes(secret, "UTF-8"),
        msg=bytes(message, "UTF-8"),
        digestmod=hashlib.sha256,
    )

    return digest.hexdigest()


def authenticate_hmac(request: Request, rawbody: str):
    message = get_hmac_message(request=request, rawbody=rawbody)
    hmac = HMAC_PREFIX + get_hmac(EnvWrapper().TWITCH_HMAC_SECRET, message=message)
    signature = request.headers.get(TWITCH_MESSAGE_SIGNATURE)
    return signature == hmac


def check_dup_events(event: Event):
    dup = RedisHandler().get_pair(name=event.event.id)
    if dup:
        return True
    RedisHandler().set_pair(name=event.event.id, value=1, expiration=300)


def get_oauth_params():
    return {
        "client_id": EnvWrapper().TWITCH_APP_ID,
        "client_secret": EnvWrapper().TWITCH_APP_SECRET,
        "grant_type": "client_credentials",
    }


def get_access_token():
    token = RedisHandler().get_dict(name="twitch_oauth", class_type=OauthToken)
    if token:
        return token.access_token
    url = "https://id.twitch.tv/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = get_oauth_params()

    response = RestHandler.make_request(
        method="POST",
        url=url,
        headers=headers,
        body=body,
    )
    token = OauthToken(**response.json())
    RedisHandler().set_dict(name="twitch_oauth", payload=token.model_dump())
    RedisHandler().set_expire(name="twitch_oauth", seconds=token.expires_in)
    print("New access token generated")
    return token.access_token


def get_user_auth_params():
    return {
        "client_id": EnvWrapper().TWITCH_APP_ID,
        "redirect_uri": EnvWrapper().GRIMM_SUBDOMAIN + "/eventsub/twitch_auth",
        "response_type": "code",
        "scope": "channel:read:redemptions",
    }


def url_encode_params(params: dict):
    return "?" + urllib.parse.urlencode(params)


def get_channel_id(channel_name: str):
    user_cache = RedisHandler().get_dict(channel_name)
    if user_cache:
        return UserCache(**user_cache).twitch_channel_id

    params = {"login": channel_name}
    url = "https://api.twitch.tv/helix/users" + url_encode_params(params=params)
    headers = {
        "Authorization": "Bearer " + get_access_token(),
        "Client-Id": EnvWrapper().TWITCH_APP_ID,
    }
    response = RestHandler.make_request(method="GET", url=url, headers=headers)
    user_data = response.json()
    if not user_data.get("data"):
        return
    print("Client id obtained")

    user_cache = UserCache(
        twitch_channel_name=channel_name,
        twitch_channel_id=user_data.get("data")[0].get("id"),
    )
    RedisHandler().set_dict(
        name=channel_name,
        payload=user_cache.model_dump(exclude_none=True),
    )
    return user_cache.twitch_channel_id


def get_subscription_body(user_id: str, event_name: str):
    event_info = get_events(event_name)
    return {
        "type": f"{event_name}",
        "version": "1",
        "condition": {f"{event_info['type']}": f"{user_id}"},
        "transport": {
            "method": "webhook",
            "callback": EnvWrapper().GRIMM_SUBDOMAIN + "/eventsub/callback",
            "secret": EnvWrapper().TWITCH_HMAC_SECRET,
        },
    }


def get_headers():
    return {
        "Authorization": "Bearer " + get_access_token(),
        "Client-Id": EnvWrapper().TWITCH_APP_ID,
        "Content-Type": "application/json",
    }


def get_events(event_name=None):
    events = {
        "channel.update": {"type": "broadcaster_user_id", "scopes": ["public"]},
        "channel.follow": {"type": "broadcaster_user_id", "scopes": ["public"]},
        "channel.subscribe": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:subscriptions"],
        },
        "channel.subscription.end": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:subscriptions"],
        },
        "channel.subscription.gift": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:subscriptions"],
        },
        "channel.subscription.message": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:subscriptions"],
        },
        "channel.cheer": {"type": "broadcaster_user_id", "scopes": ["bits:read"]},
        "channel.raid": {"type": "to_broadcaster_user_id", "scopes": ["public"]},
        "channel.ban": {"type": "broadcaster_user_id", "scopes": ["channel:moderate"]},
        "channel.unban": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:moderate"],
        },
        "channel.moderator.add": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:moderate"],
        },
        "channel.moderator.remove": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:moderate"],
        },
        "channel.channel_points_custom_reward.add": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:redemptions"],
        },
        "channel.channel_points_custom_reward.update": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:redemptions"],
        },
        "channel.channel_points_custom_reward.remove": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:redemptions"],
        },
        "channel.channel_points_custom_reward_redemption.add": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:redemptions"],
        },
        "channel.channel_points_custom_reward_redemption.update": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:redemptions"],
        },
        "channel.poll.begin": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:polls"],
        },
        "channel.poll.progress": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:polls"],
        },
        "channel.poll.end": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:polls"],
        },
        "channel.prediction.begin": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:predictions"],
        },
        "channel.prediction.progress": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:predictions"],
        },
        "channel.prediction.lock": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:predictions"],
        },
        "channel.prediction.end": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:predictions"],
        },
        "channel.goal.begin": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:goals"],
        },
        "channel.goal.progress": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:goals"],
        },
        "channel.goal.end": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:goals"],
        },
        "channel.hype_train.begin": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:hype_train"],
        },
        "channel.hype_train.progress": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:hype_train"],
        },
        "channel.hype_train.end": {
            "type": "broadcaster_user_id",
            "scopes": ["channel:read:hype_train"],
        },
        "stream.online": {"type": "broadcaster_user_id", "scopes": ["public"]},
        "stream.offline": {"type": "broadcaster_user_id", "scopes": ["public"]},
        "user.update": {"type": "user_id", "scopes": ["public"]},
    }
    return events.get(event_name, events)
