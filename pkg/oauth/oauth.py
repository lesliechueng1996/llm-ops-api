"""
@Time   : 2024/12/28 17:24
@Author : Leslie
@File   : oauth.py
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class OAuthUserInfo:
    id: str
    name: str
    email: str


@dataclass
class OAuth(ABC):

    client_id: str
    client_secret: str
    redirect_uri: str

    @abstractmethod
    def get_provider(self) -> str:
        pass

    @abstractmethod
    def get_authorization_url(self) -> str:
        pass

    @abstractmethod
    def get_access_token(self, code: str) -> str:
        pass

    @abstractmethod
    def get_raw_user_info(self, token: str) -> dict:
        pass

    def get_user_info(self, token: str) -> OAuthUserInfo:
        raw_info = self.get_raw_user_info(token)
        return self._transform_user_info(raw_info)

    @abstractmethod
    def _transform_user_info(self, raw_info: dict) -> OAuthUserInfo:
        pass
