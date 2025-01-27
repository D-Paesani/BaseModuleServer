#!/bin/bash

Help() {
    echo "USE AS: $0 [DEV|BMTEST|ONSHORE]"
    echo "DEV = DUMMY MODE"
    echo "BMTEST = A PRODUCTION MODE WITH TDK LAMBDA SUPPORT"
    echo "ONSHORE = A PRODUCTION MODE WITHOUT TDK LAMBDA SUPPORT AND TEMPERATURE MON POWER OFF"
}

CONFIG="$1"
PAT=sBovMGJDpjaTciciAx96

if [ "$CONFIG" == "DEV" ]; then
    DEVICE="/dev/ttyUSB0:/dev/ttyUSB0"
elif [ "$CONFIG" == "BMTEST" ]; then
    DEVICE="/dev/ttyUSB0:/dev/ttyUSB0"
elif [ "$CONFIG" == "ONSHORE" ]; then
    DEVICE="/dev/tty0:/dev/ttyUSB0"
else
    echo "Modalità non valida, uso DEV come predefinito."
    CONFIG="DEV"
    DEVICE="/dev/ttyUSB0:/dev/ttyUSB0"
fi

CONFIG=$CONFIG DEVICE=$DEVICE GIT_TOKEN=$PAT docker-compose up --build