"""
@Time   : 2024/12/1 05:45
@Author : Leslie
@File   : app.py
"""

from flask_login import LoginManager
from flask_migrate import Migrate
from internal.middleware import Middleware
from pkg.sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from config import Config
from internal.router import Router
from internal.server import Http
from .module import injector

load_dotenv()


app = Http(
    __name__,
    router=injector.get(Router),
    config=Config(),
    db=injector.get(SQLAlchemy),
    migrate=injector.get(Migrate),
    login_manager=injector.get(LoginManager),
    middleware=injector.get(Middleware),
)

celery = app.extensions["celery"]

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
