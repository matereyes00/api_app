#!/bin/sh

echo "Waiting for database..."
while ! nc -z db 5432; do
    sleep 1
done
echo "Database is up!"

# Apply database migrations
python manage.py migrate

# Collect static files (optional)
python manage.py collectstatic --noinput

# Start Django
exec "$@"
