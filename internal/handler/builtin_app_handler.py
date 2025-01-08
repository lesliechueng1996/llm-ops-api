"""
@Time   : 2025/01/08 22:43
@Author : Leslie
@File   : builtin_app_handler.py
"""

from dataclasses import dataclass
from injector import inject

from internal.core.builtin_apps.builtin_app_manager import BuiltinAppManager
from pkg.response.response import success_json
from flask_login import login_required


@inject
@dataclass
class BuiltinAppHandler:

    builtin_app_manager: BuiltinAppManager

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
