#!/bin/sh
set -e

cd /app

# The database container may still be starting up, so retry for a while.
tries=0
until python manage.py migrate --noinput; do
    tries=$((tries + 1))
    if [ "$tries" -ge 30 ]; then
        echo "Database not reachable, giving up." >&2
        exit 1
    fi
    echo "Waiting for database..." >&2
    sleep 2
done

gunicorn --daemon --bind unix:/tmp/kipa.sock wsgi --error-logfile /tmp/errors
