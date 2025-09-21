# AgentZero Development Environment Setup Guide

## Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+, macOS 12+, or Windows 11 with WSL2
- **Python**: 3.9 or higher
- **Node.js**: 18.x or higher (for dashboard)
- **Docker**: 20.10+ with Docker Compose
- **Git**: 2.25+
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk**: 10GB free space

### Required Software Installation

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3.9 python3.9-venv python3-pip -y

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install Docker
curl -fsSL https://get.docker.com | sudo bash
sudo usermod -aG docker $USER

# Install Redis (optional, can use Docker)
sudo apt install redis-server -y

# Install PostgreSQL (optional, can use Docker)
sudo apt install postgresql postgresql-contrib -y
```

#### macOS
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.9

# Install Node.js
brew install node@18

# Install Docker Desktop
# Download from https://www.docker.com/products/docker-desktop/

# Install Redis (optional)
brew install redis

# Install PostgreSQL (optional)
brew install postgresql@15
```

#### Windows (WSL2)
```powershell
# Install WSL2 first
wsl --install

# Inside WSL2, follow Ubuntu instructions above
```

## Project Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/AgentZero.git
cd AgentZero

# Create development branch
git checkout -b develop
```

### 2. Python Environment Setup
```bash
# Create virtual environment
python3.9 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 3. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

**.env Configuration**:
```env
# Core Configuration
HIVE_ID=dev-hive
DISTRIBUTION_STRATEGY=capability_based
LOG_LEVEL=DEBUG
MAX_AGENTS_PER_TYPE=5

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=2
JWT_SECRET=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY=3600

# Database Configuration
REDIS_URL=redis://localhost:6379/0
POSTGRES_URL=postgresql://agentzero:password@localhost/agentzero_dev

# WebSocket Configuration
WS_HOST=0.0.0.0
WS_PORT=8001
WS_PING_INTERVAL=30
WS_MAX_CONNECTIONS=100

# Security Configuration
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
COMMAND_TIMEOUT=300
COMMAND_WHITELIST_ENABLED=true

# Dashboard Configuration
DASHBOARD_URL=http://localhost:3000
API_BASE_URL=http://localhost:8000

# Development Settings
DEBUG=true
RELOAD=true
TESTING=false
```

### 4. Database Setup

#### Option A: Using Docker (Recommended)
```bash
# Start services with Docker Compose
docker-compose up -d redis postgres

# Verify services are running
docker ps

# The services will be available at:
# Redis: localhost:6379
# PostgreSQL: localhost:5432
```

#### Option B: Local Installation
```bash
# Redis
redis-server --daemonize yes

# PostgreSQL - Create database
sudo -u postgres psql
CREATE USER agentzero WITH PASSWORD 'password';
CREATE DATABASE agentzero_dev OWNER agentzero;
GRANT ALL PRIVILEGES ON DATABASE agentzero_dev TO agentzero;
\q

# Run database migrations (if applicable)
alembic upgrade head
```

### 5. Dashboard Setup
```bash
# Navigate to dashboard directory
cd dashboard

# Install dependencies
npm install

# Create environment file
cp .env.example .env.development

# Start development server
npm run dev

# Dashboard will be available at http://localhost:3000
```

### 6. IDE Configuration

#### VS Code
Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreter": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.rulers": [88]
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: AgentZero",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/main.py",
      "args": ["--mode", "interactive"],
      "console": "integratedTerminal",
      "envFile": "${workspaceFolder}/.env"
    },
    {
      "name": "Python: API Server",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["src.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
      "console": "integratedTerminal",
      "envFile": "${workspaceFolder}/.env"
    },
    {
      "name": "Dashboard",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/dashboard/src"
    }
  ]
}
```

#### PyCharm
1. Open project in PyCharm
2. Configure Python Interpreter:
   - File → Settings → Project → Python Interpreter
   - Select `venv/bin/python`
3. Configure Run Configurations:
   - Run → Edit Configurations
   - Add Python configuration for `main.py`
   - Add npm configuration for dashboard

## Running the System

### 1. Start Core Services
```bash
# Terminal 1: Start Redis (if not using Docker)
redis-server

