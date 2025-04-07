from typing import Annotated

from fastapi import Header

from core import EnvWrapper

from .api_utils import StatusResponse


async def sudo_auth(sudo_auth: Annotated[str | None, Header()] = None):
    if not sudo_auth:
        StatusResponse.unauthorized()
    if sudo_auth != EnvWrapper().SUDO_AUTH:
        StatusResponse.forbidden()
