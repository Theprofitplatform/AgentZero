# AgentZero Usage Guide

## Quick Start

### 1. Setup Python Environment
```bash
cd /home/avi/projects/agentzero
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Basic Usage - Interactive Mode
```bash
python main.py --mode interactive
```

This starts an interactive shell where you can:
- `research <topic>` - Research any topic using web agents
- `code <description>` - Generate code for your requirements
- `analyze <file>` - Analyze existing code files
- `status` - Check system and agent status
- `quit` - Exit the system

### 3. Docker Deployment (Full System)
```bash
# Start all services with Docker
docker-compose up -d

# Check running services
docker ps

# View logs
docker-compose logs -f hive-coordinator
docker-compose logs -f research-agent
```

## Usage Methods

### Method 1: Command Line Interface

#### Interactive Mode (Default)
```bash
python main.py

# Examples:
AgentZero> research latest AI developments in 2024
AgentZero> code create a REST API for user authentication
AgentZero> analyze /path/to/your/code.py
AgentZero> status
```

#### Batch Mode
Create a tasks file:
```bash
echo "research quantum computing breakthroughs" > tasks.txt
echo "code implement binary search in Python" >> tasks.txt
echo "research best practices for microservices" >> tasks.txt

# Run batch processing
python main.py --mode batch --tasks tasks.txt
```

#### Server Mode (API)
```bash
python main.py --mode server --port 8000
```

### Method 2: Python API

```python
import asyncio
from main import AgentZeroSystem

async def use_agentzero():
    # Initialize system
    system = AgentZeroSystem({
        "research_agents": 3,
        "code_agents": 2
    })
    await system.initialize()
    
    # Start system in background
    asyncio.create_task(system.start())
    
    # Submit tasks
    task1 = await system.submit_task(
        "Research the latest developments in quantum computing",
        task_type="research"
    )
    
    task2 = await system.submit_task(
        "Generate a Python class for managing a todo list",
        task_type="code_generation"
    )
    
    # Check status
    status = await system.get_status()
    print(f"Active tasks: {status['hive']['active_tasks']}")
    
    # Wait for completion
    await asyncio.sleep(10)
    
    # Shutdown
    system.shutdown()

# Run
asyncio.run(use_agentzero())
```

### Method 3: Direct Script Usage

```python
#!/usr/bin/env python3
import sys
sys.path.append('/home/avi/projects/agentzero')

from src.agents.research_agent import ResearchAgent
from src.agents.code_agent import CodeAgent
from src.core.agent import Task, Priority
import asyncio

async def simple_research():
    # Create a research agent
    agent = ResearchAgent(name="MyResearcher")
    
    # Create a task
    task = Task(
        name="Research AI trends",
        description="Find latest AI trends and developments",
        priority=Priority.HIGH
    )
    
    # Execute task
    result = await agent.execute(task)
    print(f"Research results: {result}")
    
    agent.shutdown()

asyncio.run(simple_research())
```

## Configuration Options

### Command Line Arguments
```bash
python main.py \
    --mode interactive \           # interactive, batch, or server
    --research-agents 3 \          # Number of research agents
    --code-agents 2 \              # Number of code agents
    --port 8000                    # Port for server mode
```

### Environment Variables
```bash
export HIVE_ID=main-hive
export DISTRIBUTION_STRATEGY=capability_based
export LOG_LEVEL=INFO
export RESEARCH_AGENTS=3
export CODE_AGENTS=2
```

### Configuration File
Create `config/agentzero.yml`:
```yaml
hive:
  distribution_strategy: capability_based
  max_tasks_per_agent: 5
  heartbeat_interval: 30

agents:
  research:
    count: 3
    max_depth: 3
    max_pages: 50
  code:
    count: 2
    languages:
      - python
      - javascript
      - typescript
```

## Practical Examples

### Example 1: Research and Code Generation
```python
# research_and_code.py
import asyncio
from main import AgentZeroSystem

async def research_and_implement():
    system = AgentZeroSystem()
    await system.initialize()
    asyncio.create_task(system.start())
    
    # First research
    research_id = await system.submit_task(
        "Research best practices for REST API design",
        task_type="research"
    )
    
    # Wait a bit for research
    await asyncio.sleep(5)
    
    # Then generate code based on research
    code_id = await system.submit_task(
        "Generate a REST API following best practices with user CRUD operations",
        task_type="code_generation"
    )
    
    # Monitor progress
    while True:
        status = await system.get_status()
        print(f"Tasks - Active: {status['hive']['active_tasks']}, "
              f"Completed: {status['hive']['completed_tasks']}")
        
        if status['hive']['active_tasks'] == 0:
            break
        await asyncio.sleep(2)
    
    system.shutdown()

