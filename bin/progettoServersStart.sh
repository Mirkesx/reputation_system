#!/usr/bin/env bash

#ZK
docker stop kafkaZK
docker container rm kafkaZK

docker build ../kafka/ --tag tap:kafka
docker run -d \
    -e KAFKA_ACTION=start-zk \
    --network tap --ip 10.0.100.22 \
    -p 2181:2181 \
    -v zk-data:/tmp/zookeeper/ \
    --name kafkaZK \
    -it tap:kafka

#Kafka Server
docker stop kafkaServer
docker container rm kafkaServer

docker build ../kafka/ --tag tap:kafka
docker run -d \
    -e KAFKA_ACTION=start-kafka \
    --network tap --ip 10.0.100.23 \
    -p 9092:9092 \
    -v kafka-data:/tmp/ \
    --name kafkaServer \
    -it tap:kafka