#!/usr/bin/env python3
import lief
crs = lief.parse("./crs")
crs.add_exported_function(0x02558, "hash_exported")

outfile = "crs.so"
crs.write(outfile)
print("Done, see:", outfile)
