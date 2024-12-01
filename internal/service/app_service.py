"""
@Time   : 2024/12/02 01:53
@Author : Leslie
@File   : app_service.py
"""

from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from injector import inject
from internal.model.app import App
from uuid import uuid4, UUID


@inject
@dataclass
class AppService:
    db: SQLAlchemy

    def create_app(self) -> App:
        app = App(
            account_id=uuid4(), name="AI应用", icon="icon", description="AI应用描述"
        )
        self.db.session.add(app)
        self.db.session.commit()
        return app

    def get_app(self, id: UUID) -> App:
        app = self.db.session.query(App).get(id)
        return app

    def update_app(self, id: UUID) -> App:
        app = self.get_app(id)
        app.name = "修改后的名字"
        self.db.session.commit()
        return app

    def delete_app(self, id: UUID):
        app = self.get_app(id)
        self.db.session.delete(app)
        self.db.session.commit()
        return app
