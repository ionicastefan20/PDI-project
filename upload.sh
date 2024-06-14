#!/bin/bash

FILENAME=Sentinel_2024.tif

cp "$FILENAME" data/hadoop/

docker exec -it namenode hadoop fs -mkdir -p /user/spark/input && ( echo 'hadoop mkdir successful') || echo 'hadoop mkdir failed'

docker exec -it namenode hdfs dfs -put /mnt/data/"$FILENAME" /user/spark/input || ( echo 'File already exists' && exit 1 )
