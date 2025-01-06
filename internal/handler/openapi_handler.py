"""
@Time   : 2025/01/06 19:19
@Author : Leslie
@File   : openapi_handler.py
"""

from injector import inject
from dataclasses import dataclass
from pkg.response import success_message
from flask_login import login_required


@inject
@dataclass
class OpenapiHandler:

    @login_required
    def chat(self):
        return success_message("success")
