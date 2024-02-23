#!/bin/bash

export FLASK_APP=/app
export FLASK_ENV=development
export FLASK_DEBUG=1


python3 -m flask run --host=0.0.0.0 --port=5001
# flask run --debug -p 5001
# flask run -p 5001 &


