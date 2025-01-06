"""
@Time   : 2025/01/06 19:19
@Author : Leslie
@File   : openapi_handler.py
"""

from injector import inject
from dataclasses import dataclass
from internal.schema.openapi_schema import OpenapiChatReqSchema
from internal.service.openapi_service import OpenapiService
from pkg.response import success_message, validate_error_json, compact_generate_response
from flask_login import login_required, current_user


@inject
@dataclass
class OpenapiHandler:

    openapi_service: OpenapiService

    @login_required
    def chat(self):
        req = OpenapiChatReqSchema()
        if not req.validate():
            return validate_error_json(req.errors)

        res = self.openapi_service.chat(req, current_user)
        return compact_generate_response(res)
