#!/bin/bash

source venv/bin/activate

case $1 in
	'diy')
		python3 main_$1.py
		;;
	'opengl')
		python3 main_$1.py
		;;
	*)
		python3 main.py
		;;
esac

deactivate