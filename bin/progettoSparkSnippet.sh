#!/usr/bin/env bash
# Stop
docker stop snippetSpark

# Remove previuos container 
docker container rm snippetSpark

docker build ../spark/ --tag tap:spark

docker run \
    -e SPARK_ACTION=spark-submit-python \
    -e TOPIC=$1 \
    --network tap \
    -p 4040:4040 \
    --name snippetSpark \
    -it tap:spark snippetFullText.py "org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5,org.elasticsearch:elasticsearch-hadoop:7.7.0"