#!/bin/bash

echo "🚀 Deploying SmartMapParis 3D..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Populate data
echo "📊 Populating data..."
python manage.py populate_quartiers
python manage.py import_all_france_departments

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Deployment complete!"
echo "🌐 Start the server with: python manage.py runserver" 