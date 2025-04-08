from pydantic import BaseModel


class OauthToken(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    refresh_token: str | None = None
