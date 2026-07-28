#!/usr/bin/env bash
# Render "Build Command" should be: ./build.sh
# This makes sure the production database schema is always up to date and
# static files are collected — without this, Render only installs
# dependencies and starts gunicorn; migrations are never applied, so a fresh
# Postgres database on Render stays completely empty (0 tables/rows) even
# though your local db.sqlite3 has 100 seeded articles.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
