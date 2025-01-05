"""
@Time   : 2025/01/05 21:51
@Author : Leslie
@File   : api_key_handler.py
"""

from uuid import UUID
from injector import inject
from dataclasses import dataclass
from internal.schema.api_key_schema import (
    CreateApiKeyReqSchema,
    UpdateApiKeyActiveReqSchema,
    UpdateApiKeyReqSchema,
)
from internal.service import ApiKeyService
from pkg.response import validate_error_json, success_message
from flask_login import login_required, current_user


@inject
@dataclass
class ApiKeyHandler:

    api_key_service: ApiKeyService

    @login_required
    def create_api_key(self):
        req = CreateApiKeyReqSchema()
        if not req.validate():
            return validate_error_json(req.errors)
        self.api_key_service.create_api_key(req, current_user)
        return success_message("创建成功")

    @login_required
    def delete_api_key(self, api_key_id: UUID):
        self.api_key_service.delete_api_key(api_key_id, current_user)
        return success_message("删除成功")

    @login_required
    def update_api_key(self, api_key_id: UUID):
        req = UpdateApiKeyReqSchema()
        if not req.validate():
            return validate_error_json(req.errors)
        self.api_key_service.update_api_key(api_key_id, req, current_user)
        return success_message("更新成功")

    @login_required
    def update_api_key_active(self, api_key_id: UUID):
        req = UpdateApiKeyActiveReqSchema()
        if not req.validate():
            return validate_error_json(req.errors)
        self.api_key_service.update_api_key_active(
            api_key_id, req.is_active.data, current_user
        )
        return success_message("更新成功")
