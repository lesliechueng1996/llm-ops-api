"""
@Time   : 2025/01/08 22:10
@File   : builtin_app_entity.py
@Author : Leslie
"""

from pydantic import BaseModel, Field
from internal.entity.app_entity import DEFAULT_APP_CONFIG


class BuiltinAppEntity(BaseModel):
    id: str = Field(default="")
    name: str = Field(default="")
    icon: str = Field(default="")
    description: str = Field(default="")
    language_model_config: dict = Field(
        default_factory=lambda: DEFAULT_APP_CONFIG["model_config"]
    )
    dialog_round: int = Field(default=DEFAULT_APP_CONFIG["dialog_round"])
    preset_prompt: str = Field(default=DEFAULT_APP_CONFIG["preset_prompt"])
    tools: list[dict] = Field(default_factory=list)
    retrieval_config: dict = Field(
        default_factory=lambda: DEFAULT_APP_CONFIG["retrieval_config"]
    )
    long_term_memory: dict = Field(
        default_factory=lambda: DEFAULT_APP_CONFIG["long_term_memory"]
    )
    opening_statement: str = Field(default=DEFAULT_APP_CONFIG["opening_statement"])
    opening_questions: list[str] = Field(default_factory=list)
    speech_to_text: dict = Field(
        default_factory=lambda: DEFAULT_APP_CONFIG["speech_to_text"]
    )
    text_to_speech: dict = Field(
        default_factory=lambda: DEFAULT_APP_CONFIG["text_to_speech"]
    )
    suggested_after_answer: dict = Field(
        default_factory=lambda: DEFAULT_APP_CONFIG["suggested_after_answer"]
    )
    review_config: dict = Field(
        default_factory=lambda: DEFAULT_APP_CONFIG["review_config"]
    )
    created_at: int = Field(default=0)
