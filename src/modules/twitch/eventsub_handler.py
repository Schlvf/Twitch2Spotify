from fastapi import HTTPException

from api import return_status_response
from core import make_request
from core.wrappers import EnvWrapper
from modules.redis.cache_models import UserCache
from modules.redis.redis_handler import RedisHandler

from .eventsub_models import EventSubSubscription
from .eventsub_models import EventSubSubscriptionsQuery
from .eventsub_models import TwitchUsersQuery
from .twitch_utils import get_channel_id
from .twitch_utils import get_headers
from .twitch_utils import get_subscription_body
from .twitch_utils import get_user_access_token

URL = "https://api.twitch.tv/helix/eventsub/subscriptions"
DEFAULT_EVENT = "channel.channel_points_custom_reward_redemption.add"


def subscribe_to_event(channel_name: str, event_name: str = DEFAULT_EVENT):
    user_id = get_channel_id(channel_name=channel_name)

    body = get_subscription_body(user_id=user_id, event_name=event_name)
    response = make_request(
        method="POST",
        url=URL,
        headers=get_headers(),
        json=body,
    )
    if response.status_code in [200, 202, 409]:
        print(f"Successfully subscribed {channel_name} to ", event_name)
        return

    raise HTTPException(
        status_code=400,
        detail="There was a problem, please try again",
    )


def unsubscribe_user(channel_name: str):
    user_id = get_channel_id(channel_name=channel_name)

    user_subscriptions = make_request(
        method="GET",
        url=URL,
        headers=get_headers(),
        params={"user_id": user_id},
        class_type=EventSubSubscriptionsQuery,
    )

    for event in user_subscriptions.data:
        unsubscribe_from_event(event=event)


def unsubscribe_from_all():
    total_subscriptions = make_request(
        method="GET",
        url=URL,
        headers=get_headers(),
        class_type=EventSubSubscriptionsQuery,
    )
    for event in total_subscriptions.data:
        unsubscribe_from_event(event=event)


def unsubscribe_from_event(event: EventSubSubscription):
    response = make_request(
        method="DELETE",
        url=URL,
        headers=get_headers(),
        params={"id": event.id},
    )
    if response.status_code in [200, 204]:
        print(f"Successfully unsubscribed from {event.type} with id {event.id}")
        return

    return_status_response(
        status_code=400,
        custom_message="Something went wrong when attemping to unsub from event",
    )


def create_user_cache(auth_code: str):
    """
    This method uses the code sent by twitch when the user completes the authorization process and creates the cache needed and finally returns the channel name.

    :param auth_code: String of the code sent by twitch during authorization
    """
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

    return user_cache.twitch_channel_name
