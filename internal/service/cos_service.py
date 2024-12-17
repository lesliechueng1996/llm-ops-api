"""
@Time   : 2024/12/17 14:43
@Author : Leslie
@File   : cos_service.py
"""

from injector import inject, singleton
from qcloud_cos import CosConfig, CosS3Client
from os import getenv
from werkzeug.datastructures import FileStorage
from internal.entity import ALLOWED_IMAGE_EXTENSIONS, ALLOWED_DOCUMENT_EXTENSIONS
from internal.exception import FailException
from datetime import datetime
from uuid import uuid4
from hashlib import sha3_256


@inject
@singleton
class CosService:
    client: CosS3Client = None

    def __init__(self):
        pass

    def upload_file(self, file: FileStorage, only_image: bool = False):
        try:
            client = self._get_client()
            file_name = file.filename
            ext_name = file_name.split(".")[-1] if "." in file_name else ""
            if only_image and ext_name not in ALLOWED_IMAGE_EXTENSIONS:
                raise FailException(
                    f"仅支持上传{'/'.join(ALLOWED_IMAGE_EXTENSIONS)}格式的图片"
                )

            if not only_image and ext_name not in ALLOWED_DOCUMENT_EXTENSIONS:
                raise FailException(
                    f"仅支持上传{'/'.join(ALLOWED_DOCUMENT_EXTENSIONS)}格式的文件"
                )

            bucket = self._get_bucket()

            now = datetime.now()
            key = f"{now.year}/{now.month:02d}/{now.day:02d}/{uuid4()}.{ext_name}"

            file_content = file.stream.read()

            client.put_object(Bucket=bucket, Body=file_content, Key=key)

            return {
                "name": file_name,
                "key": key,
                "size": len(file_content),
                "extension": ext_name,
                "mime_type": file.mimetype,
                "hash": sha3_256(file_content).hexdigest(),
            }
        except Exception as _:
            raise FailException("上传文件失败")

    def _get_client(self):
        if self.client:
            return self.client

        secret_id = getenv("TENCENT_COS_SECRET_ID")
        secret_key = getenv("TENCENT_COS_SECRET_KEY")
        region = getenv("TENCENT_COS_REGION")
        schema = getenv("TENCENT_COS_SCHEMA")

        config = CosConfig(
            Region=region,
            SecretId=secret_id,
            SecretKey=secret_key,
            Scheme=schema,
        )
        self.client = CosS3Client(conf=config)
        return self.client

    def _get_bucket(self):
        return getenv("TENCENT_COS_BUCKET")