# Terminal 2: Start Hive Coordinator
python main.py --mode interactive

# Terminal 3: Start API Server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 4: Start WebSocket Server
python src/api/websocket_server.py

# Terminal 5: Start Dashboard
cd dashboard && npm run dev
```

### 2. Using Docker Compose (All Services)
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Development Commands

#### Python Development
```bash
# Run tests
pytest

# Run specific test file
pytest tests/test_planning_agent.py

# Run with coverage
pytest --cov=src --cov-report=html

# Format code
black src/

# Lint code
flake8 src/
pylint src/

# Type checking
mypy src/
```

#### Dashboard Development
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port
sudo lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in .env file
```

#### 2. Redis Connection Error
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:7-alpine
```

#### 3. Python Import Errors
```bash
# Ensure virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 4. Dashboard Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### 5. Docker Issues
```bash
# Reset Docker
docker system prune -a
docker-compose build --no-cache
docker-compose up
```

### Performance Optimization

#### Development Mode
- Use fewer agents for faster startup
- Reduce log level to WARNING
- Disable unnecessary services

#### Resource Limits
```bash
# Limit Docker resources in docker-compose.yml
services:
  hive:
    mem_limit: 512m
    cpus: '0.5'
```

## Testing Setup

### 1. Unit Testing
```bash
# Run all unit tests
pytest tests/unit -v

# Run with debugging
pytest tests/unit -v -s

# Run specific test
pytest tests/unit/test_planning_agent.py::test_create_plan
```

### 2. Integration Testing
```bash
# Start test services
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration -v

# Cleanup
docker-compose -f docker-compose.test.yml down
```

### 3. End-to-End Testing
```bash
# Install Selenium
pip install selenium

# Download Chrome driver
wget https://chromedriver.storage.googleapis.com/latest/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/

# Run E2E tests
pytest tests/e2e -v
```

## Git Workflow

### Branch Structure
- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Emergency fixes

### Commit Guidelines
```bash
# Feature commit
git commit -m "feat: Add Planning Agent task decomposition"

# Bug fix commit
git commit -m "fix: Resolve WebSocket reconnection issue"

# Documentation commit
git commit -m "docs: Update API documentation"

# Test commit
git commit -m "test: Add integration tests for Execution Agent"

# Refactor commit
git commit -m "refactor: Optimize task queue processing"
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

## Debugging

### Python Debugging
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use ipdb for better experience
import ipdb; ipdb.set_trace()

# For async code
import asyncio
import aiodebug
asyncio.run(main(), debug=True)
```

### API Debugging
```bash
# Use HTTPie for API testing
pip install httpie

# Test endpoint
http GET localhost:8000/api/v1/agents Authorization:"Bearer $TOKEN"

# Use curl with verbose output
curl -v -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/agents
```

### Dashboard Debugging
```javascript
// Add debugger statement
debugger;

// Or use console.log
console.log('Debug:', variable);

// React Developer Tools
// Install Chrome extension for component inspection
```

## Monitoring

### Local Monitoring
```bash
# Monitor system resources
htop

# Monitor Docker containers
docker stats

# Monitor Python process
py-spy top -p <PID>

# Monitor API requests
tail -f logs/api.log | grep -E "ERROR|WARNING"
```

### Application Metrics
```python
# Access metrics endpoint
curl http://localhost:8000/metrics

# Prometheus metrics (if configured)
curl http://localhost:9090/metrics
```

## Next Steps

1. **Complete Environment Setup**: Ensure all services are running
2. **Run Tests**: Verify everything works with `pytest`
3. **Read Documentation**: Review `/docs/` folder
4. **Start Development**: Pick a story from `/docs/stories/`
5. **Join Communication**: Set up team chat/channels

## Support

- **Documentation**: `/docs/` folder
- **BMad Guide**: `/.bmad-core/user-guide.md`
- **Issues**: Create GitHub issue
- **Team Chat**: [Your team communication platform]

---
**Created**: 2025-09-21
**Last Updated**: 2025-09-21
**Setup Time**: ~30-60 minutes