"""
@Time   : 2024/12/28 13:13
@Author : Leslie
@File   : jwt_service.py
"""

from typing import Any
import jwt
from injector import inject
from dataclasses import dataclass
from os import getenv
import logging
from internal.exception import UnauthorizedException


@inject
@dataclass
class JWTService:
    """JWT服务类，用于处理JWT的编码和解码"""

    @classmethod
    def encode(cls, data: dict[str, Any]) -> str:
        secret_key = getenv("JWT_SECRET_KEY")
        return jwt.encode(data, secret_key, algorithm="HS256")

    @classmethod
    def decode(cls, token: str) -> dict[str, Any]:
        secret_key = getenv("JWT_SECRET KEY")

        try:
            return jwt.decode(token, secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            logging.error("Token has expired")
            raise UnauthorizedException("Token过期，请重新登录")
        except jwt.InvalidTokenError:
            logging.error("Invalid token")
            raise UnauthorizedException("无效的Token，请重新登录")
        except Exception as e:
            logging.error(f"Error decoding token: {e}")
            raise UnauthorizedException("请重新登录")
