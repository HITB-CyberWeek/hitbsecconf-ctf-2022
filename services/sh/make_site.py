from minio import Minio
import os
from pathlib import Path
from patoolib import get_archive_format, extract_archive, test_archive
from patoolib.util import PatoolError
import sys
import tempfile

(ARCHIVE, BUCKET) = sys.argv[1:3]

s3_client = Minio("s3:9000", os.getenv('MINIO_SH_USER'),
                  os.getenv('MINIO_SH_PASSWORD'), secure=False)

with tempfile.TemporaryDirectory() as outdir:
    test_archive(archive=ARCHIVE, verbosity=-1, interactive=False)
    extract_archive(archive=ARCHIVE, verbosity=-1,
                    outdir=outdir, interactive=False)

    for item in Path(outdir).iterdir():
        if not item.is_file():
            continue
        try:
            get_archive_format(item)
            extract_archive(archive=item, verbosity=-1,
                            outdir=outdir, interactive=False)
            item.unlink()
        except PatoolError:
            pass

    for item in Path(outdir).iterdir():
        s3_client.fput_object(BUCKET, item.name, item)
