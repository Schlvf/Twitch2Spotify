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
    def WEB_APP_PORT(self):
        return int(os.getenv("PORT"))

    @property
    def TWITCH_HMAC_SECRET(self):
        return os.getenv("twitch_hmac_secret")

    @property
    def TWITCH_APP_ID(self):
        return os.getenv("twitch_app_id")

    @property
    def TWITCH_APP_SECRET(self):
        return os.getenv("twitch_app_secret")

    @property
    def GRIMM_SUBDOMAIN(self):
        return os.getenv("grimm_subdomain")

    @property
    def SPOTIFY_APP_ID(self):
        return os.getenv("spotify_app_id")

    @property
    def SPOTIFY_APP_SECRET(self):
        return os.getenv("spotify_app_secret")

    @property
    def REDIS_HOST(self):
        return os.getenv("redis_host")

    @property
    def SSL_KEY_FILE(self):
        return os.getenv("ssl_key_file")

    @property
    def SSL_CERT_FILE(self):
        return os.getenv("ssl_cert_file")

    @property
    def ENV(self):
        return os.getenv("ENV")
