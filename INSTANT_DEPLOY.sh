#!/bin/bash

# INSTANT DEPLOY SCRIPT - Just paste this entire block into your server terminal

cat << 'DEPLOY_SCRIPT' > /tmp/deploy_agentzero.sh
#!/bin/bash
set -e

echo "
╔══════════════════════════════════════════════════════════════════╗
║     🚀 DEPLOYING AGENTZERO TO agent.theprofitplatform.com.au     ║
╚══════════════════════════════════════════════════════════════════╝
"

# Quick checks
if [[ $EUID -ne 0 ]]; then
   echo "❌ Run as root: sudo bash $0"
   exit 1
fi

echo "✅ Starting deployment..."

# 1. Install essentials
echo "📦 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
fi

if ! command -v docker-compose &> /dev/null; then
    apt-get update -qq
    apt-get install -y docker-compose git nginx certbot python3-certbot-nginx
fi

# 2. Setup firewall
echo "🔒 Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

# 3. Clone repository
echo "📥 Cloning repository..."
cd /var/www
rm -rf agentzero
git clone https://github.com/Theprofitplatform/AgentZero.git agentzero
cd agentzero

# 4. Generate secrets
echo "🔐 Generating secure passwords..."
cat > .env << EOF
APP_NAME=AgentZero
APP_ENV=production
DEBUG=false
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)
POSTGRES_DB=agentzero
POSTGRES_USER=agentzero
DATABASE_URL=postgresql://agentzero:$(openssl rand -hex 16)@postgres:5432/agentzero
REDIS_URL=redis://default:$(openssl rand -hex 16)@redis:6379/0
CORS_ORIGINS=https://agent.theprofitplatform.com.au
ALLOWED_HOSTS=agent.theprofitplatform.com.au
GF_ADMIN_PASSWORD=$(openssl rand -hex 12)
EOF

# 5. Build and start
echo "🐳 Starting Docker containers..."
docker-compose down 2>/dev/null || true
docker-compose up -d --build

# 6. Setup Nginx
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/agentzero << 'NGINX'
server {
    listen 80;
    server_name agent.theprofitplatform.com.au;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
    }

    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
NGINX

ln -sf /etc/nginx/sites-available/agentzero /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# 7. Get SSL certificate
echo "🔒 Getting SSL certificate..."
certbot --nginx -d agent.theprofitplatform.com.au --non-interactive --agree-tos --email admin@theprofitplatform.com.au --redirect

# 8. Wait for services
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

# 9. Check health
echo "🏥 Checking system health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is healthy!"
else
    echo "⚠️  API not responding yet, check logs: docker-compose logs api"
fi

# 10. Save credentials
cat > /root/agentzero_credentials.txt << CREDS
═══════════════════════════════════════════════════════════════
🎉 AGENTZERO DEPLOYED SUCCESSFULLY!
═══════════════════════════════════════════════════════════════

🌐 Access your system at:
─────────────────────────────────────────────────────────────
Dashboard:  https://agent.theprofitplatform.com.au
API Docs:   https://agent.theprofitplatform.com.au/docs
Health:     https://agent.theprofitplatform.com.au/health

📧 Login Credentials:
─────────────────────────────────────────────────────────────
Username: admin
Password: secret

🔧 Useful Commands:
─────────────────────────────────────────────────────────────
View logs:     cd /var/www/agentzero && docker-compose logs -f
Restart:       cd /var/www/agentzero && docker-compose restart
Check status:  cd /var/www/agentzero && docker-compose ps

═══════════════════════════════════════════════════════════════
CREDS

echo "
╔══════════════════════════════════════════════════════════════════╗
║     ✅ DEPLOYMENT COMPLETE!                                      ║
║                                                                   ║
║     🌐 Your site is live at:                                     ║
║     https://agent.theprofitplatform.com.au                       ║
║                                                                   ║
║     📧 Login with: admin / secret                                ║
║                                                                   ║
║     📄 Credentials saved to: /root/agentzero_credentials.txt     ║
╚══════════════════════════════════════════════════════════════════╝
"

DEPLOY_SCRIPT

chmod +x /tmp/deploy_agentzero.sh
sudo /tmp/deploy_agentzero.sh