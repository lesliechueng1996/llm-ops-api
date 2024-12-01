"""
@Time   : 2024/12/1 05:41
@Author : Leslie
@File   : http.py
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from internal.exception import CustomException
from internal.router import Router
from config import Config
from pkg.response import json, Response, HttpCode


class Http(Flask):
    def __init__(self, *args, router: Router, config: Config, db: SQLAlchemy, **kwargs):
        super().__init__(*args, **kwargs)
        router.register_router(self)
        self.config.from_object(config)
        self.register_error_handler(Exception, self._error_handler)
        db.init_app(self)

    def _error_handler(self, error: Exception):
        if isinstance(error, CustomException):
            return json(Response(
                code=error.code,
                message=error.message,
                data=error.data if error.data is not None else {}
            ))

        return json(Response(code=HttpCode.FAIL, message=str(error), data={}))