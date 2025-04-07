import urllib.parse

from fastapi import HTTPException

CUSTOM_RESPONSES = {
    201: "Created",
    400: "Bad request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not found",
}


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


def give_status_response(
    status_code: int,
    custom_message: str | None = None,
) -> HTTPException:
    """
    This method allows you to provide a rest response at any given time.

    :param status_code: Int of the status code you want to return
    :param custom_message: (optional) String of the custom message you want to return
    """

    if not custom_message:
        if status_code in CUSTOM_RESPONSES:
            raise HTTPException(
                status_code=status_code,
                detail=CUSTOM_RESPONSES.get(status_code),
            )

        raise HTTPException(status_code=status_code)

    raise HTTPException(status_code=status_code, detail=custom_message)
