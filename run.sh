#!/bin/bash

export FLASK_APP=/app
export FLASK_ENV=development
export FLASK_DEBUG=1

source google_export.sh

#pip3 install -r requirements.txt

python3 -m flask run --host=0.0.0.0 --port=5001
