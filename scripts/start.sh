#!/bin/bash

# Start PHP-FPM in background
echo "Starting PHP-FPM..."
php-fpm -D

# If package.json exists in the angular directory, install dependencies and start Angular
if [ -f "/var/www/html/frontend/package.json" ]; then
    echo "Found Angular project, installing dependencies..."
    cd /var/www/html/frontend
    npm install

    echo "Starting Angular development server..."
    ng serve --host 0.0.0.0 --disable-host-check &
fi

# Access to SuiteCRM directory
echo "SuiteCRM directory is available at /var/www/suitecrm"

# Keep container running
echo "Services started. Container is now running..."
tail -f /dev/null
