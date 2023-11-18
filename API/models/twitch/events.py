from pydantic import BaseModel


class ConditionField(BaseModel, extra="allow"):
    broadcaster_user_id: str | None = None


class SubscriptionField(BaseModel, extra="allow"):
    id: str | None = None
    contidion: ConditionField | None = None
    type: str | None = None
    version: str | None = None
    cost: int | None = None


class RewardField(BaseModel, extra="allow"):
    id: str | None = None
    title: str | None = None
    cost: int | None = None


class EventInfo(BaseModel, extra="allow"):
    id: str | None = None
    broadcaster_user_id: str | None = None
    reward: RewardField | None = None
    user_input: str | None = None
    broadcaster_user_login: str | None = None


class Event(BaseModel):
    challenge: str | None = None
    subscription: SubscriptionField | None = None
    event: EventInfo | None = None
