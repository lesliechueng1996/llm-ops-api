"""
@Time   : 2024/12/28 21:28
@Author : Leslie
@File   : account_handler.py
"""

from injector import inject
from dataclasses import dataclass
from flask_login import current_user, login_required
from internal.schema.account_schema import (
    GetAccountResponseSchema,
    UpdatePasswordRequestSchema,
    UpdateNameRequestSchema,
    UpdateAvatarRequestSchema,
)
from internal.service import AccountService
from pkg.response.response import success_json, success_message, validate_error_json


@inject
@dataclass
class AccountHandler:

    account_service: AccountService

    @login_required
    def get_account(self):
        return success_json(GetAccountResponseSchema().dump(current_user))

    @login_required
    def update_password(self):
        req = UpdatePasswordRequestSchema()
        if not req.validate():
            return validate_error_json(req.errors)

        self.account_service.update_password(current_user, req.password.data)
        return success_message("密码修改成功")

    @login_required
    def update_name(self):
        req = UpdateNameRequestSchema()
        if not req.validate():
            return validate_error_json(req.errors)

        self.account_service.update_name(current_user, req.name.data)
        return success_message("名称修改成功")

    @login_required
    def update_avatar(self):
        req = UpdateAvatarRequestSchema()
        if not req.validate():
            return validate_error_json(req.errors)

        self.account_service.update_avatar(current_user, req.avatar.data)
        return success_message("头像修改成功")
