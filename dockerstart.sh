#!/bin/bash

CONTAINER_NAME="bmtest"

if [ "$1" == "TEST" ]; then
    runAs="TEST"
elif [ "$1" == "PRODUCTION" ]; then
    DEVICE="/dev/ttyUSB0:/dev/ttyUSB0"
    runAs="PRODUCTION"
else
    echo "Utilizzo: $0 [TEST|PRODUCTION]"
    exit 1
fi

sed -i "s/runAs *= *'.*'/runAs = '$runAs'/" "./bms/web_manager/config.py"

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
    --device=/dev/tty9:/dev/ttyUSB0 bmtest
fi
