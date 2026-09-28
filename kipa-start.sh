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

# Only creates the admin if that username doesn't exist yet; never resets a password.
if [ -n "$KIPA_ADMIN_USER" ] && [ -n "$KIPA_ADMIN_PASSWORD" ]; then
    python manage.py shell -c "
import os
from django.contrib.auth.models import User
nimi = os.environ['KIPA_ADMIN_USER']
if not User.objects.filter(username=nimi).exists():
    User.objects.create_superuser(nimi, '', os.environ['KIPA_ADMIN_PASSWORD'])
    print('Created admin user', nimi)
"
fi

gunicorn --daemon --bind unix:/tmp/kipa.sock wsgi --error-logfile /tmp/errors
