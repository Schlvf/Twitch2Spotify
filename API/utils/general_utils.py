import urllib.parse


def url_encode_params(params: dict):
    return "?" + urllib.parse.urlencode(params)


def get_successful_auth_message():
    return {
        "Status": "Authorization successful",
        "Message": "This should be a one time process, now you can close this window",
    }


def get_unsuccessful_auth_message():
    return {
        "Status": "Authorization denied",
        "Message": "You can authorize the app later on, now you can close this window",
    }


def send_code_message(code: str):
    return {
        "Status": "PLEASE COPY THE FOLLOWING CODE, YOU WILL NEED IT",
        "Code": code,
    }


def send_code_error(error: str):
    return {
        "Status": "Something went wrong, please inform Schlvf if you're seeing this message",
        "error_msg": error,
    }
