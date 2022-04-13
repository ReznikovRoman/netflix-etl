#!/bin/sh

django-cadmin migrate --noinput
django-cadmin collectstatic --no-input

# Run the main container process
exec "$@"
