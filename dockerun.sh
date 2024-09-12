sudo docker run -it \
-p 5001:5001 \
-v "/Users/dp/Documents/Software/Python/km3net/BaseModuleServer/bmsvol/logs:/app/bms/controller/logs" \
-v "/Users/dp/Documents/Software/Python/km3net/BaseModuleServer/bmsvol/jsend:/app/bms/controller/jsend" \
-v "$(pwd)":/app \
--device=/dev/tty9:/dev/ttyUSB0 bmtest
