#!/usr/bin/env python3
import subprocess
import random
import string
import sys

if len(sys.argv) < 3:
    print("Args: HOST ROUNDS")
    sys.exit(1)

HOST = sys.argv[1]
ROUNDS = int(sys.argv[2])

prefix = "".join(random.choices(string.ascii_lowercase, k=4))
print("Flag ID Prefix:", prefix)

for r in range(1, ROUNDS + 1):
    print(" ========= Round %d of %d ========= " % (r, ROUNDS))

    (code, out) = subprocess.getstatusoutput("./checker.py check %s" % HOST)
    print(code, out)
    assert code == 101

    print("=" * 64)

    flag_id = "%s%04d" % (prefix, r)
    flag_data = ("F"*32) + "="

    cmd = "./checker.py put %s %s %s 1" % (HOST, flag_id, flag_data)
    print("RUN:", cmd)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
    assert proc.returncode == 101

    print("=" * 64)

    flag_id = out.decode().strip()
    cmd = "./checker.py get %s '%s' %s 1" % (HOST, flag_id, flag_data)
    print("RUN:", cmd)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
    assert proc.returncode == 101


print("Completed. Good job!")
