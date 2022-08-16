#!/bin/bash

export PYTHONPATH="/usr/local/lib/python2.7/site-packages"
if [ ! -f "/app/db/secret.txt" ]; then
  tr -dc A-Za-z0-9 < /dev/urandom | head -c 40 ; echo '' > /app/db/secret.txt
fi
if [ ! -f "/app/db/kipa.db" ]; then
  cp /app/docs/initial.db /app/db/kipa.db
fi

exec "$@"
