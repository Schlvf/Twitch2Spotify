from datetime import datetime
from functools import wraps

from Core.custom_logger import get_logger_instance

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

            print(f"    >   Task ended after {time_delta.total_seconds()} seconds")
            return res
        except Exception as e:
            # logger.error(e, extra={"Error class: ": type(e)})
            raise e

    return wrapper
