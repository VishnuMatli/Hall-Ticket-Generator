#!/bin/bash

echo "=== Updating system ==="
sudo apt update -y

echo "=== Installing Nginx ==="
sudo apt install -y nginx

echo "=== Creating SSL folders ==="
sudo mkdir -p /etc/ssl/private
sudo mkdir -p /etc/ssl/certs
sudo chmod 700 /etc/ssl/private

echo "=== Generating self-signed SSL certificate ==="
PUBLIC_IP=2409:40f0:11d0:92cc:35e6:eea6:d6dc:8453

sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/hallticket-self.key \
  -out /etc/ssl/certs/hallticket-self.crt \
  -subj "/CN=$PUBLIC_IP"

echo "=== Creating Nginx hallticket site ==="
sudo tee /etc/nginx/sites-available/hallticket > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name _;

    ssl_certificate /etc/ssl/certs/hallticket-self.crt;
    ssl_certificate_key /etc/ssl/private/hallticket-self.key;

    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://127.0.0.1:4000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

echo "=== Enabling hallticket site ==="
if [ ! -L /etc/nginx/sites-enabled/hallticket ]; then
    sudo ln -s /etc/nginx/sites-available/hallticket /etc/nginx/sites-enabled/
else
    echo "Site is already enabled."
fi

echo "=== Testing Nginx configuration ==="
sudo nginx -t

echo "=== Restarting Nginx ==="
sudo systemctl restart nginx

echo "=== Enabling firewall ports (80, 443) ==="
sudo ufw allow 80
sudo ufw allow 443

echo "=== Done! ==="
echo "Your site is available at: https://$PUBLIC_IP (with SSL warning)"
