from fastapi import HTTPException

from api import return_status_response
from core import make_request
from core.wrappers import EnvWrapper
from modules.redis.cache_models import UserCache
from modules.redis.redis_handler import RedisHandler

from .eventsub_models import CustomReward
from .eventsub_models import CustomRewardsQuery
from .eventsub_models import EventSubSubscription
from .eventsub_models import EventSubSubscriptionsQuery
from .eventsub_models import TwitchUser
from .eventsub_models import TwitchUsersQuery
from .twitch_utils import get_headers
from .twitch_utils import get_subscription_body
from .twitch_utils import get_user_access_token
from .twitch_utils import get_user_cache
from .twitch_utils import parse_token_data_into_cache
from .twitch_utils import parse_user_data_into_cache

URL = "https://api.twitch.tv/helix/eventsub/subscriptions"
DEFAULT_EVENT = "channel.channel_points_custom_reward_redemption.add"


def subscribe_to_event(channel_name: str, event_name: str = DEFAULT_EVENT):
    cached_user = get_user_cache(channel_name=channel_name)

    if event_name == DEFAULT_EVENT:
        song_request_reward = get_or_create_song_request_reward(user_cache=cached_user)
        if not song_request_reward.is_enabled:
            song_request_reward = set_reward_status(
                reward=song_request_reward,
                user_cache=cached_user,
                is_enabled=True,
            )
        reward_id = song_request_reward.id

    body = get_subscription_body(
        user_id=cached_user.twitch_channel_id,
        event_name=event_name,
        reward_id=reward_id,
    )
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
    cached_user = get_user_cache(channel_name=channel_name)

    song_request_reward = get_or_create_song_request_reward(user_cache=cached_user)
    if song_request_reward.is_enabled:
        song_request_reward = set_reward_status(
            reward=song_request_reward,
            user_cache=cached_user,
            is_enabled=False,
        )

    user_subscriptions = make_request(
        method="GET",
        url=URL,
        headers=get_headers(),
        params={"user_id": cached_user.twitch_channel_id},
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


def authorize_twitch_user(auth_code: str):
    """
    This method uses the code sent by twitch when the user completes the authorization process and creates the cache needed and finally returns the channel name.

    :param auth_code: String of the code sent by twitch during authorization
    """

    user_access_token = get_user_access_token(code=auth_code)
    user_data = get_user_data(user_access_token=user_access_token.access_token)

    user_cache = RedisHandler().get_dict(name=user_data.login, class_type=UserCache)

    if not user_cache:
        user_cache = parse_user_data_into_cache(
            new_user=user_data,
            new_token=user_access_token,
        )
        print("New user cache created")
    else:
        user_cache = parse_token_data_into_cache(
            user_cache=user_cache,
            new_token=user_access_token,
        )
        print("User cache updated")

    RedisHandler().set_dict(
        name=user_cache.twitch_channel_name,
        payload=user_cache.model_dump(exclude_none=True),
    )
    return user_cache.twitch_channel_name


def get_user_data(user_access_token: str) -> TwitchUser:
    url = "https://api.twitch.tv/helix/users"
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "Client-Id": EnvWrapper().TWITCH_APP_ID,
    }
    users = make_request(
        method="GET",
        url=url,
        headers=headers,
        class_type=TwitchUsersQuery,
    )
    if not users.data:
        return_status_response(
            status_code=400,
            custom_message="There was an issue obtaining the user data",
        )

    return users.data[0]


def get_or_create_song_request_reward(user_cache: UserCache) -> CustomReward:
    url = "https://api.twitch.tv/helix/channel_points/custom_rewards"
    headers = {
        "Authorization": f"Bearer {user_cache.twitch_user_token}",
        "Client-Id": EnvWrapper().TWITCH_APP_ID,
    }
    params = {
        "broadcaster_id": user_cache.twitch_channel_id,
    }
    current_rewards = make_request(
        method="GET",
        url=url,
        headers=headers,
        params=params,
        class_type=CustomRewardsQuery,
    )
    if not isinstance(current_rewards, CustomRewardsQuery):
        return_status_response(
            status_code=400,
            custom_message="Twitch has refused this action or your session has expired",
        )
    # This is an order O(n) search to find the first match that contains song request in the title
    # Opted to use next() given that it is implemented in C and avoids python-level overhead
    song_request_reward = next(
        (reward for reward in current_rewards.data if "song request" in reward.title),
        None,
    )

    if not song_request_reward:
        new_rewards = make_request(
            method="POST",
            url=url,
            headers=headers,
            params=params,
            body=get_new_song_request_reward_dict(),
            class_type=CustomRewardsQuery,
        )
        if not isinstance(new_rewards, CustomRewardsQuery):
            return_status_response(
                status_code=400,
                custom_message="Something went wrong creating the custom channel point reward",
            )
        song_request_reward = new_rewards.data[0]

    return song_request_reward


def get_new_song_request_reward_dict():
    return {
        "title": "Spotify song request",
        "cost": 100,
        "prompt": "Copy the link of the song directly from Spotify. PLAYLIST OR ALBUMS WON'T WORK",
        "is_user_input_required": True,
    }


def set_reward_status(
    reward: CustomReward,
    user_cache: UserCache,
    is_enabled: bool = True,
) -> CustomReward:
    url = "https://api.twitch.tv/helix/channel_points/custom_rewards"
    headers = {
        "Authorization": f"Bearer {user_cache.twitch_user_token}",
        "Client-Id": EnvWrapper().TWITCH_APP_ID,
    }
    params = {
        "broadcaster_id": user_cache.twitch_channel_id,
        "id": reward.id,
    }
    body = {"is_enabled": is_enabled}
    updated_reward = make_request(
        method="PATCH",
        url=url,
        headers=headers,
        params=params,
        body=body,
        class_type=CustomRewardsQuery,
    )
    if not isinstance(updated_reward, CustomRewardsQuery):
        return_status_response(
            status_code=400,
            custom_message="Twitch has refused this action or your session has expired",
        )
    return updated_reward.data[0]
