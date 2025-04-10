from typing import TypeVar

from requests import request
from requests.models import Response

METHODS = ["GET", "POST", "DELETE", "PUT"]
T = TypeVar("T")


def make_request(
    method: str,
    url: str,
    headers: dict,
    params: dict = None,
    body: dict = None,
    json: object = None,
    class_type: T | None = None,
) -> Response | T:
    if not is_valid_method(method=method):
        return

    request_data = {"method": method, "url": url, "headers": headers}
    if params:
        request_data["params"] = params
    if body:
        request_data["data"] = body
    if json:
        request_data["json"] = json

    result = request(**request_data)

    print("> status code: ", result.status_code)

    if class_type:
        try:
            return class_type(**result.json())
        except Exception:
            print(f"Unable to parse request into {class_type}")
    return result


def is_valid_method(method: str):
    return method in METHODS
