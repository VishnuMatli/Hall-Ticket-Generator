#!/bin/bash

echo "=== Stopping all PM2 apps ==="
pm2 stop all

echo "=== Deleting all PM2 apps ==="
pm2 delete all

echo "=== Removing PM2 startup script ==="
pm2 unstartup systemd

echo "=== Clearing PM2 logs ==="
pm2 flush

echo "=== Removing PM2 global install ==="
sudo npm uninstall -g pm2

echo "=== Cleanup complete ==="
