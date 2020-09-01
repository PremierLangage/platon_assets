#!/usr/bin/env bash

sudo -u postgres psqli <<EOF
CREATE DATABASE django_sandbox;
CREATE USER django WITH PASSWORD 'django_password';
GRANT ALL PRIVILEGES ON DATABASE django_sandbox TO django;
ALTER USER django CREATEDB;
EOF

pip3 install -r requirements.txt
python3 manage.py migrate
