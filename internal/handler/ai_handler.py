"""
@Time   : 2024/12/31 19:54
@Author : Leslie
@File   : ai_handler.py
"""

from injector import inject
from dataclasses import dataclass
from internal.schema import OptimizePromptReqSchema, SuggestedQuestionsReqSchema
from internal.service.ai_service import AIService
from pkg.response import success_json, validate_error_json, compact_generate_response
from flask_login import login_required, current_user


@inject
@dataclass
class AIHandler:
    ai_service: AIService

    @login_required
    def optimize_prompt(self):
        req = OptimizePromptReqSchema()
        if not req.validate():
            return validate_error_json(req.errors)

        res = self.ai_service.optimize_prompt(req.prompt.data)
        return compact_generate_response(res)

    @login_required
    def suggested_questions(self):
        req = SuggestedQuestionsReqSchema()
        if not req.validate():
            return validate_error_json(req.errors)

        suggestions = self.ai_service.generate_suggested_questions(
            req.message_id.data, current_user
        )

        return success_json(suggestions)
