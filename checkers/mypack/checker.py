#!/usr/bin/env python3

import subprocess as sp,sys,time,re
import string,random,json
from socket import *
from struct import *
import traceback

idx_read = 0
DEBUG = 1
def id_gen(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))
def read_until(s,c):
    global idx_read
    #print("Read idx %d"%idx_read)
    idx_read+=1
    cc = s.recv(1)
    mes=b""
    while cc != c:
        mes+=cc
#        sys.write(cc.decode())
        cc = s.recv(1)
        if len(cc)==0:
            break
    mes += cc
    if DEBUG:
        sys.stderr.write("<-"+str(mes)+"\n")
    try:
        return mes.decode().rstrip()
    except:
        return mes
def send_mes(s,mes):
    if (type(mes) == type(b"a")):
        mes += b"\n"
        if DEBUG:
            sys.stderr.write("->"+str(mes)+"\n")
        s.send(mes)
    elif (type(mes) == type("a")):
        mes += "\n"
        if DEBUG:
            sys.stderr.write("->"+str(mes.encode())+"\n")
        s.send(mes.encode())
    else:
        print("Cannot encode")
    #s.flush()
    #time.sleep(0.5)
def StoreVal(proc,val):
    res = read_until(proc,b"\n")
    if len(res)==0:
        print("Empty response")
        exit(104)
    if res != "Enter command":
        print("Invalid greeter")
        exit(103)
    send_mes(proc,f"store")
    res = read_until(proc,b"\n")
    if res != "Enter id":
        print("Invalid greeter 2")
        exit(103)
    id1 = id_gen()
    send_mes(proc,f"{id1}")
    res = read_until(proc,b"\n")
    if res != "Enter pack to store":
        print("Invalid greeter 3")
        exit(103)
    send_mes(proc,f"{val}")
    res = read_until(proc,b"\n")
    if res != f"Storing id {id1}":
        print("Invalid greeter 4")
        exit(103)
    return id1
def StoreVal2(proc,val,id1):
    res = read_until(proc,b"\n")
    if len(res)==0:
        print("Empty response")
        exit(104)
    if res != "Enter command":
        print("Invalid greeter")
        exit(103)
    send_mes(proc,f"store")
    res = read_until(proc,b"\n")
    if res != "Enter id":
        print("Invalid greeter 2")
        exit(103)
    send_mes(proc,f"{id1}")
    res = read_until(proc,b"\n")
    if res != "Enter pack to store":
        print("Invalid greeter 3")
        exit(103)
    send_mes(proc,f"{val}")
    res = read_until(proc,b"\n")
    if res != f"Storing id {id1}":
        print("Invalid greeter 4")
        exit(103)
    return id1
def LoadVal(proc,mid):
    res = read_until(proc,b"\n")
    if res != "Enter command":
        print("Invalid greeter")
        exit(103)

    send_mes(proc,f"search")
    res = read_until(proc,b"\n")
    if res != "Enter substring to search":
        print("Invalid greeter 2")
        exit(103)

    pos = random.randint(0,len(mid)-3)
    pat = mid[pos:pos+2]

    send_mes(proc,f"{pat}")
    found = 0
    for i in range(1000):
        res = read_until(proc,b"\n")
        if res == "No such ids":
            print("Cannot find id in search")
            exit(102)
        if res == mid:
            found =1
        if res == "Enter command":
            break
    send_mes(proc,f"load")
    res = read_until(proc,b"\n")
    if res != "Enter slot number(0-9)":
        print("Invalid greeter 4")
        exit(103)
    slot_num = random.randint(0,9)
    send_mes(proc,f"{slot_num}")
    res = read_until(proc,b"\n")
    if res != "Enter id to load":
        print("Invalid greeter 5")
        exit(103)
    send_mes(proc,f"{mid}")
    res = read_until(proc,b"\n")
    if res != f"Loaded id {mid} to slot {slot_num}":
        print("Invalid greeter 6")
        exit(103)
    res = read_until(proc,b"\n")
    if res != "Enter command":
        print("Invalid greeter 3")
        exit(103)
    send_mes(proc,f"print")
    res = read_until(proc,b"\n")
    if res != f"Enter slot number(0-9)":
        print("Invalid greeter 7")
        exit(103)
    send_mes(proc,f"{slot_num}")
    res = read_until(proc,b"\n")
    if res == f"Slot is empty":
        print("No data in slot")
        exit(103)
    return res
