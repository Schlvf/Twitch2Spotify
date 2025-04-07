from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse

from .event_handler import solve_event
from .eventsub_handler import subscribe_to_event, unsubscribe_to_all
from .eventsub_models import Event
from .twitch_utils import (
    authenticate_hmac,
    check_dup_events,
    get_user_auth_params,
    url_encode_params,
)

router = APIRouter(prefix="/eventsub")


@router.post("/callback", status_code=200, response_class=PlainTextResponse)
async def callback_endpoint(
    request: Request,
    response: Response,
    event: Event,
):
    rawbody = await request.body()
    if not authenticate_hmac(request=request, rawbody=rawbody.decode()):
        print("Unauthorized petition")
        response.status_code = 401
        return

    print("\n*** Event triggered ***")

    # """REMOVE THIS LATER"""
    # import json

    # print("\n*** THIS IS A DEBUG MESSAGE ***\n")
    # print(json.dumps(event.model_dump(), indent=4))
    # print("\n*** END OF THE MESSAGE ***")

    if check_dup_events(event=event):
        print("*** SKIPPING DUP ***")
        return

    event_type = request.headers.get("Twitch-Eventsub-Message-Type")

    if event_type == "notification":
        print("*** Subscription received ***")
        solve_event(event=event)
    if event_type == "webhook_callback_verification":
        print("*** Challenge received ***")
        return event.challenge
    if event_type == "revocation":
        print("*** Revocation event ***")
    return


@router.get("/user_authorize")
async def user_authorization():
    url = "https://id.twitch.tv/oauth2/authorize"
    params = get_user_auth_params()
    return {"redirect_url": url + url_encode_params(params=params)}


@router.get("/twitch_auth")
async def twitch_auth(request: Request):
    print(await request.body())
    return {
        "Status": "Authorization successful",
        "Message": "This should be a one time process, now you can close this window",
    }


@router.post("/subscribe")
async def twitch_sub_event(event_name: str, channel_name: str):
    subscribe_to_event(
        event_name=event_name,
        channel_name=channel_name,
    )
    return {"Status": f"{event_name} Subscribed successfully"}


@router.delete("/subscribe")
async def twitch_unsub_event(response: Response):
    if not unsubscribe_to_all():
        response.status_code = 400
        return
    return {"Status": "Unsubscribed successfully"}
