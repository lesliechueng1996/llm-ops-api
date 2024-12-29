"""
@Time   : 2024/12/02 01:53
@Author : Leslie
@File   : app_service.py
"""

from internal.model.account import Account
from internal.schema.app_schema import CreateAppReqSchema
from pkg.sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from injector import inject
from internal.model.app import App, AppConfigVersion
from uuid import uuid4, UUID
from internal.entity.app_entity import AppStatus, AppConfigType, DEFAULT_APP_CONFIG
from internal.exception import NotFoundException


@inject
@dataclass
class AppService:
    db: SQLAlchemy

    def create_app(self, req: CreateAppReqSchema, account: Account) -> App:
        with self.db.auto_commit():
            app = App(
                account_id=account.id,
                name=req.name.data,
                description=req.description.data or "",
                icon=req.icon.data,
                status=AppStatus.DRAFT,
            )
            self.db.session.add(app)
            self.db.session.flush()

            app_config_version = AppConfigVersion(
                app_id=app.id,
                version=0,
                config_type=AppConfigType.DRAFT,
                **DEFAULT_APP_CONFIG,
            )
            self.db.session.add(app_config_version)
            self.db.session.flush()

            app.draft_app_config_id = app_config_version.id
        return app

    def get_app(self, id: UUID, account: Account):
        app = (
            self.db.session.query(App)
            .filter(App.id == id, App.account_id == account.id)
            .one_or_none()
        )

        if not app:
            raise NotFoundException("应用不存在")

        draft_app_config_id = app.draft_app_config_id
        app_config_version = (
            self.db.session.query(AppConfigVersion)
            .filter(
                AppConfigVersion.id == draft_app_config_id,
                AppConfigVersion.config_type == AppConfigType.DRAFT,
            )
            .one_or_none()
        )

        if app_config_version is None:
            with self.db.auto_commit():
                app_config_version = AppConfigVersion(
                    app_id=app.id,
                    version=0,
                    config_type=AppConfigType.DRAFT,
                    **DEFAULT_APP_CONFIG,
                )
                self.db.session.add(app_config_version)
                self.db.session.flush()
                app.draft_app_config_id = app_config_version.id
        return {
            "app": app,
            "draft_updated_at": app_config_version.updated_at,
        }

    def update_app(self, id: UUID) -> App:
        with self.db.auto_commit():
            app = self.get_app(id)
            app.name = "修改后的名字"
        return app

    def delete_app(self, id: UUID):
        with self.db.auto_commit():
            app = self.get_app(id)
            self.db.session.delete(app)
        return app
