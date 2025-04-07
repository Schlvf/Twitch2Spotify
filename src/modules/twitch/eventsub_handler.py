from fastapi import HTTPException

from core import RestHandler

from .twitch_utils import get_channel_id, get_headers, get_subscription_body

URL = "https://api.twitch.tv/helix/eventsub/subscriptions"


def subscribe_to_event(event_name: str, channel_name: str):
    user_id = get_channel_id(channel_name=channel_name)

    if not user_id:
        raise HTTPException(
            status_code=403,
            detail="Make sure the username is correct and try again",
        )

    body = get_subscription_body(user_id=user_id, event_name=event_name)
    response = RestHandler.make_request(
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
    response = RestHandler.make_request(
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
    response = RestHandler.make_request(
        method="DELETE",
        url=URL,
        headers=get_headers(),
        params={"id": event_id},
    )
    if response.status_code in [200, 204]:
        return True
