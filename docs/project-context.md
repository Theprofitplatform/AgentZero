# AgentZero Project Context Documentation

## Executive Summary

AgentZero is a sophisticated Python-based multi-agent system leveraging hive intelligence for collaborative problem-solving. The system features specialized agents coordinated through a central hive system, enabling complex task execution through distributed intelligence.

## Current System Architecture

### Technology Stack

- **Core Language**: Python 3.9+
- **Async Framework**: asyncio for concurrent operations
- **Web Framework**: FastAPI (server mode)
- **HTTP Client**: aiohttp for async HTTP operations
- **Data Processing**: pandas, numpy
- **Database**: Redis for message queue (Docker deployment)
- **Testing**: pytest with async support
- **Containerization**: Docker & Docker Compose

### System Components

#### 1. Core Framework (`src/core/agent.py`)
- **BaseAgent Class**: Abstract base for all agents
- **Memory Systems**: Short-term, long-term, episodic, semantic
- **Task Processing**: Priority-based queue with dependency management
- **Communication**: Message passing between agents
- **Capabilities**: Dynamic capability registration system
- **Metrics**: Performance tracking and success rate calculation

#### 2. Hive Coordinator (`src/hive/coordinator.py`)
- **Task Distribution**: Multiple strategies (capability-based, load-balanced, etc.)
- **Agent Registry**: Tracks agent status and capabilities
- **Message Routing**: Handles inter-agent communication
- **Heartbeat Monitoring**: Ensures agent health
- **State Persistence**: Optional state saving to disk

#### 3. Specialized Agents

##### Research Agent (`src/agents/research_agent.py`) - COMPLETE
- Web searching and data gathering
- Content extraction with BeautifulSoup
- Sentiment analysis capabilities
- Knowledge graph construction
- Configurable depth and page limits

##### Code Agent (`src/agents/code_agent.py`) - COMPLETE
- Multi-language code generation (Python, JavaScript, TypeScript)
- Code analysis and optimization
- Debugging assistance
- Test generation
- Code refactoring suggestions

##### Planning Agent (`src/agents/planning_agent.py`) - PARTIAL
- Strategic planning methods (stub)
- Task decomposition algorithms (stub)
- Resource allocation systems (stub)
- Timeline management (basic structure)
- Dependency resolution (not implemented)

##### Execution Agent (`src/agents/execution_agent.py`) - PARTIAL
- Task execution monitoring (basic structure)
- System operations (stub)
- Deployment automation (directory structure only)
- Integration management (not implemented)

### Current Capabilities

#### Operational Features
- ✅ Interactive mode with command-line interface
- ✅ Batch processing from task files
- ✅ Basic server mode with API
- ✅ Docker deployment configuration
- ✅ Agent registration and heartbeat
- ✅ Task submission and routing
- ✅ Memory persistence
- ✅ Metrics tracking

#### Partial/Missing Features
- ⚠️ Planning Agent (structure only, no implementation)
- ⚠️ Execution Agent (structure only, no implementation)
- ❌ Web Dashboard
- ❌ Comprehensive REST API
- ❌ WebSocket support for real-time updates
- ❌ Agent marketplace
- ❌ GPU acceleration
- ❌ Distributed deployment

### Code Quality Assessment

#### Strengths
- Clean async/await patterns throughout
- Proper error handling with try/except blocks
- Comprehensive logging infrastructure
- Good separation of concerns
- Minimal technical debt (only 4 TODO comments)
- Well-documented with docstrings

#### Areas for Enhancement
- Planning Agent implementation incomplete
- Execution Agent implementation incomplete
- No web UI components
- Limited API endpoints
- Missing integration tests

### Integration Points

#### Internal Integration
- Agents register with HiveCoordinator via AgentInfo objects
- Task distribution based on agent capabilities
- Memory systems allow learning from experience
- Message passing for inter-agent communication

#### External Integration
- FastAPI server for HTTP API
- Redis for distributed message queue (Docker)
- PostgreSQL support mentioned but not implemented
- Prometheus/Grafana monitoring (Docker config exists)

### Constraints & Considerations

#### Technical Constraints
- Python 3.9+ required
- Async operations throughout (no blocking calls)
- Memory management for long-running agents
- Task queue size limitations

#### Architectural Constraints
- All agents must inherit from BaseAgent
- Capability-based task routing
- Hive coordinator as central point (potential bottleneck)
- State persistence optional but recommended

### Development Patterns

#### Agent Creation Pattern
```python
class CustomAgent(BaseAgent):
    def __init__(self, ...):
        super().__init__(...)
        self._register_custom_capabilities()

    async def execute(self, task: Task):
        # Implementation required
        pass
```

#### Task Submission Pattern
```python
task = Task(name="...", description="...", priority=Priority.MEDIUM)
task_id = await system.submit_task(description, task_type)
```

#### Capability Registration Pattern
```python
self.register_capability(AgentCapability(
    name="capability_name",
    description="What it does",
    handler=self._handler_method
))
```

### Testing Infrastructure

- Unit tests: `test_simple.py`, `test_parallel_5_agents.py`
- Test patterns focus on multi-agent coordination
- Async test support with pytest-asyncio
- No comprehensive test coverage yet

### Documentation Status

- ✅ README.md - Complete overview
- ✅ USAGE_GUIDE.md - Detailed usage instructions
- ✅ CLAUDE.md - Development guidance for Claude Code
- ✅ Docstrings in all major classes
- ❌ API documentation
- ❌ Architecture diagrams (text-based only)

### Security Considerations

- No authentication/authorization implemented
- API endpoints unprotected
- Potential for resource exhaustion
- No rate limiting
- Workspace isolation not enforced

### Performance Characteristics

- Async operations enable high concurrency
- Agent pooling for resource efficiency
- Memory usage grows with task history
- No performance benchmarks available
- Scalability limited by single coordinator

## Recommendations for Enhancement

### Priority 1: Complete Core Agents
- Implement Planning Agent methods
- Implement Execution Agent methods
- Add comprehensive testing

### Priority 2: Web Dashboard
- React or Vue.js frontend
- Real-time WebSocket updates
- Agent monitoring interface
- Task management UI

### Priority 3: API Enhancement
- Complete REST API endpoints
- Add authentication layer
- Implement rate limiting
- Create OpenAPI documentation

### Priority 4: Production Readiness
- Add security measures
- Implement monitoring
- Create deployment scripts
- Add performance optimizations

## File Structure Summary

```
AgentZero/
├── src/
│   ├── core/
│   │   └── agent.py (330 lines, complete)
│   ├── hive/
│   │   └── coordinator.py (730 lines, complete)
│   └── agents/
│       ├── research_agent.py (695 lines, complete)
│       ├── code_agent.py (886 lines, complete)
│       ├── planning_agent.py (608 lines, partial)
│       └── execution_agent.py (515 lines, partial)
├── main.py (323 lines, entry point)
├── test_*.py (test files)
├── docker-compose.yml (services configuration)
├── requirements.txt (dependencies)
└── docs/ (documentation)
```

## Next Steps

This project is well-positioned for enhancement using the BMad brownfield workflow. The core architecture is solid, and the missing components (Planning Agent, Execution Agent, Web UI, API) are clearly defined and can be implemented systematically using BMad's agent-driven development approach.