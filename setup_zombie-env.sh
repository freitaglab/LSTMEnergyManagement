#!/bin/bash

python3 -m venv .zombie-env
source .zombie-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
