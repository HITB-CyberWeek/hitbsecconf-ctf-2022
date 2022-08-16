#!/usr/bin/env python3
import time,os
from stat import S_ISREG, ST_CTIME, ST_MODE
import datetime

def CleanOld(dirpath,last_time):
    entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
    entries = ((os.stat(path), path) for path in entries)
    entries = ((stat[ST_CTIME], path) for stat, path in entries if S_ISREG(stat[ST_MODE]))
    all_file_names = []
    curtime = datetime.datetime.now()
    all_file_names_to_delete=[]
    for cdate, path in sorted(entries):
        ct = datetime.datetime.fromtimestamp(cdate)
        #print(ct,curtime,curtime - ct,last_time,curtime - ct > last_time,path)
        if curtime - ct > last_time:
            all_file_names_to_delete.append(path)
            print("Removing",path)
            os.unlink(path)
    return

while 1:
    CleanOld("spacemans",datetime.timedelta(minutes=30))
    CleanOld("spaceships",datetime.timedelta(minutes=30))
    time.sleep(60)
