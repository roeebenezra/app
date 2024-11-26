#!/bin/bash

if [ "$1" == "up" ]; then
    docker compose up --scale app=5 -d
elif [ "$1" == "down" ]; then
    docker compose up --scale app=3 -d
else
    echo "Usage: ./scale.sh up|down"
fi
