"""
@Time   : 2024/12/13 11:56
@Author : Leslie
@File   : api_tool_schema.py
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class ValidationOpenAPISchemaReq(FlaskForm):
    openapi_schema = StringField(
        "openapi_schema",
        validators=[
            DataRequired(message="openapi_schema字段不能为空"),
        ],
    )
