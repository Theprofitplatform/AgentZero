# 🚀 DEPLOY AGENTZERO TO agent.theprofitplatform.com.au - RIGHT NOW!

## Prerequisites Check ✅

You need:
1. **Ubuntu Server** (20.04 or newer) with root access
2. **Domain DNS** pointed to your server's IP address
3. **Server Specs**: Minimum 2GB RAM, 2 CPU cores, 20GB storage

## 🎯 STEP 1: Get Your Server Ready

First, check if your domain is pointing to your server:

```bash
# On your local machine, check DNS:
nslookup agent.theprofitplatform.com.au
# Should return your server's IP address
```

## 🎯 STEP 2: Push Code to GitHub

From your local AgentZero project:

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/agentzero.git
git push -u origin main
```

## 🎯 STEP 3: Deploy to Server (Copy & Paste These Commands)

SSH into your server and run these commands **EXACTLY**:

### Option A: One-Line Deploy (Recommended)

```bash
# SSH into your server first:
ssh root@YOUR_SERVER_IP

# Then run this single command:
curl -o deploy.sh https://raw.githubusercontent.com/YOUR_USERNAME/agentzero/main/scripts/quick-deploy.sh && chmod +x deploy.sh && sudo ./deploy.sh
```

### Option B: Step-by-Step Deploy

If the one-liner doesn't work, run these commands one by one:

```bash
# 1. SSH into your server
ssh root@YOUR_SERVER_IP

# 2. Update system and install Docker
apt update && apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose git nginx certbot python3-certbot-nginx -y

# 3. Setup firewall
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

# 4. Clone your repository
cd /var/www
git clone https://github.com/YOUR_USERNAME/agentzero.git
cd agentzero

# 5. Generate secure passwords
export SECRET_KEY=$(openssl rand -hex 32)
export JWT_SECRET=$(openssl rand -hex 32)
export DB_PASS=$(openssl rand -hex 16)
export REDIS_PASS=$(openssl rand -hex 16)

# 6. Create production config
cat > .env << EOF
APP_NAME=AgentZero
APP_ENV=production
DEBUG=false
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET
POSTGRES_PASSWORD=$DB_PASS
REDIS_PASSWORD=$REDIS_PASS
POSTGRES_DB=agentzero
POSTGRES_USER=agentzero
DATABASE_URL=postgresql://agentzero:$DB_PASS@postgres:5432/agentzero
REDIS_URL=redis://default:$REDIS_PASS@redis:6379/0
CORS_ORIGINS=https://agent.theprofitplatform.com.au
GF_ADMIN_PASSWORD=admin123
EOF

# 7. Get SSL certificate
certbot certonly --standalone -d agent.theprofitplatform.com.au --non-interactive --agree-tos --email admin@theprofitplatform.com.au

# 8. Build and start everything
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# 9. Check if it's working
sleep 30
docker-compose ps
curl http://localhost:8000/health
```

## 🎯 STEP 4: Setup Nginx Reverse Proxy

```bash
# Create Nginx config
cat > /etc/nginx/sites-available/agentzero << 'EOF'
server {
    listen 80;
    server_name agent.theprofitplatform.com.au;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name agent.theprofitplatform.com.au;

    ssl_certificate /etc/letsencrypt/live/agent.theprofitplatform.com.au/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/agent.theprofitplatform.com.au/privkey.pem;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/agentzero /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx
```

## 🎯 STEP 5: Verify Deployment

```bash
# Check all services are running
docker-compose ps

# Check API health
curl https://agent.theprofitplatform.com.au/health

# View logs if needed
docker-compose logs -f
```

## ✅ YOUR SITE IS LIVE!

Access your deployed application:

🌐 **Dashboard**: https://agent.theprofitplatform.com.au
📚 **API Docs**: https://agent.theprofitplatform.com.au/docs
🔑 **Login**: admin / secret

## 🚨 TROUBLESHOOTING

If something doesn't work:

```bash
# Check Docker containers
docker ps -a

# Check logs
docker-compose logs api
docker-compose logs dashboard

# Restart everything
docker-compose down
docker-compose up -d

# Check Nginx
systemctl status nginx
nginx -t

# Check SSL certificate
certbot certificates
```

## 📱 Quick Test Commands

Once deployed, test from your local machine:

```bash
# Test API
curl https://agent.theprofitplatform.com.au/health

# Test dashboard
curl -I https://agent.theprofitplatform.com.au

# Test WebSocket
wscat -c wss://agent.theprofitplatform.com.au/ws
```

## 🔐 IMPORTANT: Secure Your Deployment

After deployment, immediately:

1. **Change default password**:
   - Login to dashboard
   - Go to Settings > Change Password

2. **Save your secrets** from `.env` file:
   ```bash
   cat /var/www/agentzero/.env | grep -E "SECRET_KEY|PASSWORD"
   ```

3. **Setup backups**:
   ```bash
   # Add to crontab
   0 2 * * * docker-compose exec postgres pg_dump -U agentzero agentzero > /backups/db_$(date +\%Y\%m\%d).sql
   ```

---

## 💡 Need Help?

If you get stuck at any step:

1. Check logs: `docker-compose logs`
2. Check service health: `docker-compose ps`
3. Restart services: `docker-compose restart`

The deployment should take about 5-10 minutes total.