#!/usr/bin/env bash
# Render build komutu — Redis/Celery YOK; önbellek Django LocMemCache (süreç içi bellek).
set -o errexit
pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py seed_media   # önce/sonra vakaları + klinik fotoğrafları (idempotent)
python manage.py seed_translations   # dosyadaki çeviriler (yeni dil vb.) — yalnızca eksikler
