# AgentZero Coding Standards

## Overview

This document defines the coding standards and best practices for the AgentZero project. All contributors must follow these standards to maintain code quality, consistency, and maintainability.

## Python Standards

### Style Guide

We follow [PEP 8](https://pep8.org/) with the following specifications:
- **Line Length**: Maximum 88 characters (Black formatter default)
- **Indentation**: 4 spaces (no tabs)
- **Import Order**: Standard library → Third-party → Local application
- **Quotes**: Prefer double quotes for strings

### Code Formatting

**Required**: Use Black formatter with default settings

```bash
# Format single file
black src/agents/planning_agent.py

# Format entire project
black src/ tests/

# Check without modifying
black --check src/
```

### Naming Conventions

```python
# Classes: PascalCase
class PlanningAgent(BaseAgent):
    pass

# Functions/Methods: snake_case
def calculate_critical_path():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 300

# Private methods: leading underscore
def _internal_method():
    pass

# Protected attributes: single underscore
self._protected_attribute = value

# Module-level private: leading underscore
_private_module_variable = 42
```

### Type Hints

**Required** for all new code:

```python
from typing import List, Dict, Optional, Union, Any
from datetime import datetime

def process_task(
    task: Task,
    timeout: int = 300,
    retry_count: int = 3
) -> TaskResult:
    """Process a task with specified timeout and retry count."""
    pass

async def get_agent_status(
    agent_id: str
) -> Optional[Dict[str, Any]]:
    """Get agent status or None if not found."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_resource_allocation(
    tasks: List[Task],
    agents: List[Agent],
    constraints: Dict[str, Any]
) -> AllocationPlan:
    """
    Calculate optimal resource allocation for tasks.

    Args:
        tasks: List of tasks to be allocated
        agents: Available agents for allocation
        constraints: Allocation constraints including:
            - max_tasks_per_agent: Maximum tasks per agent
            - priority_weight: Weight for priority consideration
            - deadline_weight: Weight for deadline consideration

    Returns:
        AllocationPlan containing agent assignments and timeline

    Raises:
        InsufficientResourcesError: If resources cannot meet requirements
        InvalidConstraintError: If constraints are contradictory

    Example:
        >>> tasks = [Task(name="Task1"), Task(name="Task2")]
        >>> agents = [Agent(id="agent1"), Agent(id="agent2")]
        >>> plan = calculate_resource_allocation(tasks, agents, {})
        >>> print(plan.assignments)
    """
    pass
```

### Async Best Practices

```python
# Always use async/await for I/O operations
async def fetch_data(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# Use asyncio.gather for concurrent operations
results = await asyncio.gather(
    fetch_data(url1),
    fetch_data(url2),
    fetch_data(url3)
)

# Handle async context managers properly
async with asyncio.Lock() as lock:
    # Critical section
    pass

# Use asyncio.create_task for fire-and-forget
task = asyncio.create_task(background_operation())
```

### Error Handling

```python
# Define custom exceptions
class AgentError(Exception):
    """Base exception for agent-related errors."""
    pass

class TaskExecutionError(AgentError):
    """Raised when task execution fails."""
    pass

# Use specific exception handling
try:
    result = await execute_task(task)
except TaskExecutionError as e:
    logger.error(f"Task execution failed: {e}")
    # Handle specific error
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    # Handle general error
finally:
    # Cleanup resources
    await cleanup()

# Use context managers for resource management
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_resource():
    resource = await acquire_resource()
    try:
        yield resource
    finally:
        await release_resource(resource)
```

### Logging

```python
import logging

# Create logger at module level
logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debugging information")
logger.info("General informational messages")
logger.warning("Warning messages for potential issues")
logger.error("Error messages for failures")
logger.exception("Error with full stack trace")

# Include context in log messages
logger.info(
    "Task completed",
    extra={
        "task_id": task.id,
        "duration": duration,
        "agent_id": agent.id
    }
)
```

### Testing Standards

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch

# Test file naming: test_<module_name>.py
# Test class naming: Test<ClassName>
# Test method naming: test_<method_name>_<scenario>

class TestPlanningAgent:
    """Tests for PlanningAgent class."""

    @pytest.fixture
    async def agent(self):
        """Create test agent instance."""
        return PlanningAgent(config={"test": True})

    @pytest.mark.asyncio
    async def test_create_plan_success(self, agent):
        """Test successful plan creation."""
        # Arrange
        project_spec = {"name": "Test Project"}

        # Act
        plan = await agent.create_plan(project_spec)

        # Assert
        assert plan is not None
        assert plan.project_name == "Test Project"

    @pytest.mark.asyncio
    async def test_create_plan_with_invalid_input(self, agent):
        """Test plan creation with invalid input raises error."""
        # Arrange
        invalid_spec = None

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid project specification"):
            await agent.create_plan(invalid_spec)
```

## TypeScript/React Standards

### Style Guide

We follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript) with TypeScript additions:

### File Naming
- **Components**: PascalCase (`AgentCard.tsx`)
- **Utilities**: camelCase (`formatters.ts`)
- **Types/Interfaces**: PascalCase (`AgentTypes.ts`)
- **Hooks**: camelCase with 'use' prefix (`useWebSocket.ts`)

### Component Structure

```typescript
// Use functional components with TypeScript
interface AgentCardProps {
  agent: Agent;
  onAction: (action: AgentAction) => void;
  className?: string;
}

export const AgentCard: React.FC<AgentCardProps> = ({
  agent,
  onAction,
  className
}) => {
  // Hooks at the top
  const [expanded, setExpanded] = useState(false);
  const theme = useTheme();

  // Event handlers
  const handleClick = useCallback(() => {
    setExpanded(!expanded);
  }, [expanded]);

  // Render
  return (
    <div className={clsx('agent-card', className)}>
      {/* Component JSX */}
    </div>
  );
};

// Default props if needed
AgentCard.defaultProps = {
  className: ''
};
```

### TypeScript Best Practices

```typescript
// Use interfaces for object shapes
interface User {
  id: string;
  name: string;
  email: string;
}

// Use type for unions and intersections
type Status = 'idle' | 'loading' | 'error';
type ExtendedUser = User & { role: string };

// Use enums for constants
enum AgentStatus {
  IDLE = 'idle',
  WORKING = 'working',
  ERROR = 'error'
}

// Use generics for reusable components
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

// Avoid 'any' - use 'unknown' if type is truly unknown
function processData(data: unknown): void {
  if (typeof data === 'string') {
    // Handle string
  }
}
```

### State Management

```typescript
// Use Redux Toolkit
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AgentsState {
  agents: Agent[];
  loading: boolean;
  error: string | null;
}

const agentsSlice = createSlice({
  name: 'agents',
  initialState: {
    agents: [],
    loading: false,
    error: null
  } as AgentsState,
  reducers: {
    setAgents: (state, action: PayloadAction<Agent[]>) => {
      state.agents = action.payload;
    },
    updateAgent: (state, action: PayloadAction<Agent>) => {
      const index = state.agents.findIndex(a => a.id === action.payload.id);
      if (index !== -1) {
        state.agents[index] = action.payload;
      }
    }
  }
});
```

## Git Commit Standards

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, semicolons, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions or corrections
- `build`: Build system changes
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

### Examples

```bash
feat(planning): add task decomposition algorithm

Implement recursive task decomposition with support for up to 5 levels
of hierarchy. Includes cycle detection and dependency resolution.

Closes #123

---

fix(execution): prevent command injection vulnerability

Add input sanitization and whitelist validation for all commands
executed by the Execution Agent.

Security: CVE-2024-1234

---

docs(api): update WebSocket protocol documentation

Add examples for event subscription and error handling.
```

## Security Standards

### Input Validation

```python
from pydantic import BaseModel, validator
import re

class TaskCreateRequest(BaseModel):
    name: str
    description: str
    priority: str

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v) > 255:
            raise ValueError('Name must be 1-255 characters')
        if not re.match(r'^[\w\s\-\.]+$', v):
            raise ValueError('Name contains invalid characters')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of {valid_priorities}')
        return v
