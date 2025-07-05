#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install django-image-cropping easy-thumbnails
pip install -r requirements.txt

# Navigate to the Django project directory
cd model-project

# Set up persistent directories for database and media
mkdir -p /opt/render/project/data
mkdir -p /opt/render/project/data/media
mkdir -p /opt/render/project/data/media/community_posts/2025
mkdir -p /opt/render/project/data/media/profile_pics

# Copy the local database to persistent storage if it doesn't exist
if [ ! -f /opt/render/project/data/db.sqlite3 ]; then
  echo "Creating initial database in persistent storage"
  if [ -f db.sqlite3 ]; then
    cp db.sqlite3 /opt/render/project/data/db.sqlite3
  fi
fi

# Copy default profile picture if it doesn't exist
if [ ! -f /opt/render/project/data/media/profile_pics/default.png ]; then
  cp -n static/images/farmerLogo.png /opt/render/project/data/media/profile_pics/default.png 2>/dev/null || :
fi

# Collect static files
python manage.py collectstatic --no-input

# Run migrations on the persistent database
python manage.py migrate