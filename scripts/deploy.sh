#!/bin/bash

# AgentZero Production Deployment Script
# Deploy to agent.theprofitplatform.com.au

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="agent.theprofitplatform.com.au"
DEPLOY_USER="deploy"
PROJECT_DIR="/var/www/agentzero"
BACKUP_DIR="/var/backups/agentzero"
EMAIL="admin@theprofitplatform.com.au"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
    fi
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."

    apt-get update
    apt-get install -y \
        docker.io \
        docker-compose \
        nginx \
        certbot \
        python3-certbot-nginx \
        git \
        curl \
        htop \
        ufw \
        fail2ban

    # Enable Docker
    systemctl enable docker
    systemctl start docker

    log "Dependencies installed successfully"
}

# Setup firewall
setup_firewall() {
    log "Configuring firewall..."

    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow http
    ufw allow https
    ufw allow 8000/tcp  # API port (internal)

    ufw --force enable

    log "Firewall configured"
}

# Create deployment user
create_deploy_user() {
    log "Creating deployment user..."

    if ! id "$DEPLOY_USER" &>/dev/null; then
        useradd -m -s /bin/bash $DEPLOY_USER
        usermod -aG docker $DEPLOY_USER
        usermod -aG sudo $DEPLOY_USER

        # Setup SSH key for deployment
        mkdir -p /home/$DEPLOY_USER/.ssh
        touch /home/$DEPLOY_USER/.ssh/authorized_keys
        chmod 700 /home/$DEPLOY_USER/.ssh
        chmod 600 /home/$DEPLOY_USER/.ssh/authorized_keys
        chown -R $DEPLOY_USER:$DEPLOY_USER /home/$DEPLOY_USER/.ssh

        log "Deployment user created"
    else
        warning "Deployment user already exists"
    fi
}

# Setup project directory
setup_project_directory() {
    log "Setting up project directory..."

    mkdir -p $PROJECT_DIR
    mkdir -p $BACKUP_DIR
    mkdir -p $PROJECT_DIR/certbot/conf
    mkdir -p $PROJECT_DIR/certbot/www

    chown -R $DEPLOY_USER:$DEPLOY_USER $PROJECT_DIR
    chown -R $DEPLOY_USER:$DEPLOY_USER $BACKUP_DIR

    log "Project directory created"
}

# Clone or update repository
setup_repository() {
    log "Setting up repository..."

    cd $PROJECT_DIR

    if [ ! -d ".git" ]; then
        git clone https://github.com/yourusername/agentzero.git .
    else
        git pull origin main
    fi

    # Copy production environment file
    if [ ! -f ".env" ]; then
        cp .env.example .env
        warning "Please update .env file with production values!"
    fi

    log "Repository setup complete"
}

# Setup SSL certificates
setup_ssl() {
    log "Setting up SSL certificates..."

    # Check if certificates already exist
    if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        warning "SSL certificates already exist"
    else
        # Get certificates from Let's Encrypt
        certbot certonly \
            --webroot \
            --webroot-path=$PROJECT_DIR/certbot/www \
            --email $EMAIL \
            --agree-tos \
            --no-eff-email \
            -d $DOMAIN \
            --non-interactive

        # Setup auto-renewal
        echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | crontab -

        log "SSL certificates obtained"
    fi
}

# Build and start Docker containers
deploy_containers() {
    log "Building and deploying Docker containers..."

    cd $PROJECT_DIR

    # Build images
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

    # Stop existing containers
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

    # Start new containers
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

    # Wait for services to be healthy
    sleep 10

    # Check health
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

    log "Containers deployed successfully"
}

# Setup database
setup_database() {
    log "Setting up database..."

    cd $PROJECT_DIR

    # Run database migrations
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api python -m alembic upgrade head

    log "Database setup complete"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."

    # Create Grafana admin user
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T grafana \
        grafana-cli admin reset-admin-password admin@123

    log "Monitoring setup complete"
}

# Backup existing data
backup_data() {
    log "Backing up existing data..."

    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

    # Backup database
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T postgres \
        pg_dump -U agentzero agentzero > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

    # Backup volumes
    docker run --rm -v agentzero_postgres_data_prod:/data -v $BACKUP_DIR:/backup \
        alpine tar czf "/backup/postgres_data_$TIMESTAMP.tar.gz" -C /data .

    log "Backup completed: $BACKUP_FILE"
}

# Health check
health_check() {
    log "Running health checks..."

    # Check API
    if curl -f https://$DOMAIN/health > /dev/null 2>&1; then
        log "✓ API is healthy"
    else
        error "✗ API health check failed"
    fi

    # Check Dashboard
    if curl -f https://$DOMAIN > /dev/null 2>&1; then
        log "✓ Dashboard is accessible"
    else
        error "✗ Dashboard is not accessible"
    fi

    # Check SSL
    if echo | openssl s_client -connect $DOMAIN:443 2>/dev/null | grep -q "Verify return code: 0"; then
        log "✓ SSL certificate is valid"
    else
        warning "⚠ SSL certificate might have issues"
    fi

    log "Health checks completed"
}

# Main deployment process
main() {
    log "Starting AgentZero deployment to $DOMAIN"

    check_root
    install_dependencies
    setup_firewall
    create_deploy_user
    setup_project_directory
    setup_repository
    setup_ssl
    backup_data
    deploy_containers
    setup_database
    setup_monitoring
    health_check

    log "==========================================="
    log "Deployment completed successfully!"
    log "==========================================="
    log "Dashboard: https://$DOMAIN"
    log "API: https://$DOMAIN/api/v1"
    log "API Docs: https://$DOMAIN/docs"
    log "Grafana: https://$DOMAIN/grafana (admin/admin@123)"
    log "==========================================="
    warning "Remember to:"
    warning "1. Update .env file with production values"
    warning "2. Change all default passwords"
    warning "3. Configure backup schedule"
    warning "4. Setup monitoring alerts"
}

# Run main function
main "$@"