"""
@Time   : 2024/12/28 18:34
@Author : Leslie
@File   : oauth_service.py
"""

from injector import inject
from dataclasses import dataclass
from pkg.oauth import GithubOAuth
from os import getenv
from internal.exception import NotFoundException


@inject
@dataclass
class OAuthService:
    def get_all_oauth(self):
        github = GithubOAuth(
            client_id=getenv("GITHUB_CLIENT_ID"),
            client_secret=getenv("GITHUB_CLIENT_SECRET"),
            redirect_uri=getenv("GITHUB_REDIRECT_URI"),
        )

        return {"github": github}

    def get_oauth_by_provider_name(self, provider_name: str):
        oauth = self.get_all_oauth().get(provider_name)
        if oauth is None:
            raise NotFoundException(f"该授权方式[{provider_name}]不存在")
        return oauth