asyncio.run(research_and_implement())
```

### Example 2: Parallel Task Processing
```bash
# Create multiple tasks file
cat > parallel_tasks.txt << EOF
research machine learning frameworks comparison
code implement quicksort algorithm in Python
research microservices vs monolithic architecture
code create a simple web scraper with BeautifulSoup
research blockchain consensus mechanisms
EOF

# Run with more agents for parallel processing
python main.py \
    --mode batch \
    --tasks parallel_tasks.txt \
    --research-agents 3 \
    --code-agents 2
```

### Example 3: Continuous Monitoring
```python
# monitor.py
import asyncio
import time
from main import AgentZeroSystem

async def monitor_system():
    system = AgentZeroSystem()
    await system.initialize()
    asyncio.create_task(system.start())
    
    # Submit tasks periodically
    tasks = [
        "research latest cybersecurity threats",
        "code implement data encryption utility",
        "research cloud computing trends"
    ]
    
    for task in tasks:
        await system.submit_task(task)
        await asyncio.sleep(2)
    
    # Monitor until complete
    start_time = time.time()
    while True:
        status = await system.get_status()
        elapsed = time.time() - start_time
        
        print(f"\n[{elapsed:.1f}s] System Status:")
        print(f"  Agents: {status['hive']['agents']}")
        print(f"  Active: {status['hive']['active_tasks']}")
        print(f"  Queued: {status['hive']['queued_tasks']}")
        print(f"  Completed: {status['hive']['completed_tasks']}")
        print(f"  Efficiency: {status['hive']['metrics']['hive_efficiency']:.2%}")
        
        if status['hive']['active_tasks'] == 0 and status['hive']['queued_tasks'] == 0:
            break
        
        await asyncio.sleep(3)
    
    print("\nAll tasks completed!")
    system.shutdown()

asyncio.run(monitor_system())
```

## Monitoring & Debugging

### View Logs
```bash
# Real-time logs
tail -f logs/*.log

# Filter by agent type
grep "ResearchAgent" logs/*.log
grep "CodeAgent" logs/*.log

# Check errors
grep "ERROR" logs/*.log
```

### Check System Status
```python
# status_check.py
import asyncio
from main import AgentZeroSystem

async def check_status():
    system = AgentZeroSystem()
    await system.initialize()
    
    status = await system.get_status()
    
    print("=== HIVE STATUS ===")
    for key, value in status['hive']['metrics'].items():
        print(f"{key}: {value}")
    
    print("\n=== AGENT STATUS ===")
    for agent in status['agents']:
        print(f"{agent['name']}: {agent['status']}")
        print(f"  Queue: {agent['queue_size']}")
        print(f"  Success Rate: {agent['metrics']['success_rate']:.2%}")
    
    system.shutdown()

asyncio.run(check_status())
```

### Access Monitoring Dashboard
If using Docker deployment:
```bash
# Grafana dashboard (if configured)
open http://localhost:3000
# Default: admin/admin

# Prometheus metrics
open http://localhost:9090
```

## Troubleshooting

### Common Issues

1. **Import Errors**
```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

2. **No Agents Available**
```bash
# Start with more agents
python main.py --research-agents 4 --code-agents 3
```

3. **Tasks Not Processing**
```python
# Check agent capabilities match task requirements
status = await system.get_status()
print(status['agents'])  # Verify agents are running
```

4. **Docker Issues**
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check container logs
docker-compose logs -f
```

## Tips for Best Results

1. **Task Descriptions**: Be specific and clear in task descriptions
2. **Agent Balance**: Use more research agents for information gathering, more code agents for development tasks
3. **Priority Levels**: Use HIGH priority for urgent tasks
4. **Batch Processing**: Group similar tasks together for efficiency
5. **Monitor Performance**: Check hive efficiency regularly and adjust agent counts

## Next Steps

- Explore creating custom agents in `src/agents/`
- Modify distribution strategies in the hive coordinator
- Add new capabilities to existing agents
- Integrate with external APIs and services
- Set up the web dashboard for visual monitoring