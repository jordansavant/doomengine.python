#!/bin/bash

source venv/bin/activate

if [ -f main_$1.py ]; then
	python3 main_$1.py
else
	python3 main.py
fi

deactivate