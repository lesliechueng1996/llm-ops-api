"""
@Time   : 2024/12/31 19:58
@Author : Leslie
@File   : ao_schema.py
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, UUID


class OptimizePromptReqSchema(FlaskForm):
    prompt = StringField(
        "prompt",
        validators=[
            DataRequired(message="prompt不能为空"),
            Length(max=2000, message="prompt长度不能超过2000"),
        ],
    )


class SuggestedQuestionsReqSchema(FlaskForm):
    message_id = StringField(
        "message_id",
        validators=[
            DataRequired(message="message_id不能为空"),
            UUID(message="message_id格式不正确"),
        ],
    )
