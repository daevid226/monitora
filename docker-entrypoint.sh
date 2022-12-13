#!/bin/bash

python3 manager.py migrate
gunicorn -c gunicorn.py -b 0.0.0.0:8000 skippay.asgi:application