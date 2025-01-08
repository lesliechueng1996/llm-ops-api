"""
@Time   : 2025/01/08 23:07
@Author : Leslie
@File   : builtin_app_service.py
"""

from dataclasses import dataclass
from injector import inject
from internal.core.builtin_apps.builtin_app_manager import BuiltinAppManager
from internal.entity.app_entity import AppConfigType, AppStatus
from internal.exception import NotFoundException
from internal.model.account import Account
from internal.model.app import App, AppConfigVersion
from pkg.sqlalchemy.sqlalchemy import SQLAlchemy


@inject
@dataclass
class BuiltinAppService:

    db: SQLAlchemy
    builtin_app_manager: BuiltinAppManager

    def add_builtin_app_to_space(self, builtin_app_id: str, account: Account) -> str:
        builtin_app = self.builtin_app_manager.get_builtin_app(builtin_app_id)
        if not builtin_app:
            raise NotFoundException("内置应用不存在")

        with self.db.auto_commit():
            app = App(
                account_id=account.id,
                name=builtin_app.name,
                icon=builtin_app.icon,
                description=builtin_app.description,
                status=AppStatus.DRAFT,
            )
            self.db.session.add(app)
            self.db.session.flush()

            draft_app_config = AppConfigVersion(
                app_id=app.id,
                model_config=builtin_app.language_model_config,
                dialog_round=builtin_app.dialog_round,
                preset_prompt=builtin_app.preset_prompt,
                tools=builtin_app.tools,
                workflows=[],
                datasets=[],
                retrieval_config=builtin_app.retrieval_config,
                long_term_memory=builtin_app.long_term_memory,
                opening_statement=builtin_app.opening_statement,
                opening_questions=builtin_app.opening_questions,
                speech_to_text=builtin_app.speech_to_text,
                text_to_speech=builtin_app.text_to_speech,
                suggested_after_answer=builtin_app.suggested_after_answer,
                review_config=builtin_app.review_config,
                version=0,
                config_type=AppConfigType.DRAFT,
            )
            self.db.session.add(draft_app_config)
            self.db.session.flush()

            app.draft_app_config_id = draft_app_config.id

        return app.id
