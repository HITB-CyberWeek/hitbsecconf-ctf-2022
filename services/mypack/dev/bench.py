
import string,random,threading,sys
import subprocess as sp

requests = 0
errors = 0

def id_gen(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def runcheck(ip):
    flag = "TEAM" +id_gen(3) + "_" + id_gen(32)
    flag_id = id_gen(4) + "-" + id_gen(4) + "-" + id_gen(4)

    proc = sp.Popen(["python3","./checker/checker.py","check",ip,],stderr=sp.PIPE,stdout=sp.PIPE)
    global errors
    res = proc.communicate()
    if proc.returncode != 101:
        errors+=1
        print ("error",res)


def Worker(ip):
    global requests

    while 1:
        runcheck(ip)
        requests +=1
        print(requests,errors)

NUM=int(sys.argv[1])
ths=[]
for c in range(NUM):
    ths.append(threading.Thread(target=Worker,args=("mypack.team2.ctf.hitb.org",)))
for t in ths:
    t.start()
for t in ths:
    t.join()
