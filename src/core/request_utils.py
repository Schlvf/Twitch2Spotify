from requests import request
from requests.models import Response

from .wrappers import custom_logger

METHODS = ["GET", "POST", "DELETE", "PUT"]


class RestHandler:
    @custom_logger
    def make_request(
        method: str,
        url: str,
        headers: dict,
        params: dict = None,
        body: dict = None,
        json: object = None,
    ) -> Response:
        if not RestHandler.is_valid_method(method=method):
            return

        request_data = {"method": method, "url": url, "headers": headers}
        if params:
            request_data["params"] = params
        if body:
            request_data["data"] = body
        if json:
            request_data["json"] = json

        result = request(**request_data)
        return result

    def is_valid_method(method: str):
        return method in METHODS
