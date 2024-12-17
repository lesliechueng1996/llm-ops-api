import os

# 执行命令
os.system(
    "celery -A app.http.app.celery worker --loglevel INFO --logfile storage/log/celery.log"
)
