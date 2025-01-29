#!/bin/bash

Help() {
    echo "USE AS: $0 [DEV|BMTEST|ONSHORE|BUILD]"
    echo "DEV = DUMMY MODE"
    echo "BMTEST = A PRODUCTION MODE WITH TDK LAMBDA SUPPORT"
    echo "ONSHORE = A PRODUCTION MODE WITHOUT TDK LAMBDA SUPPORT AND TEMPERATURE MON POWER OFF"
    echo "BUILD = RUN A DOCKER COMPOSE BUILD"
}

CONFIG="$1"
#DEVICE=""
PAT=$(head -n 1 PAT)
OPTS=""

if [ "$CONFIG" == "DEV" ]; then
#    DEVICE="/dev/ttyUSB0:/dev/ttyUSB0"
    OPTS="docker compose up"
elif [ "$CONFIG" == "BMTEST" ]; then
#    DEVICE="/dev/ttyUSB0:/dev/ttyUSB0"
    OPTS="docker compose up"
elif [ "$CONFIG" == "ONSHORE" ]; then
#    DEVICE="/dev/tty0:/dev/ttyUSB0"
    OPTS="docker compose up"
elif [ "$CONFIG" == "BUILD" ]; then
    OPTS="docker compose build"
else
    Help
fi

CONFIG=$CONFIG GIT_TOKEN=$PAT $OPTS