#!/bin/bash

docker rm -f bmtest

CONTAINER_NAME="bmtest"
CONFIG="$1"

if [ "$CONFIG" == "TEST" ]; then
    DEVICE="/dev/tty9:/dev/ttyUSB0"
elif [ "$CONFIG" == "PRODUCTION" ]; then
    DEVICE="/dev/ttyUSB0:/dev/ttyUSB0"
else
    echo "Utilizzo: $0 [TEST|PRODUCTION]"
    #exit 1
    CONFIG="PRODUCTION"
    echo "Starting in default mode $CONFIG"
    DEVICE="/dev/ttyUSB0:/dev/ttyUSB0"
fi

if [ "$(sudo docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
    sudo docker start $CONTAINER_NAME
    sudo docker attach $CONTAINER_NAME
else
    sudo docker run -it \
    --name $CONTAINER_NAME \
    -p 5001:5001 \
    -v "/Users/dp/Documents/Software/Python/km3net/BaseModuleServer/bmsvol/logs:/app/bms/controller/logs" \
    -v "/Users/dp/Documents/Software/Python/km3net/BaseModuleServer/bmsvol/jsend:/app/bms/controller/jsend" \
    -v "$(pwd)":/app \
    --device=$DEVICE \
    -e FLASK_CONFIG=$CONFIG \
    $CONTAINER_NAME
fi
