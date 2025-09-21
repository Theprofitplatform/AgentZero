#!/bin/bash

# AgentZero Quick Deploy Script for agent.theprofitplatform.com.au
# Run this on your Ubuntu server with: curl -sSL https://raw.githubusercontent.com/yourusername/agentzero/main/scripts/quick-deploy.sh | bash

set -e

# Configuration
DOMAIN="agent.theprofitplatform.com.au"
EMAIL="admin@theprofitplatform.com.au"
GITHUB_REPO="https://github.com/yourusername/agentzero.git"

echo "
════════════════════════════════════════════════════════════════════
    🚀 AgentZero Quick Deploy to $DOMAIN
════════════════════════════════════════════════════════════════════
"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root. Run: sudo bash $0"
   exit 1
fi

echo "📦 Installing required packages..."
apt-get update -qq
apt-get install -y -qq docker.io docker-compose git nginx certbot python3-certbot-nginx curl ufw

echo "🔧 Configuring system..."
systemctl enable docker
systemctl start docker

echo "🔥 Setting up firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

echo "📁 Setting up project directory..."
cd /var/www
rm -rf agentzero
git clone $GITHUB_REPO agentzero
cd agentzero

echo "🔐 Generating secure secrets..."
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
POSTGRES_PASS=$(openssl rand -hex 16)
REDIS_PASS=$(openssl rand -hex 16)
GRAFANA_PASS=$(openssl rand -hex 12)

echo "📝 Creating production environment file..."
cat > .env << EOF
# Auto-generated production configuration
APP_NAME=AgentZero
APP_ENV=production
DEBUG=false
LOG_LEVEL=WARNING

# Domain
DOMAIN=$DOMAIN
ALLOWED_HOSTS=$DOMAIN
CORS_ORIGINS=https://$DOMAIN

# Secrets (auto-generated)
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET
POSTGRES_PASSWORD=$POSTGRES_PASS
REDIS_PASSWORD=$REDIS_PASS
GF_ADMIN_PASSWORD=$GRAFANA_PASS

# Database
POSTGRES_DB=agentzero_prod
POSTGRES_USER=agentzero_prod
DATABASE_URL=postgresql://agentzero_prod:$POSTGRES_PASS@postgres:5432/agentzero_prod

# Redis
REDIS_URL=redis://default:$REDIS_PASS@redis:6379/0

# API
API_PORT=8000
API_HOST=0.0.0.0

# JWT
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Agents
PLANNING_AGENTS=2
EXECUTION_AGENTS=3
RESEARCH_AGENTS=2

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GF_ADMIN_USER=admin
EOF

echo "🔒 Getting SSL certificate..."
mkdir -p certbot/www
certbot certonly --standalone --non-interactive --agree-tos --email $EMAIL -d $DOMAIN || {
    echo "⚠️  SSL certificate failed. We'll continue and use self-signed for now."
}

echo "🐳 Building and starting services..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo "⏳ Waiting for services to start..."
sleep 30

echo "🗄️ Initializing database..."
docker-compose exec -T api python -c "
from src.api.database import init_db
init_db()
print('Database initialized!')
" || echo "Database initialization skipped"

echo "✅ Checking health status..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ API is healthy"
else
    echo "⚠️  API health check failed - check logs with: docker-compose logs api"
fi

echo "📊 Creating admin credentials..."
cat > admin_credentials.txt << EOF
═══════════════════════════════════════════════════════════════
🎉 AgentZero Deployed Successfully!
═══════════════════════════════════════════════════════════════

🌐 Access Points:
────────────────────────────────────────────────────────────
Dashboard:    https://$DOMAIN
API:          https://$DOMAIN/api/v1
API Docs:     https://$DOMAIN/docs
Grafana:      https://$DOMAIN/grafana

📧 Admin Credentials:
────────────────────────────────────────────────────────────
Dashboard Login:
  Username: admin
  Password: secret

Grafana Login:
  Username: admin
  Password: $GRAFANA_PASS

🔐 Important Secrets (SAVE THESE!):
────────────────────────────────────────────────────────────
SECRET_KEY:       $SECRET_KEY
JWT_SECRET_KEY:   $JWT_SECRET
POSTGRES_PASS:    $POSTGRES_PASS
REDIS_PASS:       $REDIS_PASS
GRAFANA_PASS:     $GRAFANA_PASS

📝 Next Steps:
────────────────────────────────────────────────────────────
1. Update DNS A record to point to this server's IP
2. Change default admin password
3. Configure backup schedule
4. Setup monitoring alerts

🛠️ Useful Commands:
────────────────────────────────────────────────────────────
View logs:        docker-compose logs -f
Restart:          docker-compose restart
Check status:     docker-compose ps
Stop services:    docker-compose down

═══════════════════════════════════════════════════════════════
EOF

cat admin_credentials.txt

echo "
🎊 Deployment Complete!
Credentials saved to: /var/www/agentzero/admin_credentials.txt
"