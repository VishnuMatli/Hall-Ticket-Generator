#!/bin/bash

echo "=== Installing PM2 globally ==="
sudo npm install -g pm2

echo "=== Navigating to project directory ==="
# CHANGE THIS PATH TO YOUR PROJECT PATH
PROJECT_PATH="/home/$USER/Desktop/university-version"
cd "$PROJECT_PATH" || { echo "Project folder not found!"; exit 1; }

echo "=== Installing dependencies (npm install) ==="
npm install

echo "=== Starting Node.js app with PM2 ==="
# CHANGE server.js TO YOUR ENTRY FILE IF DIFFERENT
pm2 start server.js --name hallticket

echo "=== Saving PM2 process list ==="
pm2 save

echo "=== Enabling PM2 startup on reboot ==="
pm2 startup systemd -u $USER --hp /home/$USER

echo "=== PM2 setup complete ==="
echo "App name: hallticket"
echo "Check logs with: pm2 logs hallticket"
echo "Check status: pm2 status"
echo "Restart app: pm2 restart hallticket"
echo "Stop app: pm2 stop hallticket"
