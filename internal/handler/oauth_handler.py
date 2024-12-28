"""
@Time   : 2024/12/28 18:32
@Author : Leslie
@File   : oauth_handler.py
"""

from dataclasses import dataclass
from injector import inject
from internal.service import OAuthService
from pkg.response import success_json, validate_error_json
from internal.schema import OAuthAuthorizeRequestSchema


@inject
@dataclass
class OAuthHandler:
    oauth_service: OAuthService

    def get_redirect_url(self, provider_name: str):
        oauth = self.oauth_service.get_oauth_by_provider_name(provider_name)
        return success_json({"redirect_url": oauth.get_authorization_url()})

    def authorize(self, provider_name: str):
        req = OAuthAuthorizeRequestSchema()
        if not req.validate():
            return validate_error_json(req.errors)

        result = self.oauth_service.oauth_login(provider_name, req.code.data)

        return success_json(result)
