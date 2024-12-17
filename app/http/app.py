"""
@Time   : 2024/12/1 05:45
@Author : Leslie
@File   : app.py
"""

from flask_migrate import Migrate
from pkg.sqlalchemy import SQLAlchemy
from injector import Injector
from dotenv import load_dotenv

from .module import ExtensionModule
from config import Config
from internal.router import Router
from internal.server import Http

load_dotenv()

injector = Injector([ExtensionModule])

app = Http(
    __name__,
    router=injector.get(Router),
    config=Config(),
    db=injector.get(SQLAlchemy),
    migrate=injector.get(Migrate),
)

celery = app.extensions["celery"]

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
