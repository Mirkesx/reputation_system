# Stop
docker stop kafkaConsumerPython

# Remove previuos container 
docker container rm kafkaConsumerPython

docker build ../python/ --tag tap:python
docker run --network tap \
        -e PYTHON_APP=scriptedConsumer.py \
        -e TOPIC=$1 \
        --name kafkaConsumerPython \
        -it \
        tap:python
