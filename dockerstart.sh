#!/bin/bash

Help() {
    echo "USE AS: $0 [DEV|BMTEST|ONSHORE|BUILD] [DEV PATH TO MOUNT (or use default)]"
    echo "DEV = DUMMY MODE"
    echo "BMTEST = A PRODUCTION MODE WITH TDK LAMBDA SUPPORT"
    echo "ONSHORE = A PRODUCTION MODE WITHOUT TDK LAMBDA SUPPORT AND TEMPERATURE MON POWER OFF"
    echo "BUILD = RUN A DOCKER COMPOSE BUILD"

    echo "EXAMPLE: ./dockerstart BMTEST /dev/ttyUSB3"
    echo "OR TO USE DEFAULT DEVICE ./dockerstart DEV"
    echo "IF YOU HAVE DEV MOUNT PROBLEMS ./dockerstart DEV /dev/null"
}

Set_device() {
    if [ $2 ]; then
        echo "$2"
    else
        echo "$1"
    fi
}

CONFIG="$1"
DEVICE=""
PAT=$(head -n 1 PAT)
OPTS=""

if [ "$CONFIG" == "DEV" ]; then
    DEVICE=$(Set_device "/dev/ttyUSB0" "$2")
    OPTS="docker compose up"
elif [ "$CONFIG" == "BMTEST" ]; then
    DEVICE=$(Set_device "/dev/ttyUSB0" "$2")
    OPTS="docker compose up"
elif [ "$CONFIG" == "ONSHORE" ]; then
    DEVICE=$(Set_device "/dev/null" "$2")
    OPTS="docker compose up"
elif [ "$CONFIG" == "BUILD" ]; then
    OPTS="docker compose build"
    DEVICE=$(Set_device "/dev/null" "$2")
else
    Help
fi

CONFIG=$CONFIG GIT_TOKEN=$PAT DEVICE=$DEVICE $OPTS