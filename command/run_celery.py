import os

# 执行命令
os.system(
    "celery -A app.http.app.celery worker --loglevel DEBUG --concurrency 10 --pool threads --logfile storage/log/celery.log"
)
