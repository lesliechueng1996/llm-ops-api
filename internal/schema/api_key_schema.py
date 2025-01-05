"""
@Time   : 2025/01/05 21:53
@Author : Leslie
@File   : api_key_schema.py
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField
from wtforms.validators import DataRequired, Length, Optional


class CreateApiKeyReqSchema(FlaskForm):
    is_active = BooleanField(
        "is_active", validators=[DataRequired(message="is_active不能为空")]
    )

    remark = StringField(
        "remark",
        validators=[
            Optional(),
            Length(
                min=0,
                max=100,
                message="remark长度必须在0到100之间",
            ),
        ],
    )
