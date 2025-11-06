import minio

minio_client = minio.Minio(
    "minio:9000", access_key="minioadmin", secret_key="minioadmin123", secure=False
)

BUCKET_NAME = "foodtracker"

if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)
