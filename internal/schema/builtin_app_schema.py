"""
@Time   : 2025/01/08 23:04
@Author : Leslie
@File   : builtin_app_schema.py
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, UUID


class AddBuiltinAppToSpaceReqSchema(FlaskForm):

    builtin_app_id = StringField(
        "builtin_app_id",
        validators=[
            DataRequired(message="builtin_app_id 不能为空"),
            UUID(message="builtin_app_id 格式错误"),
        ],
    )
