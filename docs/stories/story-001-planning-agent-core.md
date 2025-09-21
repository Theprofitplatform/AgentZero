# Story 001: Planning Agent Core Implementation

## Story Overview
**Epic**: Planning Agent Implementation
**Story ID**: STORY-001
**Priority**: P0 (Critical)
**Estimated Effort**: 8 story points
**Status**: Ready for Development

## User Story
**As a** system user
**I want to** have a fully functional Planning Agent
**So that** the system can create strategic plans, decompose tasks, and allocate resources optimally

## Acceptance Criteria

### AC1: Strategic Planning Implementation
- [ ] Implement `create_strategic_plan()` method that accepts project specifications
- [ ] Generate multi-phase project plans with timelines (up to 90 days)
- [ ] Support hierarchical structure (project → phase → milestone → task)
- [ ] Calculate critical path using CPM algorithm
- [ ] Export plans in JSON and Markdown formats
- [ ] Include risk assessment in plans

### AC2: Task Decomposition
- [ ] Implement `decompose_task()` method for breaking down complex tasks
- [ ] Support recursive decomposition up to 5 levels deep
- [ ] Auto-identify task dependencies
- [ ] Estimate task duration based on complexity
- [ ] Generate task dependency graph
- [ ] Handle circular dependency detection

### AC3: Resource Allocation
- [ ] Implement `allocate_resources()` method for optimal resource distribution
- [ ] Calculate agent capacity based on current workload
- [ ] Implement bin packing algorithm for resource optimization
- [ ] Support priority-based allocation
- [ ] Handle resource conflicts gracefully
- [ ] Provide allocation recommendations to HiveCoordinator

### AC4: Hive Integration
- [ ] Register planning capabilities with HiveCoordinator
- [ ] Handle task assignments from Hive
- [ ] Report status updates in real-time
- [ ] Support task cancellation
- [ ] Implement heartbeat mechanism
- [ ] Handle graceful shutdown

### AC5: Error Handling & Logging
- [ ] Comprehensive error handling for all methods
- [ ] Structured logging with appropriate log levels
- [ ] Input validation for all public methods
- [ ] Graceful degradation on partial failures
- [ ] Retry logic for recoverable errors

## Technical Implementation Details

### File: `src/agents/planning_agent.py`

Key methods to complete:
```python
async def _create_strategic_plan(self, params: Dict[str, Any]) -> Dict:
    """
    Generate comprehensive strategic plan
    Input: project specifications
    Output: structured plan with phases, milestones, timeline
    """

async def _decompose_task(self, params: Dict[str, Any]) -> List[Dict]:
    """
    Break down complex task into subtasks
    Input: task description and constraints
    Output: hierarchical task structure with dependencies
    """

async def _allocate_resources(self, params: Dict[str, Any]) -> Dict:
    """
    Optimize resource allocation across tasks
    Input: tasks list, available resources, constraints
    Output: allocation plan with assignments
    """

async def _calculate_critical_path(self, tasks: List[Task]) -> List[str]:
    """
    Calculate critical path using CPM
    Input: tasks with dependencies and durations
    Output: list of task IDs on critical path
    """
```

### Dependencies
- `networkx` for graph operations (add to requirements.txt)
- `python-dateutil` for date calculations (already present)
- Existing `BaseAgent` class from `src/core/agent.py`
- `HiveCoordinator` for registration

### Data Structures
```python
@dataclass
class Plan:
    plan_id: str
    project_name: str
    phases: List[Phase]
    milestones: List[Milestone]
    critical_path: List[str]
    timeline: Timeline
    resource_allocation: Dict[str, List[str]]
    risk_assessment: List[Risk]

@dataclass
class Phase:
    phase_id: str
    name: str
    start_date: datetime
    end_date: datetime
    milestones: List[str]
    tasks: List[str]

@dataclass
class Milestone:
    milestone_id: str
    name: str
    target_date: datetime
    deliverables: List[str]
    success_criteria: List[str]
```

## Testing Requirements

### Unit Tests
- Test strategic plan generation with various project sizes
- Test task decomposition with different complexity levels
- Test resource allocation algorithms
- Test critical path calculation
- Test error handling scenarios

### Integration Tests
- Test registration with HiveCoordinator
- Test task assignment and completion flow
- Test inter-agent communication
- Test plan updates based on execution feedback

### Test File: `tests/test_planning_agent.py`
```python
import pytest
from src.agents.planning_agent import PlanningAgent

@pytest.mark.asyncio
async def test_strategic_plan_creation():
    agent = PlanningAgent()
    project_spec = {...}
    plan = await agent.create_strategic_plan(project_spec)
    assert plan.phases
    assert plan.critical_path
    assert plan.timeline

@pytest.mark.asyncio
async def test_task_decomposition():
    agent = PlanningAgent()
    complex_task = {...}
    subtasks = await agent.decompose_task(complex_task)
    assert len(subtasks) > 1
    assert all(task.parent_id for task in subtasks)

@pytest.mark.asyncio
async def test_resource_allocation():
    agent = PlanningAgent()
    tasks = [...]
    allocation = await agent.allocate_resources(tasks)
    assert allocation.assignments
    assert allocation.utilization < 1.0
```

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] No critical bugs
- [ ] Performance benchmarks met (<100ms response time)
- [ ] Logging implemented
- [ ] Error handling complete

## Implementation Notes

### Priority Order
1. Implement core planning logic (strategic planning)
2. Add task decomposition
3. Implement resource allocation
4. Integrate with HiveCoordinator
5. Add error handling and logging
6. Write comprehensive tests

### Potential Challenges
- Complex dependency graph management
- Optimal resource allocation is NP-hard
- Real-time plan adjustments
- Handling large projects (1000+ tasks)

### Performance Considerations
- Use caching for repeated calculations
- Implement lazy loading for large plans
- Consider using worker threads for CPU-intensive operations
- Optimize graph algorithms for large task networks

## Related Documents
- PRD: `/docs/prd.md#FR-1`
- Architecture: `/docs/architecture.md#2.1`
- Epic: Planning Agent Implementation

## Post-Implementation Tasks
- Performance optimization if needed
- Add advanced planning algorithms (genetic algorithms, ML-based)
- Implement plan versioning
- Add plan comparison features

---
**Created**: 2025-09-21
**Last Updated**: 2025-09-21
**Author**: BMad Workflow System