#!/usr/bin/env bash

pip3 install -r requirements
python3 manage.py migrate