def LoadVal2(proc,mid,password):
    res = read_until(proc,b"\n")
    if len(res)==0:
        print("Empty response")
        exit(104)
    if res != "Enter command":
        print("Invalid greeter")
        exit(103)

    send_mes(proc,f"search")
    res = read_until(proc,b"\n")
    if res != "Enter substring to search":
        print("Invalid greeter 2")
        exit(103)

    pos = random.randint(0,len(mid)-3)
    pat = mid[pos:pos+2]

    send_mes(proc,f"{pat}")
    found = 0
    for i in range(1000):
        res = read_until(proc,b"\n")
        if res == "No such ids":
            print("Cannot find id in search")
            exit(102)
        if res == mid:
            found =1
        if res == "Enter command":
            break
    send_mes(proc,f"load")
    res = read_until(proc,b"\n")
    if res != "Enter slot number(0-9)":
        print("Invalid greeter 4")
        exit(103)
    slot_num = random.randint(0,9)
    send_mes(proc,f"{slot_num}")
    res = read_until(proc,b"\n")
    if res != "Enter id to load":
        print("Invalid greeter 5")
        exit(103)
    send_mes(proc,f"{mid}")
    res = read_until(proc,b"\n")
    if res != f"Loaded id {mid} to slot {slot_num}":
        print("Invalid greeter 6")
        exit(103)
    res = read_until(proc,b"\n")
    if res != "Enter command":
        print("Invalid greeter 3")
        exit(103)
    send_mes(proc,f"print")
    res = read_until(proc,b"\n")
    if res != f"Enter slot number(0-9)":
        print("Invalid greeter 7")
        exit(103)
    send_mes(proc,f"{slot_num}")
    res = read_until(proc,b"\n")
    if res != f"enter password":
        print("No data in slot")
        exit(103)
    send_mes(proc,f"{password}")
    res = read_until(proc,b"\n")
    if not "Flag is " in res:
        print("Cannot read flag")
        exit(102)
    return res
if sys.argv[1] == "info":
    print("vulns: 1\npublic_flag_description: Flag ID is id of packet to store\n")
    exit(101)
#proc = sp.Popen("./serv12",shell=True,stdin=sp.PIPE,stdout=sp.PIPE)
proc = socket(AF_INET,SOCK_STREAM)
try:
    proc.connect((sys.argv[2],3777))
except OSError as e:
    traceback.print_tb(e.__traceback__)
    exit(104)
except Exception as e:
    traceback.print_tb(e.__traceback__)
    exit(104)
if sys.argv[1] == 'check':
    p1 = random.randint(0,127)
    id1 = StoreVal(proc,"%02x" %p1)

    val1 = LoadVal(proc,id1)
    if val1 != str(p1):
        print("Value was not received")
        exit(103)

    s2 = id_gen(random.randint(3,50))
    p2 = "d9%02x%02s" % (len(s2), s2.encode().hex())
    id2 = StoreVal(proc,p2)

    val2 = LoadVal(proc,id2)
    #print(val2,s2)
    if val2 !=s2:
        print("Value was not received")
        exit(103)
elif sys.argv[1] == 'put':
    flagid = sys.argv[3]
    flag = sys.argv[4]
    password = id_gen(8)
    fpack = "83"
    fpack += "D9%02X%s" % (len("id"),"id".encode().hex())
    fpack += "D9%02X%s" % (len(flagid),flagid.encode().hex())
    fpack += "D9%02X%s" % (len("password"),"password".encode().hex())
    fpack += "D9%02X%s" % (len(password),password.encode().hex())
    fpack += "D9%02X%s" % (len("flag"),"flag".encode().hex())
    fpack += "D9%02X%s" % (len(flag),flag.encode().hex())
    StoreVal2(proc,fpack,flagid)
    res = LoadVal2(proc,flagid,password)
    if not flag in res:
        print("No flag stored")
        exit(103)
    #print(f"{flagid},{password}")
    print(json.dumps({"public_flag_id": str(flagid), "password": password}))
elif sys.argv[1] == 'get':
    #flagid,password = sys.argv[3].split(",")
    jsn = json.loads(sys.argv[3])
    flagid = jsn['public_flag_id']
    password = jsn['password']
    flag = sys.argv[4]
    res = LoadVal2(proc,flagid,password)
    if not flag in res:
        print("No flag stored")
        exit(102)
proc.close()
exit(101)
