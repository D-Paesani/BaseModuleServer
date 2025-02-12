Copy the 3 files pointed in the .gitignore 
```
use ./dockerstart COMMAND <lambda_device|optional>
```
## COMMAND LIST:
* DEV = DUMMY MODE"
* BMTEST = A PRODUCTION MODE WITH TDK LAMBDA SUPPORT"
* ONSHORE = A PRODUCTION MODE WITHOUT TDK LAMBDA SUPPORT AND TEMPERATURE MON POWER OFF"
* BUILD = RUN A DOCKER COMPOSE BUILD"

## LAMBDA DEVICE:
The docker will mount /dev/ttyUSB0 as default if not specified, otherwise type the right dev 
```
ex. ./dockerstart BMTEST /dev/ttyUSB1
```
