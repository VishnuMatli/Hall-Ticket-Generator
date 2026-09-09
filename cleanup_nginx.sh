#!/bin/bash

echo "=== Removing hallticket Nginx config ==="
sudo rm -f /etc/nginx/sites-available/hallticket
sudo rm -f /etc/nginx/sites-enabled/hallticket

echo "=== Removing self-signed SSL files ==="
sudo rm -f /etc/ssl/private/hallticket-self.key
sudo rm -f /etc/ssl/certs/hallticket-self.crt

echo "=== Testing Nginx configuration ==="
sudo nginx -t

echo "=== Restarting Nginx ==="
sudo systemctl restart nginx

echo "=== Stopping Nginx service ==="
sudo systemctl stop nginx

echo "=== Disabling Nginx service from startup ==="
sudo systemctl disable nginx

echo "=== Cleanup complete ==="
echo "Nginx is stopped and hallticket configs removed."
