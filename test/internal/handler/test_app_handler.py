"""
@Time   : 2024/12/1 21:43
@Author : Leslie
@File   : test_app_handler.py
"""

import pytest
from flask.testing import FlaskClient

from pkg.response import HttpCode


class TestAppHandler:

    @pytest.mark.parametrize(
        "app_id, query",
        [
            ("8cc4a6de-b375-4a99-b9c8-c19ceefaf758", None),
            ("8cc4a6de-b375-4a99-b9c8-c19ceefaf758", "你好"),
        ],
    )
    def test_completion(self, client: FlaskClient, app_id, query):
        resp = client.post(f"/apps/{app_id}/debug", json={"query": query})
        print(resp.json)
        assert resp.status_code == 200
        if query is None:
            assert resp.json.get("code") == HttpCode.VALIDATE_ERROR
        else:
            assert resp.json.get("code") == HttpCode.SUCCESS
