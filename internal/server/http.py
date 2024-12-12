"""
@Time   : 2024/12/1 05:41
@Author : Leslie
@File   : http.py
"""

from flask import Flask
from pkg.sqlalchemy import SQLAlchemy
import traceback
from internal.exception import CustomException
from internal.router import Router
from config import Config
from pkg.response import json, Response, HttpCode
from flask_migrate import Migrate
from flask_cors import CORS


class Http(Flask):
    def __init__(
        self,
        *args,
        router: Router,
        config: Config,
        db: SQLAlchemy,
        migrate: Migrate,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        router.register_router(self)
        self.config.from_object(config)
        self.register_error_handler(Exception, self._error_handler)
        db.init_app(self)
        CORS(
            self,
            resources={
                r"/*": {
                    "origins": "*",
                    "supports_credentials": True,
                    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                    "allow_headers": [
                        "Content-Type",
                        "Authorization",
                        "Access-Control-Allow-Origin",
                    ],
                }
            },
        )
        migrate.init_app(self, db, directory="internal/migration")
        # with self.app_context():
        #     _ = App()
        #     db.create_all()

    def _error_handler(self, error: Exception):
        traceback.print_exception(error)
        if isinstance(error, CustomException):
            return json(
                Response(
                    code=error.code,
                    message=error.message,
                    data=error.data if error.data is not None else {},
                )
            )

        return json(Response(code=HttpCode.FAIL, message=str(error), data={}))
