"""
@Time   : 2024/12/28 22:18
@Author : Leslie
@File   : auth_schema.py
"""

from flask_wtf import FlaskForm
from marshmallow import Schema, fields
from wtforms import StringField
from wtforms.validators import DataRequired, Email, Length


class PasswordLoginRequestSchema(FlaskForm):
    email = StringField(
        "email",
        validators=[
            DataRequired(message="登录邮箱不能为空"),
            Email(message="登录邮箱格式不正确"),
            Length(min=5, max=254, message="登录邮箱格式不正确"),
        ],
    )

    password = StringField(
        "password", validators=[DataRequired(message="登录密码不能为空")]
    )


class PasswordLoginResponseSchema(Schema):
    access_token = fields.String()
    expire_at = fields.Integer()
