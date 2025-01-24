import tempfile
import os
from django.conf import settings
from dotenv import load_dotenv
from minio import Minio
import io
from minio.error import S3Error
import zipfile
from uuid import uuid4
import io
load_dotenv()

MINIO_CLIENT: Minio = settings.MINIO_CLIENT
BUCKET = os.getenv("MINIO_DEFAULT_BUCKETS")
found = MINIO_CLIENT.bucket_exists(BUCKET)

if not found:
    MINIO_CLIENT.make_bucket(BUCKET)
    print("Created bucket", BUCKET)
else:
    print("Bucket", BUCKET, "already exists")


def create_folder(folder_name):
    MINIO_CLIENT.put_object(BUCKET, str(folder_name) +
                            '/', data=io.BytesIO(b''), length=0)


def upload_single(file, folder_name):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            for chunk in file.chunks():
                temp_file.write(chunk)
            temp_file.close()
            MINIO_CLIENT.fput_object(
                BUCKET,
                str(folder_name)+"/" + file.name,
                temp_file.name,
                content_type=file.content_type,
            )
        except S3Error as e:
            print(e)
            raise e
        finally:
            os.remove(temp_file.name)


def download_folder(folder_name):
    try:
        tmp_folder_path = os.path.join(
            settings.MEDIA_ROOT)
        objects = MINIO_CLIENT.list_objects(
            BUCKET, prefix=folder_name, recursive=True)
        temp_dir = os.path.join(tmp_folder_path, str(uuid4()))
        os.makedirs(temp_dir, exist_ok=True)
        for obj in objects:
            file_path = os.path.join(temp_dir, os.path.relpath(obj.object_name, folder_name))
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            if not obj.is_dir:
                MINIO_CLIENT.fget_object(BUCKET, obj.object_name, file_path)
                print(f"Downloaded {obj.object_name} to {file_path}")
        print(temp_dir)
    except S3Error as err:
        print(f"Error occurred: {err}")
        temp_dir = None
    return temp_dir
