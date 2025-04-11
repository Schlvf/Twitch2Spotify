from api import return_status_response
from core import EnvWrapper
from core import make_request
from modules.spotify import add_song_to_queue

from .eventsub_models import Event
from .eventsub_models import EventInfo
from .twitch_utils import get_user_cache

REDEMPTIONS_ENDPOINT = (
    "https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions"
)


def solve_event(event: Event):
    event_type = event.subscription.type

    if event_type == "channel.channel_points_custom_reward_redemption.add":
        solve_channel_points_event(event=event)
        return


def solve_channel_points_event(event: Event):
    reward_name = event.event.reward.title.lower()
    if "song request" in reward_name:
        link = event.event.user_input
        user_name = event.event.broadcaster_user_login

        response = add_song_to_queue(link=link, user_name=user_name)
        if response.get("error"):
            update_custom_reward_status(event_data=event.event, is_completed=False)
        return

    print("EVENT IGNORED")


def update_custom_reward_status(event_data: EventInfo, is_completed: bool = True):
    channel_name = event_data.broadcaster_user_login
    user_cache = get_user_cache(channel_name=channel_name)
    new_status = "FULFILLED" if is_completed else "CANCELED"

    if not user_cache:
        return_status_response(
            status_code=400,
            custom_message="Please re-authorize twitch before performing this action",
        )

    headers = {
        "Authorization": f"Bearer {user_cache.twitch_user_token}",
        "Client-Id": EnvWrapper().TWITCH_APP_ID,
    }
    params = {
        "id": event_data.id,
        "broadcaster_id": user_cache.twitch_channel_id,
        "reward_id": event_data.reward.id,
    }
    body = {"status": new_status}

    response = make_request(
        method="PATCH",
        url=REDEMPTIONS_ENDPOINT,
        headers=headers,
        params=params,
        body=body,
    )

    if response.status_code == 200:
        print(f"Reward by {event_data.user_name} updated to {new_status}")
    else:
        print(f"Failed to update custom reward status by {event_data.user_name}")
