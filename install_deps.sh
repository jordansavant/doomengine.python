#!/bin/bash

brew install python@3 sdl sdl_image sdl_mixer sdl_ttf portmidi sdl2
brew cask install xquartz
python3 -m venv venv

source venv/bin/activate
pip3 install --upgrade pip
pip3 install pygame==2.0.0.dev4 numpy PyOpenGL
deactivate
