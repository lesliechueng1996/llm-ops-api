"""
@Time   : 2024/12/13 20:35
@Author : Leslie
@File   : pagination.py
"""

from dataclasses import dataclass
from typing import Any
from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import Optional, NumberRange
from pkg.sqlalchemy import SQLAlchemy
import math


class PaginationReq(FlaskForm):
    current_page = IntegerField(
        "current_page",
        default=1,
        validators=[
            Optional(),
            NumberRange(min=1, max=9999, message="当前页码必须在1-9999之间"),
        ],
    )

    page_size = IntegerField(
        "page_size",
        default=20,
        validators=[
            Optional(),
            NumberRange(min=1, max=50, message="每页条数必须在1-50之间"),
        ],
    )


@dataclass
class Paginator:
    total_page: int = 0
    total_record: int = 0
    current_page: int = 1
    page_size: int = 20

    def __init__(self, db: SQLAlchemy, req: PaginationReq):
        if req is not None:
            self.current_page = req.current_page.data
            self.page_size = req.page_size.data
        self.db = db

    def paginate(self, query):
        page_result = self.db.paginate(
            query, page=self.current_page, per_page=self.page_size, error_out=False
        )

        self.total_record = page_result.total
        self.total_page = math.ceil(self.total_record / self.page_size)

        return page_result.items


@dataclass
class PageModel:
    list: list[Any]
    paginator: Paginator
