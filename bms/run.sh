#!/bin/bash

export FLASK_APP=/app
export FLASK_ENV=development
export FLASK_DEBUG=1

rm /bpd-software/host/python/console/NG_BPDCmd.class
rm /bpd-software/host/python/console/remote.jar
rm /bpd-software/host/python/console/execute.sh

ln -s /cu_tools/NG-DUBase_java/NG_BPDCmd.class /bpd-software/host/python/console/NG_BPDCmd.class
ln -s /cu_tools/NG-DUBase_java/remote.jar /bpd-software/host/python/console/remote.jar
ln -s /cu_tools/NG-DUBase_java/execute.sh /bpd-software/host/python/console/execute.sh

source google_export.sh

#pip3 install -r requirements.txt

#gunicorn -w 4 -b 0.0.0.0:5002 app:app
python3 -u -m flask run --host=0.0.0.0 --port=5002 --debug
