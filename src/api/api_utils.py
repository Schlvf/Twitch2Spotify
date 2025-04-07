import urllib.parse

from fastapi import HTTPException


def url_encode_params(params: dict):
    return "?" + urllib.parse.urlencode(params)


class ResponseMessage:
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


class StatusResponse:
    def created():
        raise HTTPException(status_code=201, detail="Created")

    def bad_request():
        raise HTTPException(status_code=400, detail="Bad request")

    def unauthorized():
        raise HTTPException(status_code=401, detail="Unauthorized")

    def forbidden():
        raise HTTPException(status_code=403, detail="Forbidden")

    def not_found():
        raise HTTPException(status_code=404, detail="Not found")
