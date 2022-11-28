#!/bin/bash
dockerize -wait tcp://db:3306 -timeout 20s
#alembic upgrade head && gunicorn --bind 0.0.0.0:8000 -w 1 -k uvicorn.workers.UvicornWorker app.server:app
alembic upgrade head && uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload