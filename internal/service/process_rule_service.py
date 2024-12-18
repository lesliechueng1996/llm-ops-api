"""
@Time   : 2024/12/19 02:59
@Author : Leslie
@File   : process_rule_service.py
"""

import re
from injector import inject
from dataclasses import dataclass
from internal.model import ProcessRule
from typing import Callable
from langchain_text_splitters import TextSplitter, RecursiveCharacterTextSplitter
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class ProcessRuleService:
    db: SQLAlchemy

    def get_text_splitter_by_process_rule(
        self,
        process_rule: ProcessRule,
        length_function: Callable[[str], int] = len,
        **kwargs,
    ) -> TextSplitter:
        process_rule_segment = process_rule.rule["segment"]
        return RecursiveCharacterTextSplitter(
            chunk_size=process_rule_segment["chunk_size"],
            chunk_overlap=process_rule_segment["chunk_overlap"],
            separators=process_rule_segment["separators"],
            is_separator_regex=True,
            length_function=length_function,
            **kwargs,
        )

    def clean_text_by_process_rule(self, process_rule: ProcessRule, text: str) -> str:
        for pre_process_rule in process_rule.rule["pre_process_rules"]:
            # 2.删除多余空格
            if (
                pre_process_rule["id"] == "remove_extra_space"
                and pre_process_rule["enabled"] is True
            ):
                pattern = r"\n{3,}"
                text = re.sub(pattern, "\n\n", text)
                pattern = (
                    r"[\t\f\r\x20\u00a0\u1680\u180e\u2000-\u200a\u202f\u205f\u3000]{2,}"
                )
                text = re.sub(pattern, " ", text)
            # 3.删除多余的URL链接及邮箱
            if (
                pre_process_rule["id"] == "remove_url_and_email"
                and pre_process_rule["enabled"] is True
            ):
                pattern = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
                text = re.sub(pattern, "", text)
                pattern = r"https?://[^\s]+"
                text = re.sub(pattern, "", text)
        return text
