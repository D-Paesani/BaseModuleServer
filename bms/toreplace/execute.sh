cd /cu_tools/NG-DUBase_java
source java_setenv.sh     
/usr/bin/java -cp  ./remote.jar:. $1 $2 $3 $4 $5 $6 $7
echo cd - >> /dev/null