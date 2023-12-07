from typing import Annotated

from fastapi import Header
from fastapi import HTTPException


async def sudo_auth(sudo_auth: Annotated[str, Header()]):
    if not sudo_auth:
        raise HTTPException(status_code=401, detail="Unauthorized operation")
    if sudo_auth != "fake-super-secret-token":
        raise HTTPException(status_code=403, detail="Forbidden")
