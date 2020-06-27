#!/usr/bin/env bash
# Stop
docker stop sparkSubmit

# Remove previuos container 
docker container rm sparkSubmit

docker build ../spark/ --tag tap:spark

docker run \
    -e SPARK_ACTION=spark-submit-python \
    -e TOPIC=$1 \
    -e USER_NAME="$2" \
    -e USER_ID="$3" \
    --network tap \
    -p 4040:4040 \
    --name sparkSubmit \
    -it tap:spark twitter_reputation_analysis_to_es.py "org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5,org.elasticsearch:elasticsearch-hadoop:7.7.0"