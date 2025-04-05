from typing import Annotated

from fastapi import Header, HTTPException

from API.utils.env_wrapper import EnvWrapper


async def sudo_auth(sudo_auth: Annotated[str | None, Header()] = None):
    if not sudo_auth:
        raise HTTPException(status_code=401, detail="Unauthorized operation")
    if sudo_auth != EnvWrapper().SUDO_AUTH:
        raise HTTPException(status_code=403, detail="Forbidden")
