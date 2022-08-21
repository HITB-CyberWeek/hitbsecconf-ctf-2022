#!/bin/bash
set -eu

OUTPUT="table.txt"

echo -n "Compiling..."
gcc -o brute *.c && echo "OK."

echo -n "Generating..."
./brute | sort > $OUTPUT && echo "OK."

echo "Result:"
wc -l $OUTPUT
