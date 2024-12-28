"""
@Time   : 2024/12/28 21:33
@Author : Leslie
@File   : account_schema.py
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, regexp, Length, URL
from marshmallow import Schema, fields, pre_dump
from internal.lib.helper import datetime_to_timestamp
from internal.model.account import Account
from pkg.password import password_pattern


class GetAccountResponseSchema(Schema):
    id = fields.UUID()
    name = fields.String()
    email = fields.String()
    avatar = fields.String()
    last_login_at = fields.Integer()
    last_login_ip = fields.String()
    created_at = fields.Integer()

    @pre_dump
    def process_data(self, account: Account, **kwargs):
        return {
            "id": account.id,
            "name": account.name,
            "email": account.email,
            "avatar": account.avatar,
            "last_login_at": datetime_to_timestamp(account.last_login_at),
            "last_login_ip": account.last_login_ip,
            "created_at": datetime_to_timestamp(account.created_at),
        }


class UpdatePasswordRequestSchema(FlaskForm):
    password = StringField(
        "password",
        validators=[
            DataRequired("登录密码不能为空"),
            regexp(
                regex=password_pattern,
                message="密码最少包含一个字母，一个数字，并且长度为8-16位",
            ),
        ],
    )


class UpdateNameRequestSchema(FlaskForm):
    name = StringField(
        "name",
        validators=[
            DataRequired("名称不能为空"),
            Length(min=3, max=30, message="名称长度为3-30位"),
        ],
    )


class UpdateAvatarRequestSchema(FlaskForm):
    avatar = StringField(
        "avatar",
        validators=[
            DataRequired("头像连接不能为空"),
            URL("头像连接格式不正确"),
        ],
    )
