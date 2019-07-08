#!/bin/bash


for i in $(grep cxidb $1 | grep ^Image | cut -f 3 -d " ")
do
  echo $i
  python hdfsee.py  ~/$i  -g $2 -p $1
done
