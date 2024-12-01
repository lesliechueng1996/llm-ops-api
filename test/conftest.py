"""
@Time   : 2024/12/1 21:36
@Author : Leslie
@File   : conftest.py
"""
import pytest

from app.http.app import app

@pytest.fixture()
def client():
    app.config.update({
        "TESTING": True,
    })
    with app.test_client() as client:
        yield client