# Description

Service mypack is intended for parsing, storing and loading packages in msgpack format.
User connects to service via 3777/tcp and sends commands interactively.

Next commands are supported:
1. "store" - stores new msgpack package with specific id
2. "load" - loads previously stored msgpack package in some local
cell. Service supports 10 cells totally.
3. "print" - parses buffer from specific cell according the msgpack format.
Prints content in json-like format
4. "unload" - unloads cell from msgpack buffer and makes this cell empty
5. "search" - prints all ids which contains specific substring

# Flag

"print" command has special improvement: if package is a map and it contains
"flag" and "password" keys, then it asks user to enter password. If password is
correct then service prints content of flag key. If package does not contain
flag and password keys, then service prints string representation of package.

# Vulnerability

In msgpack small strings may be encoded by following way:

`D9 XX YYYYYYY`

where `XX` is a length of line `YYYYYYY`.
`XX` can be a number which equals `0xFF` (-1).

This value allows to skip length verification and forces parser to copy more bytes
than required. This is heap buffer overflow. To use it for getting flag you may
try to force service to allocate chunks in heap so that buffer with flag would follow
right after buffer, where `YYYYYYY` is copied. So you can overwrite type of msgpack
package to line type and in print command full package with flag will be be shown.

# Scheme of chunks in heap

###  Before overwrite

```
                                               i  d
?? ?? ?? ?? ?? ?? ?? ?? chunk header 83 D9 02 69 64 D9 ?? ?? ... password and flag fields
                                     |   |  |
                                     |   |  - length is 2
                                     |   - type is string
                                     - type is map, sequence of pairs, 3 hex means 3 pairs.
```

### After overwrite

```
                                               i  d
D9 FF XX XX XX XX XX XX chunk header D9 30 02 69 64 D9 ?? ?? ... password and flag fields
                                      |  |
                                      |  - length is 0x30, on print entire package will be shown.
                                      - line type
```

The main difficulty of exploitation is to allocate chunks in specific sequence.

To do this some magic is required. In exploit I have done this successfuly, but you may try to
reach this by another way.

See full exploit at [/sploits/mypack/](../../sploits/mypack/).
