"""
@Time   : 2024/12/1 20:09
@Author : Leslie
@File   : response.py
"""

from typing import Any, Generator, Union
from dataclasses import field, dataclass
from flask import jsonify
from flask import Response as FlaskResponse, stream_with_context
from .http_code import HttpCode


@dataclass
class Response:
    code: HttpCode = HttpCode.SUCCESS
    message: str = ""
    data: Any = field(default_factory=dict)


def json(res: Response = None):
    return jsonify(res), 200


def success_json(data: Any = None):
    return json(Response(data=data))


def fail_json(data: Any = None):
    return json(Response(code=HttpCode.FAIL, data=data))


def validate_error_json(errors: dict = None):
    first_key = next(iter(errors))
    if first_key is not None:
        msg = errors.get(first_key)[0]
    else:
        msg = ""
    return json(Response(code=HttpCode.VALIDATE_ERROR, message=msg, data=errors))


def message(code: HttpCode = None, msg: str = ""):
    return json(Response(code=code, message=msg, data={}))


def success_message(msg: str = ""):
    return message(code=HttpCode.SUCCESS, msg=msg)


def fail_message(msg: str = ""):
    return message(code=HttpCode.FAIL, msg=msg)


def not_found_message(msg: str = ""):
    return message(code=HttpCode.NOT_FOUND, msg=msg)


def unauthorized_message(msg: str = ""):
    return message(code=HttpCode.UNAUTHORIZED, msg=msg)


def forbidden_message(msg: str = ""):
    return message(code=HttpCode.FORBIDDEN, msg=msg)


def compact_generate_response(response: Union[Generator, Response]) -> FlaskResponse:
    if isinstance(response, Response):
        return json(response)

    def generate() -> Generator:
        yield from response

    return FlaskResponse(
        stream_with_context(generate()),
        status=200,
        mimetype="text/event-stream",
    )
