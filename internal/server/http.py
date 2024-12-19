"""
@Time   : 2024/12/1 05:41
@Author : Leslie
@File   : http.py
"""

from flask import Flask
from pkg.sqlalchemy import SQLAlchemy
import logging
from internal.exception import CustomException
from internal.extension import logging_extension
from internal.extension import redis_extension
from internal.extension import celery_extension
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

        self.config.from_object(config)

        self.register_error_handler(Exception, self._error_handler)

        db.init_app(self)
        migrate.init_app(self, db, directory="internal/migration")
        redis_extension.init_app(self)
        celery_extension.init_app(self)
        logging_extension.init_app(self)

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
        router.register_router(self)

    def _error_handler(self, error: Exception):
        logging.error("An error occurred: %s", error, exc_info=True)
        if isinstance(error, CustomException):
            return json(
                Response(
                    code=error.code,
                    message=error.message,
                    data=error.data if error.data is not None else {},
                )
            )

        return json(Response(code=HttpCode.FAIL, message=str(error), data={}))
