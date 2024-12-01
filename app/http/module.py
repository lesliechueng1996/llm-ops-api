"""
@Time   : 2024/12/1 23:57
@Author : Leslie
@File   : module.py
"""
from flask_sqlalchemy import SQLAlchemy
from injector import Module, Binder
from internal.extension.database_extension import db

class ExtensionModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(SQLAlchemy, to=db)