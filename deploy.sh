#!/bin/bash
#
# GolfPlex Quick Deployment Script for Ubuntu 22.04
# Optimized for $6/month DigitalOcean droplet (1GB RAM, 1 vCPU)
# 
# Usage: 
#   curl -fsSL https://raw.githubusercontent.com/PWSdelta/TCGolf/main/deploy.sh | bash
#   OR save this file and run: chmod +x deploy.sh && ./deploy.sh
#

set -e  # Exit on any error

echo "🚀 Starting GolfPlex deployment on Ubuntu 22.04..."
echo "💰 Optimized for $6/month droplet (no content generation)"
echo ""

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install core dependencies
echo "🔧 Installing core dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    nginx \
    sqlite3 \
    curl \
    htop \
    ufw

# Configure firewall
echo "🔒 Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Create app user (optional, for security)
echo "👤 Setting up application..."
cd /home/$(whoami)

# Clone the repository
echo "📥 Cloning GolfPlex repository..."
if [ -d "TCGolf" ]; then
    echo "Repository already exists, pulling latest changes..."
    cd TCGolf
    git pull origin main
else
    git clone https://github.com/PWSdelta/TCGolf.git
    cd TCGolf
fi

# Set up Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server

# Configure Django settings for production
echo "⚙️  Configuring Django for production..."
cp golfplex/settings.py golfplex/settings_backup.py

# Create production settings
cat >> golfplex/settings_production.py << 'EOF'
from .settings import *

# Production settings
DEBUG = False
ALLOWED_HOSTS = ['*']  # Configure with your domain later

# Database - SQLite for simplicity
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_production.sqlite3',
    }
}

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Cache with memory backend for small sites
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'golfplex-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}
EOF

# Run Django setup
echo "🗄️  Setting up database..."
export DJANGO_SETTINGS_MODULE=golfplex.settings_production
python manage.py migrate
python manage.py collectstatic --noinput

# Create superuser (optional - comment out if not needed)
echo "👑 Creating Django superuser..."
echo "You can skip this by pressing Ctrl+C and continuing"
python manage.py createsuperuser --noinput --username admin --email admin@example.com || true

# Test Django
echo "🧪 Testing Django application..."
python manage.py check

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/golfplex << EOF
server {
    listen 80;
    server_name _;  # Replace with your domain
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Static files
    location /static/ {
        alias /home/$(whoami)/TCGolf/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files (if any)
    location /media/ {
        alias /home/$(whoami)/TCGolf/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/golfplex /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# Create systemd service for Gunicorn
echo "🔧 Setting up Gunicorn service..."
sudo tee /etc/systemd/system/golfplex.service << EOF
[Unit]
Description=GolfPlex Gunicorn daemon
After=network.target

[Service]
User=$(whoami)
Group=$(whoami)
WorkingDirectory=/home/$(whoami)/TCGolf
Environment="DJANGO_SETTINGS_MODULE=golfplex.settings_production"
ExecStart=/home/$(whoami)/TCGolf/.venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 golfplex.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable golfplex
sudo systemctl start golfplex
sudo systemctl enable nginx
sudo systemctl restart nginx

# Check status
echo "📊 Checking service status..."
sudo systemctl status golfplex --no-pager -l
sudo systemctl status nginx --no-pager -l

# Get droplet IP
DROPLET_IP=$(curl -s ifconfig.me)

echo ""
echo "🎉 GolfPlex deployment complete!"
echo "=================================="
echo ""
echo "📍 Your site is available at: http://$DROPLET_IP"
echo "🔧 Admin panel: http://$DROPLET_IP/admin/"
echo ""
echo "📂 Project location: /home/$(whoami)/TCGolf"
echo "📝 Logs: sudo journalctl -u golfplex -f"
echo "🔄 Restart: sudo systemctl restart golfplex"
echo ""
echo "💡 Next steps:"
echo "   1. Point your domain to this IP: $DROPLET_IP"
echo "   2. Update ALLOWED_HOSTS in settings_production.py"
echo "   3. Set up SSL with certbot (optional)"
echo ""
echo "🏗️  To deploy updates:"
echo "   cd /home/$(whoami)/TCGolf"
echo "   git pull origin main"
echo "   source .venv/bin/activate"
echo "   python manage.py migrate"
echo "   python manage.py collectstatic --noinput"
echo "   sudo systemctl restart golfplex"
echo ""
echo "💰 Running on a $6/month droplet!"
echo "⚡ Typeahead search and country flags ready!"
