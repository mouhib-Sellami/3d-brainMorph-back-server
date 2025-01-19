import os
from django.conf import settings
from dotenv import load_dotenv
from minio import Minio
import io
from minio.error import S3Error
import zipfile
from uuid import uuid4
load_dotenv()

MINIO_CLIENT: Minio = settings.MINIO_CLIENT
BUCKET = os.getenv("MINIO_DEFAULT_BUCKETS")
# print(MINIO_CLIENT.get_presigned_url('GET',BUCKET,'testy'))
found = MINIO_CLIENT.bucket_exists(BUCKET)
if not found:
    MINIO_CLIENT.make_bucket(BUCKET)
    print("Created bucket", BUCKET)
else:
    print("Bucket", BUCKET, "already exists")

# for file in files:
#     object_name = file.name
#     minio_client.put_object(bucket_name, object_name, file, file.size)
# for root, dirs, files in os.walk(folder):
#     for file in files:
#         file_path = os.path.join(root, file)
#         object_name = os.path.relpath(file_path, folder).replace("\\", "/")
#         MINIO_CLIENT.fput_object(
#             BUCKET, client_name+'/'+object_name, file_path)
#         print(
#             f"File '{file_path}' uploaded as '{object_name}' in bucket '{BUCKET}'.")


def download_folder(folder_name):
    try:
        tmp_folder_path = os.path.join(
            settings.MEDIA_ROOT)
        objects = MINIO_CLIENT.list_objects(
            BUCKET, prefix=folder_name, recursive=True)
        
        temp_dir = os.path.join(tmp_folder_path,str(uuid4()))
        os.makedirs(temp_dir, exist_ok=True)
        for obj in objects:
            object_name = obj.object_name
            file_path = os.path.join(temp_dir, object_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            MINIO_CLIENT.fget_object(BUCKET, object_name, file_path)
            print(f"Downloaded {object_name}")

    except S3Error as err:
        print(f"Error occurred: {err}")

    return tmp_folder_path
