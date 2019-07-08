#!/bin/bash
# script runs subsequent images via hdfsee.py from the stream file.
# Running from args1: stream file, args2: geomfile
for i in $(grep cxidb $1 | grep ^Image | cut -f 3 -d " ")
do
  echo $i
  python hdfsee.py  ~/$i  -g $2 -p $1
done
