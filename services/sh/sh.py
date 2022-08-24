from fastapi import FastAPI, UploadFile
from fastapi.responses import Response, JSONResponse
from minio import Minio
from minio.error import S3Error
import os
from pathlib import Path
from rq import Queue
import redis
import shutil
import tempfile

app = FastAPI(docs_url="/")

s3_client = Minio("s3:9000", os.getenv('MINIO_SH_USER'),
                  os.getenv('MINIO_SH_PASSWORD'), secure=False)
redist_client = redis.from_url("redis://redis:6379")
q = Queue(connection=redist_client)


@app.post("/bucket/~{bucket}")
def post(bucket, input: UploadFile):
    if s3_client.bucket_exists(bucket):
        return JSONResponse({"bucket": bucket}, status_code=409)
    try:
        s3_client.make_bucket(bucket)
    except S3Error:
        return JSONResponse({"bucket": bucket}, status_code=400)

    archive = tempfile.NamedTemporaryFile(
        dir="/data/input", delete=False, suffix=Path(input.filename).suffix)
    input.file.truncate(8 * 1024)
    shutil.copyfileobj(input.file, archive)
    archive.close()

    q.enqueue("worker.run", args=(archive.name, bucket),
              job_timeout=15, result_ttl=1800, ttl=30)
    return JSONResponse({"bucket": bucket}, status_code=200)


@app.get("/~{bucket}/{file}")
def get(bucket, file):
    r = None
    try:
        r = s3_client.get_object(bucket, file)
        content = r.read()
        return Response(content=content)
    except S3Error:
        return Response(status_code=404)
    finally:
        if r:
            r.close()
            r.release_conn()
