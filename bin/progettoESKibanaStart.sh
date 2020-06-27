#!/usr/bin/env bash
# Stop
docker stop elasticsearch

# Remove previuos container 
docker container rm elasticsearch

# Build
docker build ../elasticsearch/ --tag tap:elasticsearch

docker run -t -d \
     -p 9200:9200 \
     -p 9300:9300 \
     --ip 10.0.100.51 \
     --name elasticsearch \
     --network tap \
     -v "$(pwd)"/../volumes/es-data:/usr/share/elasticsearch/data/ \
     -e "discovery.type=single-node"  \
     tap:elasticsearch

# Stop
docker stop kibana

#  Remove previuos container 
docker container rm kibana

# Build
docker build ../kibana/ --tag tap:kibana

docker run -d \
     -p 5601:5601 \
     --ip 10.0.100.52 \
     --name kibana\
     --network tap \
     tap:kibana