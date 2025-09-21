# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgentZero is a Python-based multi-agent system that uses hive intelligence for collaborative problem-solving. The system features specialized agents (research, code, planning, execution) coordinated through a central hive system.

## Core Commands

### Development Setup
```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the System
```bash
# Interactive mode (default)
python main.py --mode interactive

# Batch mode with tasks file
python main.py --mode batch --tasks tasks.txt

# Server mode (API)
python main.py --mode server --port 8000

# Custom agent configuration
python main.py --research-agents 3 --code-agents 2
```

### Testing
```bash
# Run basic tests
python test_simple.py

# Run parallel agent tests
python test_parallel_5_agents.py

# Run comprehensive test suite
pytest tests/
```

### Docker Operations
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f hive-coordinator
docker-compose logs -f research-agent

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Architecture Overview

### Core Components
- **src/core/agent.py**: BaseAgent class with task processing, memory, and communication
- **src/hive/coordinator.py**: HiveCoordinator for task distribution and agent management
- **src/agents/**: Specialized agent implementations
  - `research_agent.py`: Web scraping and data gathering
  - `code_agent.py`: Code generation and analysis
  - `planning_agent.py`: Strategic task decomposition
  - `execution_agent.py`: Task execution monitoring

### System Flow
1. Tasks submitted to HiveCoordinator via main.py
2. Hive uses distribution strategies (capability_based, load_balanced, etc.) to assign tasks
3. Agents process tasks using their specialized capabilities
4. Results collected and learning occurs through episodic memory

### Key Design Patterns
- **Agent-based Architecture**: Each agent inherits from BaseAgent with execute() method
- **Hive Intelligence**: Central coordinator manages task distribution and agent communication
- **Memory Systems**: Agents maintain short-term, long-term, episodic, and semantic memory
- **Capability Registration**: Agents register capabilities that determine task assignment
- **Async Processing**: All operations use asyncio for concurrent execution

## Agent Types and Capabilities

### Research Agent
- Capabilities: `["web_search", "extract_content", "analyze_data"]`
- Configuration: `max_depth`, `max_pages`
- Tools: Web scraping, content extraction, sentiment analysis

### Code Agent
- Capabilities: `["generate_code", "analyze_code", "debug_code"]`
- Configuration: `languages` (python, javascript, typescript)
- Tools: Code generation, analysis, optimization, test generation

### Planning Agent
- Capabilities: Task decomposition, resource allocation, timeline management
- Status: Coming Soon

### Execution Agent
- Capabilities: Task execution monitoring, system operations
- Status: Coming Soon

## Configuration

### Environment Variables
```bash
HIVE_ID=main-hive
DISTRIBUTION_STRATEGY=capability_based
LOG_LEVEL=INFO
RESEARCH_AGENTS=2
CODE_AGENTS=2
```

### Task Distribution Strategies
- `capability_based`: Match tasks to agent capabilities
- `load_balanced`: Distribute evenly across agents
- `auction_based`: Agents bid for tasks
- `priority_based`: Consider performance metrics
- `round_robin`: Sequential distribution

## Development Guidelines

### Creating Custom Agents
```python
from src.core.agent import BaseAgent, Task

class CustomAgent(BaseAgent):
    async def execute(self, task: Task):
        # Implement specialized task logic
        result = await self.process_custom_task(task)
        return result

    def _register_default_capabilities(self):
        super()._register_default_capabilities()
        # Register custom capabilities
```

### Task Submission
```python
from main import AgentZeroSystem

system = AgentZeroSystem()
await system.initialize()

# Research task
task_id = await system.submit_task(
    "Research quantum computing developments",
    task_type="research"
)

# Code generation task
task_id = await system.submit_task(
    "Generate REST API for user management",
    task_type="code_generation"
)
```

### File Organization
- `main.py`: System entry point and orchestration
- `src/core/`: Base agent framework and shared utilities
- `src/hive/`: Hive coordination and task distribution
- `src/agents/`: Specialized agent implementations
- `examples/`: Usage examples and demos
- `tests/`: Test files (test_*.py pattern)

## Common Development Tasks

### Adding New Agent Type
1. Create new file in `src/agents/`
2. Inherit from `BaseAgent`
3. Implement `execute()` method
4. Register capabilities in `_register_default_capabilities()`
5. Update `main.py` to instantiate and register with hive

### Modifying Task Distribution
1. Edit `src/hive/coordinator.py`
2. Add new strategy to `TaskDistributionStrategy` enum
3. Implement strategy logic in `_distribute_task()` method

### Monitoring and Debugging
- Check agent status: Call `system.get_status()` or interactive `status` command
- View logs: Agents log to console with structured format
- Memory inspection: Access `agent.memory` for debugging learning
- Task history: Check `agent.completed_tasks` for execution history