#!/usr/bin/env bash
# Stop ES
docker stop elasticsearch
docker container rm elasticsearch

# Stop Kibana
docker stop kibana 
docker container rm kibana