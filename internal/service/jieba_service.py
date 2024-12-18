"""
@Time   : 2024/12/18 15:38
@Author : Leslie
@File   : jieba_service.py
"""

import jieba
from injector import inject
from dataclasses import dataclass
from internal.entity import STOPWORD_SET
import jieba.analyse


@inject
class JiebaService:
    def __init__(self):
        jieba.analyse.default_tfidf.stop_words = STOPWORD_SET

    def extract_keywords(self, text: str, max_keyword_per_chunk: int = 10) -> list[str]:
        return jieba.analyse.extract_tags(text, topK=max_keyword_per_chunk)
