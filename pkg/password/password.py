"""
@Time   : 2024/12/28 13:24
@Author : Leslie
@File   : password.py
"""

import base64
import binascii
import hashlib
import re
from typing import Any


password_pattern = r"^(?=.*[a-zA-Z])(?=.*\d).{8,16}$"


def validate_password(password: str, pattern: str = password_pattern) -> bool:
    return re.match(pattern, password) is not None


def hash_password(password: str, salt: Any) -> bytes:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return binascii.hexlify(dk)


def compare_password(
    password: str, password_hashed_base64: str, salt_base64: str
) -> bool:
    salt = base64.b64decode(salt_base64)
    password_hashed = hash_password(password, salt)
    return password_hashed == base64.b64decode(password_hashed_base64)
