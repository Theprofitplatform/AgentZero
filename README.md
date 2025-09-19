# AgentZero - Advanced Multi-Agent System with Hive Intelligence

## Overview

AgentZero is a sophisticated multi-agent system that leverages hive intelligence for collaborative problem-solving. It features specialized agents coordinated through a central hive system, enabling complex task execution through distributed intelligence.

## Features

### 🧠 Core Capabilities
- **Hive Coordination**: Central orchestrator managing multi-agent collaboration
- **Specialized Agents**: Purpose-built agents for specific domains
- **Distributed Intelligence**: Agents work together to solve complex problems
- **Adaptive Learning**: Agents learn from experience and improve over time
- **Scalable Architecture**: Easily add more agents as needed

### 🤖 Agent Types

1. **Research Agent**
   - Web searching and data gathering
   - Content extraction and analysis
   - Fact verification and validation
   - Sentiment analysis
   - Knowledge graph construction

2. **Code Agent**
   - Code generation in multiple languages
   - Code analysis and optimization
   - Debugging and error fixing
   - Refactoring suggestions
   - Test generation

3. **Planning Agent** (Coming Soon)
   - Strategic task decomposition
   - Resource allocation
   - Timeline management
   - Dependency resolution

4. **Execution Agent** (Coming Soon)
   - Task execution monitoring
   - System operations
   - Integration management

## Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose (optional)
- Redis (for message queue)
- PostgreSQL (for persistent storage)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/agentzero.git
cd agentzero
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the system:
```bash
python main.py
```

### Docker Deployment

```bash
docker-compose up -d
```

This will start:
- Hive Coordinator
- Multiple Research Agents
- Multiple Code Agents
- Redis for messaging
- PostgreSQL for storage
- Prometheus & Grafana for monitoring

## Usage

### Interactive Mode

```bash
python main.py --mode interactive
```

Commands:
- `research <query>` - Research a topic
- `code <description>` - Generate code
- `analyze <file>` - Analyze code file
- `status` - Show system status
- `quit` - Exit

### Batch Mode

```bash
python main.py --mode batch --tasks tasks.txt
```

### Python API

```python
from agentzero import AgentZeroSystem
from src.core.agent import Task, Priority

# Initialize system
system = AgentZeroSystem()
await system.initialize()

# Submit a research task
task_id = await system.submit_task(
    "Research latest developments in quantum computing",
    task_type="research"
)

# Submit a code generation task
task_id = await system.submit_task(
    "Generate a REST API for user management",
    task_type="code_generation"
)

# Get system status
status = await system.get_status()
print(f"Active tasks: {status['hive']['active_tasks']}")
```

## Architecture

```
┌─────────────────────────────────────────┐
│           Hive Coordinator              │
│  • Task Distribution                    │
│  • Agent Management                     │
│  • Resource Optimization                │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┬────────┬────────┐
    │                 │        │        │
┌───▼───┐      ┌──────▼──┐ ┌──▼───┐ ┌──▼───┐
│Research│      │  Code   │ │Plan  │ │Exec  │
│ Agent  │      │  Agent  │ │Agent │ │Agent │
└────────┘      └─────────┘ └──────┘ └──────┘
```

### Task Distribution Strategies

1. **Capability-Based**: Match tasks to agents with required skills
2. **Load-Balanced**: Distribute evenly across available agents
3. **Auction-Based**: Agents bid for tasks they can handle
4. **Priority-Based**: Consider agent performance metrics
5. **Round-Robin**: Simple sequential distribution

## Configuration

### Environment Variables

```bash
# Hive Configuration
HIVE_ID=main-hive
DISTRIBUTION_STRATEGY=capability_based

# Agent Configuration
RESEARCH_AGENTS=2
CODE_AGENTS=2

# Database
POSTGRES_URL=postgresql://user:pass@localhost/agentzero
REDIS_URL=redis://localhost:6379

# Monitoring
LOG_LEVEL=INFO
```

### Config File

```yaml
# config/agentzero.yml
hive:
  distribution_strategy: capability_based
  max_tasks_per_agent: 5
  heartbeat_interval: 30

agents:
  research:
    count: 2
    max_depth: 3
    max_pages: 50
  code:
    count: 2
    languages:
      - python
      - javascript
      - typescript
```

## Monitoring

Access Grafana dashboard at http://localhost:3000 (default: admin/admin)

Key metrics:
- Agent utilization
- Task completion rate
- Average task duration
- Hive efficiency score
- Memory usage per agent

## Development

### Project Structure

```
agentzero/
├── src/
│   ├── core/           # Core agent framework
│   ├── hive/           # Hive coordination system
│   ├── agents/         # Specialized agent implementations
│   ├── tools/          # Agent tools and utilities
│   ├── memory/         # Memory and learning systems
│   └── communication/  # Inter-agent communication
├── tests/              # Test suite
├── config/             # Configuration files
├── docker/             # Docker configurations
└── docs/               # Documentation
```

### Creating Custom Agents

```python
from src.core.agent import BaseAgent, Task

class CustomAgent(BaseAgent):
    async def execute(self, task: Task):
        # Implement task execution logic
        result = await self.process_custom_task(task)
        return result
```

### Running Tests

```bash
pytest tests/
pytest tests/ --cov=src --cov-report=html
```

## Roadmap

- [x] Core agent framework
- [x] Hive coordinator
- [x] Research agent
- [x] Code agent
- [ ] Planning agent
- [ ] Execution agent
- [ ] Web UI dashboard
- [ ] REST API
- [ ] Agent marketplace
- [ ] Distributed deployment
- [ ] GPU acceleration for AI tasks

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) first.

## License

MIT License - see [LICENSE](LICENSE) file for details

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/yourusername/agentzero/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/agentzero/discussions)

## Acknowledgments

Built with cutting-edge technologies and inspired by swarm intelligence principles.