```

### Secret Management

```python
# Never hardcode secrets
# BAD
API_KEY = "sk-1234567890abcdef"

# GOOD
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY environment variable not set")
```

### SQL Injection Prevention

```python
# Use parameterized queries
# BAD
query = f"SELECT * FROM users WHERE id = {user_id}"

# GOOD
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))

# With SQLAlchemy
from sqlalchemy import text

# BAD
result = conn.execute(f"SELECT * FROM users WHERE id = {user_id}")

# GOOD
result = conn.execute(
    text("SELECT * FROM users WHERE id = :user_id"),
    {"user_id": user_id}
)
```

## Performance Standards

### Optimization Guidelines

```python
# Use generators for large datasets
def process_large_file(filepath: str):
    with open(filepath) as f:
        for line in f:  # Generator, doesn't load entire file
            yield process_line(line)

# Cache expensive computations
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(param: str) -> int:
    # Complex calculation
    return result

# Use connection pooling
from asyncpg import create_pool

async def setup_database():
    return await create_pool(
        DATABASE_URL,
        min_size=10,
        max_size=20,
        command_timeout=60
    )

# Batch operations
async def batch_insert(items: List[Dict]):
    # Instead of individual inserts
    async with pool.acquire() as conn:
        await conn.executemany(
            "INSERT INTO items (name, value) VALUES ($1, $2)",
            [(item['name'], item['value']) for item in items]
        )
```

## Code Review Checklist

### Before Submitting PR
- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] No console.log/print statements
- [ ] Type hints added (Python)
- [ ] TypeScript types defined
- [ ] Error handling implemented
- [ ] Logging added appropriately

### Review Focus Areas
1. **Security**: Input validation, SQL injection, XSS
2. **Performance**: N+1 queries, memory leaks, inefficient algorithms
3. **Maintainability**: Code clarity, documentation, test coverage
4. **Architecture**: Design patterns, SOLID principles, DRY
5. **Error Handling**: Graceful degradation, user feedback

## Tools Configuration

### .flake8
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,venv,build,dist
```

### .eslintrc.js
```javascript
module.exports = {
  extends: [
    'react-app',
    'airbnb',
    'airbnb-typescript',
    'prettier'
  ],
  parserOptions: {
    project: './tsconfig.json'
  },
  rules: {
    'react/react-in-jsx-scope': 'off',
    'import/prefer-default-export': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off'
  }
};
```

### .prettierrc
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
```

## Enforcement

These standards are enforced through:
1. **Pre-commit hooks**: Automatic formatting and linting
2. **CI/CD pipeline**: Automated checks on all PRs
3. **Code reviews**: Manual verification by team members
4. **Documentation**: This guide as the source of truth

Non-compliance will result in:
- PR rejection until standards are met
- Automated issues created for violations
- Team discussion for repeated violations

---
**Last Updated**: 2025-09-21
**Version**: 1.0
**Owner**: AgentZero Development Team