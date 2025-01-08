"""
@Time   : 2025/01/08 22:43
@Author : Leslie
@File   : builtin_app_handler.py
"""

from dataclasses import dataclass
from injector import inject

from internal.core.builtin_apps.builtin_app_manager import BuiltinAppManager
from internal.schema.builtin_app_schema import AddBuiltinAppToSpaceReqSchema
from internal.service.builtin_app_service import BuiltinAppService
from pkg.response.response import success_json, validate_error_json
from flask_login import login_required, current_user


@inject
@dataclass
class BuiltinAppHandler:

    builtin_app_manager: BuiltinAppManager
    builtin_app_service: BuiltinAppService

    @login_required
    def get_builtin_app_categories(self):
        categories = self.builtin_app_manager.get_categories()
        result = [
            {
                "name": category.name,
                "category": category.category,
            }
            for category in categories
        ]
        return success_json(result)

    @login_required
    def get_builtin_apps(self):
        builtin_apps = self.builtin_app_manager.get_builtin_apps()
        result = [
            {
                "id": builtin_app.id,
                "name": builtin_app.name,
                "icon": builtin_app.icon,
                "description": builtin_app.description,
                "model_config": {
                    "provider": builtin_app.language_model_config.get("provider"),
                    "model": builtin_app.language_model_config.get("model"),
                },
                "created_at": builtin_app.created_at,
            }
            for builtin_app in builtin_apps
        ]
        return success_json(result)

    @login_required
    def add_builtin_app_to_space(self):
        req = AddBuiltinAppToSpaceReqSchema()
        if not req.validate():
            return validate_error_json(req.errors)

        app_id = self.builtin_app_service.add_builtin_app_to_space(
            req.builtin_app_id.data, current_user
        )
        return success_json({"id": app_id})
