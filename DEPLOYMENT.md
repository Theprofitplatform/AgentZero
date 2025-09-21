# AgentZero Deployment Guide for agent.theprofitplatform.com.au

## 🚀 Quick Deployment

### Prerequisites
- Ubuntu 20.04+ server with root access
- Domain pointed to server IP (agent.theprofitplatform.com.au)
- GitHub repository with the code
- Minimum 4GB RAM, 2 CPU cores

### Step 1: Initial Server Setup

SSH into your server and run:

```bash
# Download and run the deployment script
wget https://raw.githubusercontent.com/yourusername/agentzero/main/scripts/deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh
```

This script will:
- Install Docker, Docker Compose, Nginx, Certbot
- Setup firewall rules
- Create deployment user
- Setup SSL certificates
- Deploy the application

### Step 2: Configure Environment Variables

Edit the production environment file:

```bash
sudo nano /var/www/agentzero/.env
```

Update these critical values:
```env
SECRET_KEY=<generate-with-openssl-rand-hex-32>
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
POSTGRES_PASSWORD=<strong-database-password>
REDIS_PASSWORD=<strong-redis-password>
GF_ADMIN_PASSWORD=<grafana-admin-password>
```

### Step 3: GitHub Actions Setup

In your GitHub repository settings, add these secrets:

1. Go to Settings > Secrets and variables > Actions
2. Add the following secrets:

```
DEPLOY_HOST: Your server IP or hostname
DEPLOY_USER: deploy
DEPLOY_KEY: Your SSH private key
SLACK_WEBHOOK: (Optional) Slack webhook URL for notifications
```

### Step 4: Deploy

Push to main branch to trigger automatic deployment:

```bash
git push origin main
```

## 📋 Manual Deployment Steps

If you prefer manual deployment:

### 1. Clone Repository

```bash
cd /var/www
sudo git clone https://github.com/yourusername/agentzero.git
cd agentzero
```

### 2. Setup Environment

```bash
cp .env.production .env
# Edit .env with production values
nano .env
```

### 3. Get SSL Certificate

```bash
sudo certbot certonly --nginx -d agent.theprofitplatform.com.au
```

### 4. Build and Start Services

```bash
# Build images
sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start services
sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check status
sudo docker-compose ps
```

### 5. Initialize Database

```bash
# Run migrations
sudo docker-compose exec api python -m alembic upgrade head

# Create admin user (optional)
sudo docker-compose exec api python scripts/create_admin.py
```

## 🔒 Security Checklist

- [ ] Change all default passwords in `.env`
- [ ] Setup SSH key authentication only
- [ ] Configure firewall (ufw)
- [ ] Enable fail2ban
- [ ] Setup regular backups
- [ ] Enable monitoring alerts
- [ ] Configure rate limiting
- [ ] Setup log rotation
- [ ] Review CORS settings
- [ ] Enable HTTPS only

## 📊 Monitoring

### Access Points

- **Main Application**: https://agent.theprofitplatform.com.au
- **API Documentation**: https://agent.theprofitplatform.com.au/docs
- **Grafana Dashboard**: https://agent.theprofitplatform.com.au/grafana
  - Default login: admin / (password you set)
- **Health Check**: https://agent.theprofitplatform.com.au/health

### Check Application Logs

```bash
# API logs
sudo docker-compose logs -f api

# Agent logs
sudo docker-compose logs -f planning-agent execution-agent

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Monitor System Resources

```bash
# Docker stats
sudo docker stats

# System resources
htop

# Disk usage
df -h
```

## 🔄 Updates and Maintenance

### Update Application

```bash
cd /var/www/agentzero
sudo git pull origin main
sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Backup Database

```bash
# Manual backup
sudo docker-compose exec postgres pg_dump -U agentzero_prod agentzero_prod > backup_$(date +%Y%m%d).sql

# Restore from backup
sudo docker-compose exec -T postgres psql -U agentzero_prod agentzero_prod < backup_20240101.sql
```

### SSL Certificate Renewal

Certificates auto-renew via cron, but you can manually renew:

```bash
sudo certbot renew --dry-run  # Test renewal
sudo certbot renew             # Actual renewal
```

## 🚨 Troubleshooting

### Services Not Starting

```bash
# Check Docker logs
sudo docker-compose logs

# Restart services
sudo docker-compose restart

# Rebuild if needed
sudo docker-compose down
sudo docker-compose build --no-cache
sudo docker-compose up -d
```

### Database Connection Issues

```bash
# Check PostgreSQL status
sudo docker-compose exec postgres pg_isready

# Reset database
sudo docker-compose down -v
sudo docker-compose up -d
```

### SSL/HTTPS Issues

```bash
# Check certificate status
sudo certbot certificates

# Restart Nginx
sudo systemctl restart nginx

# Check Nginx configuration
sudo nginx -t
```

### Performance Issues

```bash
# Scale up agents
sudo docker-compose up -d --scale execution-agent=5

# Increase resource limits in docker-compose.prod.yml
# Then restart services
```

## 📞 Support

For issues or questions:
- Check logs first: `sudo docker-compose logs`
- Review health endpoint: https://agent.theprofitplatform.com.au/health
- Check GitHub Issues: https://github.com/yourusername/agentzero/issues

## 🔐 Production Secrets Management

Never commit secrets to git! Use environment variables or secret management services:

1. **Local Development**: Use `.env` file (gitignored)
2. **Production**: Use server environment or secret manager
3. **CI/CD**: Use GitHub Secrets or similar

## 🎯 Post-Deployment Tasks

1. **Test all endpoints**:
   - Login functionality
   - Agent creation and management
   - Task submission and processing
   - WebSocket connections

2. **Setup monitoring alerts** in Grafana for:
   - High CPU/memory usage
   - Failed tasks
   - Agent failures
   - API errors

3. **Configure backups**:
   - Automated daily database backups
   - Volume backups
   - Off-site backup storage

4. **Performance tuning**:
   - Adjust agent counts based on load
   - Optimize database queries
   - Configure caching

5. **Security hardening**:
   - Regular security updates
   - Penetration testing
   - Security audit logs