#!/bin/bash
# script to run subsequent images from the stream file.
# you must enter the stream and geom file.
for i in $(grep "Image filename" $1| cut -f 3 -d " ")
do
  echo $i
  python hdfsee.py  $i  -g $2 -p $1
done
