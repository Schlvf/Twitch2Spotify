from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import Response
from fastapi.responses import PlainTextResponse

from api import ResponseMessage
from api import sudo_auth

from .event_handler import solve_event
from .eventsub_handler import authorize_twitch_user
from .eventsub_handler import subscribe_to_event
from .eventsub_handler import unsubscribe_from_all
from .eventsub_handler import unsubscribe_user
from .eventsub_models import Event
from .twitch_utils import authenticate_hmac
from .twitch_utils import check_dup_events
from .twitch_utils import get_twitch_auth_url

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
    return {"redirect_url": get_twitch_auth_url()}


@router.get("/twitch_auth")
async def twitch_auth(code: str | None = None):
    if not code:
        return ResponseMessage.get_unsuccessful_auth_message()

    user_name = authorize_twitch_user(auth_code=code)

    print(f"The user subscribed was {user_name}")
    return ResponseMessage.get_successful_auth_message()


@router.get("/enable_integration/{channel_name}")
async def enable_spotify_integration(channel_name: str):
    subscribe_to_event(channel_name=channel_name)
    return {"Status": "Integration successfully enabled"}


@router.get("/disable_integration/{channel_name}")
async def disable_spotify_integration(channel_name: str):
    unsubscribe_user(channel_name=channel_name)
    return {"Status": "Integration successfully disabled"}


@router.delete("/unsubscribe_from_all", dependencies=[Depends(sudo_auth)])
async def unsubscribe_from_all_events():
    unsubscribe_from_all()
    return {"Status": "Removed all subscriptions"}
