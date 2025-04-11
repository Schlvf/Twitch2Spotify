from pydantic import BaseModel


class OauthToken(BaseModel):
    access_token: str
    expires_in: int | None = None
    token_type: str
    refresh_token: str | None = None
