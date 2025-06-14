from pydantic import BaseModel


class ConditionField(BaseModel):
    broadcaster_user_id: str | None = None


class SubscriptionField(BaseModel):
    id: str | None = None
    contidion: ConditionField | None = None
    type: str | None = None
    version: str | None = None
    cost: int | None = None


class RewardField(BaseModel):
    id: str | None = None
    title: str | None = None
    cost: int | None = None


class EventInfo(BaseModel):
    id: str | None = None
    broadcaster_user_id: str | None = None
    reward: RewardField | None = None
    user_input: str | None = None
    user_name: str | None = None
    broadcaster_user_login: str | None = None


class Event(BaseModel):
    challenge: str | None = None
    subscription: SubscriptionField | None = None
    event: EventInfo | None = None


class TwitchUser(BaseModel):
    id: str
    login: str
    display_name: str


class TwitchUsersQuery(BaseModel):
    data: list[TwitchUser | None]


class EventSubSubscription(BaseModel):
    id: str
    type: str
    status: str


class EventSubSubscriptionsQuery(BaseModel):
    total: int
    data: list[EventSubSubscription | None]


class CustomReward(BaseModel):
    id: str
    is_enabled: bool
    title: str
    is_user_input_required: bool
    cost: int
    prompt: str


class CustomRewardsQuery(BaseModel):
    data: list[CustomReward | None]


class TokenValidation(BaseModel):
    client_id: str
    login: str
    user_id: str
    scopes: list[str]
    expires_in: int
