import os
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv

from .custom_logger import get_logger_instance

logger = get_logger_instance("Custom Logger", "INFO")


def custom_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(e, extra={"Error class: ": type(e)})

    return wrapper


def time_diff(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            time_a = datetime.now()
            res = func(*args, **kwargs)
            time_b = datetime.now()
            time_delta = time_b - time_a

            print(f"REDIS - Task ended after {time_delta.total_seconds()} seconds")
            return res
        except Exception as e:
            # logger.error(e, extra={"Error class: ": type(e)})
            raise e

    return wrapper


class EnvWrapper:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            load_dotenv(override=True)
            cls.instance = super().__new__(cls)
        return cls.instance

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
    def APP_SUBDOMAIN(self):
        return os.getenv("app_subdomain")

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

    @property
    def SUDO_AUTH(self):
        return os.getenv("sudo_auth")
