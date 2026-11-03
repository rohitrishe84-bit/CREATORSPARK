#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "--- Installing dependencies ---"
pip install -r requirements.txt

echo "--- Collecting static files ---"
python manage.py collectstatic --no-input

echo "--- Running database migrations ---"
python manage.py migrate

echo "--- Seeding FAQs and Error Codes ---"
python manage.py seed_faqs
python manage.py seed_error_codes

echo "--- Build complete! ---"
