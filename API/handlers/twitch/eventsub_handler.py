from API.utils import twitch_utils
from Core.rest_helper.request_utils import RestHandler

URL = "https://api.twitch.tv/helix/eventsub/subscriptions"


def subscribe_to_event(event_name: str, channel_name: str):
    user_id = twitch_utils.get_channel_id(channel_name=channel_name)
    body = twitch_utils.get_subscription_body(user_id=user_id, event_name=event_name)
    response = RestHandler.make_request(
        method="POST",
        url=URL,
        headers=twitch_utils.get_headers(),
        json=body,
    )
    print(response.json())
    print(response.status_code)
    if response.status_code in [200, 202, 409]:
        print("Successfully subscribed to ", event_name)
        return True


def unsubscribe_to_all():
    response = RestHandler.make_request(
        method="GET",
        url=URL,
        headers=twitch_utils.get_headers(),
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
    response = RestHandler.make_request(
        method="DELETE",
        url=URL,
        headers=twitch_utils.get_headers(),
        params={"id": event_id},
    )
    if response.status_code in [200, 204]:
        return True
