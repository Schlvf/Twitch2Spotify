from typing import Annotated

from fastapi import Header

from core import EnvWrapper

from .api_utils import return_status_response


async def sudo_auth(sudo_auth: Annotated[str | None, Header()] = None):
    if not sudo_auth:
        return_status_response(status_code=401)
    if sudo_auth != EnvWrapper().SUDO_AUTH:
        return_status_response(status_code=403)
