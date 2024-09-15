#!/usr/bin/bash

pkill -f display.py

sleep 1

python3 src/display.py &

jobs

source ../bin/activate

python3 src/main.py
