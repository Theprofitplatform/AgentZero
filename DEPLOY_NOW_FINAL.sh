#!/bin/bash

# =====================================================
# AGENTZERO RAPID DEPLOYMENT SCRIPT
# For: agent.theprofitplatform.com.au (31.97.222.218)
# =====================================================

set -e

echo "
╔════════════════════════════════════════════════════════════╗
║   🚀 DEPLOYING AGENTZERO TO agent.theprofitplatform.com.au ║
╚════════════════════════════════════════════════════════════╝
"

# Ensure running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Please run as root: sudo bash $0"
   exit 1
fi

echo "✅ Starting deployment process..."

# 1. Install Docker if not present
echo "📦 Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
else
    echo "✓ Docker already installed"
fi

# 2. Install docker-compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "Installing docker-compose..."
    apt-get update -qq
    apt-get install -y docker-compose
else
    echo "✓ Docker-compose already installed"
fi

# 3. Install other dependencies
echo "📦 Installing dependencies..."
apt-get install -y git certbot python3-certbot-nginx

# 4. Clone repository
echo "📥 Cloning AgentZero repository..."
cd /var/www || mkdir -p /var/www && cd /var/www
rm -rf agentzero
git clone https://github.com/Theprofitplatform/AgentZero.git agentzero
cd agentzero

# 5. Generate secure configuration
echo "🔐 Generating secure configuration..."
cat > .env << EOF
APP_NAME=AgentZero
APP_ENV=production
DEBUG=false
LOG_LEVEL=WARNING

# Security Keys (auto-generated)
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Database
POSTGRES_DB=agentzero_prod
POSTGRES_USER=agentzero
POSTGRES_PASSWORD=$(openssl rand -hex 20)

# Redis
REDIS_PASSWORD=$(openssl rand -hex 20)

# URLs
DATABASE_URL=postgresql://agentzero:$(openssl rand -hex 20)@postgres:5432/agentzero_prod
REDIS_URL=redis://default:$(openssl rand -hex 20)@redis:6379/0

# Domain Configuration
DOMAIN=agent.theprofitplatform.com.au
ALLOWED_HOSTS=agent.theprofitplatform.com.au
CORS_ORIGINS=https://agent.theprofitplatform.com.au

# API Settings
API_PORT=8000
API_HOST=0.0.0.0

# Dashboard
DASHBOARD_PORT=80
VITE_API_URL=/api/v1
VITE_WS_URL=/ws

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GF_ADMIN_USER=admin
GF_ADMIN_PASSWORD=$(openssl rand -hex 12)

# Agents
PLANNING_AGENTS=2
EXECUTION_AGENTS=3
RESEARCH_AGENTS=2
EOF

# 6. Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down 2>/dev/null || true

# 7. Build and start containers
echo "🐳 Building and starting Docker containers..."
docker-compose up -d --build

# 8. Configure Nginx
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/agentzero << 'NGINX_CONFIG'
server {
    listen 80;
    server_name agent.theprofitplatform.com.au;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name agent.theprofitplatform.com.au;

    # SSL certificates (will be added by certbot)
    # ssl_certificate /etc/letsencrypt/live/agent.theprofitplatform.com.au/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/agent.theprofitplatform.com.au/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Dashboard proxy
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket proxy
    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }

    # API documentation
    location /docs {
        proxy_pass http://localhost:8000/docs;
    }

    location /openapi.json {
        proxy_pass http://localhost:8000/openapi.json;
    }
}
NGINX_CONFIG

# Enable nginx site
ln -sf /etc/nginx/sites-available/agentzero /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

# Test and reload nginx
nginx -t && systemctl reload nginx

# 9. Get SSL certificate
echo "🔒 Getting SSL certificate from Let's Encrypt..."
certbot --nginx -d agent.theprofitplatform.com.au \
    --non-interactive \
    --agree-tos \
    --email admin@theprofitplatform.com.au \
    --redirect

# 10. Wait for services to be ready
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

# 11. Health check
echo "🏥 Performing health check..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is healthy!"
else
    echo "⚠️  API not ready yet. Check logs: docker-compose logs api"
fi

# 12. Save credentials
GRAFANA_PASS=$(grep GF_ADMIN_PASSWORD .env | cut -d= -f2)
cat > /root/agentzero_credentials.txt << CREDENTIALS
═══════════════════════════════════════════════════════════════════
🎉 AGENTZERO DEPLOYED SUCCESSFULLY!
═══════════════════════════════════════════════════════════════════

🌐 ACCESS POINTS:
───────────────────────────────────────────────────────────────────
Dashboard:    https://agent.theprofitplatform.com.au
API Docs:     https://agent.theprofitplatform.com.au/docs
Health Check: https://agent.theprofitplatform.com.au/health
Grafana:      https://agent.theprofitplatform.com.au/grafana

📧 LOGIN CREDENTIALS:
───────────────────────────────────────────────────────────────────
Dashboard:
  Username: admin
  Password: secret

Grafana Monitoring:
  Username: admin
  Password: $GRAFANA_PASS

🔧 USEFUL COMMANDS:
───────────────────────────────────────────────────────────────────
View logs:       cd /var/www/agentzero && docker-compose logs -f
Check status:    cd /var/www/agentzero && docker-compose ps
Restart:         cd /var/www/agentzero && docker-compose restart
Stop:            cd /var/www/agentzero && docker-compose down
Update:          cd /var/www/agentzero && git pull && docker-compose up -d --build

📁 LOCATIONS:
───────────────────────────────────────────────────────────────────
Project:         /var/www/agentzero
Environment:     /var/www/agentzero/.env
Nginx Config:    /etc/nginx/sites-available/agentzero
This File:       /root/agentzero_credentials.txt

═══════════════════════════════════════════════════════════════════
CREDENTIALS

echo "
╔════════════════════════════════════════════════════════════════╗
║              ✅ DEPLOYMENT COMPLETE!                           ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║   🌐 Your AgentZero system is now live at:                    ║
║      https://agent.theprofitplatform.com.au                   ║
║                                                                ║
║   📧 Login with: admin / secret                               ║
║                                                                ║
║   📄 Credentials saved to:                                    ║
║      /root/agentzero_credentials.txt                          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"

echo "🔍 Quick verification:"
echo "───────────────────────"
curl -s https://agent.theprofitplatform.com.au/health | python3 -m json.tool || echo "Still starting up..."
echo ""
echo "📊 Container status:"
echo "───────────────────────"
cd /var/www/agentzero && docker-compose ps