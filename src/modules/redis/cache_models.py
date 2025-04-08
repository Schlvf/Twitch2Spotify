from pydantic import BaseModel


class UserCache(BaseModel):
    twitch_channel_name: str
    twitch_channel_id: str

    twitch_user_token: str
    twitch_user_refresh_token: str
    twitch_user_token_expiration: float

    spotify_auth_token: str | None = None
    spotify_refresh_token: str | None = None
    spotify_expire_ts: float | None = None
