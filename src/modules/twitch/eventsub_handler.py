from fastapi import HTTPException

from core import make_request
from core.wrappers import EnvWrapper
from modules.redis.cache_models import UserCache
from modules.redis.redis_handler import RedisHandler

from .eventsub_models import TwitchUsersQuery
from .twitch_utils import (
    get_channel_id,
    get_headers,
    get_subscription_body,
    get_user_access_token,
)

URL = "https://api.twitch.tv/helix/eventsub/subscriptions"


def subscribe_to_event(event_name: str, channel_name: str):
    user_id = get_channel_id(channel_name=channel_name)

    if not user_id:
        raise HTTPException(
            status_code=403,
            detail="Make sure the username is correct and try again",
        )

    body = get_subscription_body(user_id=user_id, event_name=event_name)
    response = make_request(
        method="POST",
        url=URL,
        headers=get_headers(),
        json=body,
    )
    if response.status_code in [200, 202, 409]:
        print("Successfully subscribed to ", event_name)
        return

    print(response.json())
    print(response.status_code)

    raise HTTPException(
        status_code=400,
        detail="There was a problem, please try again",
    )


def unsubscribe_to_all():
    response = make_request(
        method="GET",
        url=URL,
        headers=get_headers(),
    )
    print(response)
    subscriptions = response.json()
    for event in subscriptions.get("data"):
        if not unsubscribe_to_event(event_id=event.get("id")):
            return
    print(
        "Successfully unsubscribed from ",
        subscriptions.get("total"),
        " subscriptions",
    )
    return True


def unsubscribe_to_event(event_id: str):
    response = make_request(
        method="DELETE",
        url=URL,
        headers=get_headers(),
        params={"id": event_id},
    )
    if response.status_code in [200, 204]:
        return True


def create_user_cache(auth_code: str):
    user_access_token = get_user_access_token(code=auth_code)

    def check_if_user_cache_exists(channel_name):
        return RedisHandler().exists(key=channel_name)

    url = "https://api.twitch.tv/helix/users"
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "Client-Id": EnvWrapper().TWITCH_APP_ID,
    }
    response = make_request(
        method="GET",
        url=url,
        headers=headers,
        class_type=TwitchUsersQuery,
    )
    if response.data:
        user_data = response.data[0]

    user_cache = UserCache(
        twitch_channel_name=user_data.login,
        twitch_channel_id=user_data.id,
    )

    if not check_if_user_cache_exists(channel_name=user_cache.twitch_channel_name):
        RedisHandler().set_dict(
            name=user_cache.twitch_channel_name,
            payload=user_cache.model_dump(exclude_none=True),
        )
        print("User cache created")
