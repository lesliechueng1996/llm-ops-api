"""
@Time   : 2024/12/1 05:45
@Author : Leslie
@File   : app.py
"""
from injector import Injector
from dotenv import load_dotenv

from internal.router import Router
from internal.server import Http

app = Http(__name__, router=Injector().get(Router))

if __name__ == "__main__":
    load_dotenv()
    app.run(debug=True, host="0.0.0.0", port=8000)
