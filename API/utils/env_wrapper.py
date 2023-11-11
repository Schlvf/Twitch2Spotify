import os

from dotenv import load_dotenv


class EnvWrapper:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            load_dotenv()
            cls.instance = super(EnvWrapper, cls).__new__(cls)

        return cls.instance

    def set_variable(self, key: str, value: str):
        os.environ[key] = value

    @property
    def DB_NAME(self):
        return os.getenv("db_name")

    @property
    def DB_CONN(self):
        return os.getenv("db_conn")

    @property
    def WEB_APP_PORT(self):
        return int(os.getenv("PORT"))

    @property
    def HMAC_SECRET(self):
        return os.getenv("hmac_secret")

    @property
    def TWITCH_APP_ID(self):
        return os.getenv("twitch_app_id")

    @property
    def TWITCH_APP_SECRET(self):
        return os.getenv("twitch_app_token")

    @property
    def OAUTH_TOKEN(self):
        return os.getenv("twitch_oauth_token")

    @property
    def EVENTSUB_CALLBACK(self):
        return os.getenv("twitch_app_callback_endpoint")

    @property
    def EVENTSUB_AUTH(self):
        return os.getenv("twitch_auth_endpoint")
