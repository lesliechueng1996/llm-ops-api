from flask import Flask
from os import path, getcwd, makedirs, getenv
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter, INFO, getLogger, StreamHandler


def init_app(app: Flask):
    log_folder = path.join(getcwd(), "storage", "log")
    if not path.exists(log_folder):
        makedirs(log_folder)

    log_file = path.join(log_folder, "app.log")

    handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    fomatter = Formatter(
        "[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s]: %(message)s"
    )
    handler.setLevel(INFO)
    handler.setFormatter(fomatter)
    getLogger().addHandler(handler)

    if app.debug or getenv("FLASK_ENV") == "development":
        console_handler = StreamHandler()
        console_handler.setFormatter(fomatter)
        getLogger().addHandler(console_handler)
