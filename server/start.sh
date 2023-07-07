#!/bin/sh

redis-server --port 6379 --bind "0.0.0.0" --daemonize yes
python main.py