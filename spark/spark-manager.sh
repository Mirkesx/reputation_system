#!/bin/bash
[[ -z "${SPARK_ACTION}" ]] && { echo "SPARK_ACTION required"; exit 1; }

echo "Running action ${SPARK_ACTION}"
./bin/spark-submit --packages $2 /opt/tap/$1 ${TOPIC} ${USER_NAME} ${USER_ID}

