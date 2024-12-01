"""
@Time   : 2024/12/1 20:06
@Author : Leslie
@File   : http_code.py
"""
from enum import Enum

class HttpCode(str, Enum):
    SUCCESS = "success"
    FAIL = "fail"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    VALIDATE_ERROR = "validate_error"