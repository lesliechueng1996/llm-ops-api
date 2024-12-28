"""
@Time   : 2024/12/28 18:52
@Author : Leslie
@File   : oauth_schema.py
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from marshmallow import Schema, fields


class OAuthAuthorizeRequestSchema(FlaskForm):
    code = StringField("code", validators=[DataRequired(message="code不能为空")])


class OAuthAuthorizeResponseSchema(Schema):
    access_token = fields.String()
    expire_at = fields.Integer()
