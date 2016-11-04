#!/usr/bin/env bash

# Start the celery worker
celery worker -A crashreporter_hq.celery --loglevel=debug &
celery -A crashreporter_hq.celery beat --loglevel=debug &
