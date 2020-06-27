#!/usr/bin/env bash
#REM Stop
docker stop tapflume

#REM Remove previuos container 
docker container rm tapflume

#REM Build
docker build ../flume/ --tag tap:flume

docker stop tapflume

FLUME_CONF_FILE=twitterKafka.conf
TOPIC=$1
KEYWORDS=$2

#REM Run
docker run --network tap \
    --ip 10.0.100.10  \
    -e FLUME_CONF_FILE=${FLUME_CONF_FILE} \
    -e TOPIC=${TOPIC} \
    -e KEYWORDS="${KEYWORDS}" \
    --name tapflume \
    -it tap:flume