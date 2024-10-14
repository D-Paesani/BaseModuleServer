#!/bin/bash

docker rm -f bmtest

CONTAINER_NAME="bmtest"
CONFIG="$1"

if [ "$CONFIG" == "DEV" ]; then
    DEVICE="/dev/tty0:/dev/ttyUSB0"
elif [ "$CONFIG" == "BMTEST" ]; then
    DEVICE="/dev/ttyUSB0:/dev/ttyUSB0"
elif [ "$CONFIG" == "ONSHORE" ]; then
    DEVICE="/dev/tty0:/dev/ttyUSB0"
else
    echo "USE AS: $0 [DEV|BMTEST|ONSHORE]"
    echo "DEV = DUMMY MODE"
    echo "BMTEST = A PRODUCTION MODE WITH TDK LAMBDA SUPPORT"
    echo "ONSHORE = A PRODUCTION MODE WITHOUT TDK LAMBDA SUPPORT AND TEMPERATURE MON POWER OFF"
    #exit 1
    CONFIG="DEV"
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
