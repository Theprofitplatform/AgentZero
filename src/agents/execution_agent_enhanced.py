"""
Enhanced Execution Agent for AgentZero
Implements secure command execution, sandboxing, and advanced deployment capabilities
"""

import asyncio
import subprocess
import json
import os
import re
import signal
import shutil
import tempfile
import psutil
import aiofiles
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import hashlib
import uuid

import sys
sys.path.append('/mnt/c/Users/abhis/projects/AgentZero')
from src.core.agent import BaseAgent, Task, AgentCapability, Priority


# Data structures for execution
@dataclass
class ResourceLimits:
    """Resource usage limits for command execution"""
    cpu_percent: float = 50.0  # Max CPU usage percentage
    memory_mb: int = 512  # Max memory in MB
    disk_io_mb: int = 100  # Max disk I/O per second in MB
    network_mb: int = 10  # Max network bandwidth in MB/s
    max_processes: int = 10  # Max number of child processes
    max_file_size_mb: int = 100  # Max file size that can be created


@dataclass
class ExecutionResult:
    """Result of command execution"""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    resource_usage: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    sandbox_path: Optional[str] = None


@dataclass
class DeploymentState:
    """Deployment state tracking"""
    deployment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_name: str = ""
    version: str = ""
    environment: str = ""
    status: str = "pending"
    deployed_at: Optional[datetime] = None
    health_status: str = "unknown"
    rollback_version: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionState:
    """Execution state for monitoring"""
    task_id: str
    start_time: datetime
    status: str
    metrics: Dict[str, Any]
    end_time: Optional[datetime] = None
    duration: Optional[float] = None


class ExecutionError(Exception):
    """Base exception for execution errors"""
    pass


class SecurityError(ExecutionError):
    """Raised for security violations"""
    pass


class TimeoutError(ExecutionError):
    """Raised when execution times out"""
    pass


class ResourceError(ExecutionError):
    """Raised when resource limits exceeded"""
    pass


class DeploymentError(ExecutionError):
    """Raised for deployment failures"""
    pass


class CommandValidator:
    """Validates commands against security rules"""

    # Command whitelist patterns
    WHITELIST_PATTERNS = [
        r'^ls\s+[\w\-\.\/\s]+$',           # List directory
        r'^cat\s+[\w\-\.\/]+$',            # Read file
        r'^echo\s+.*$',                    # Echo text
        r'^pwd$',                           # Print working directory
        r'^whoami$',                        # Current user
        r'^date$',                          # Current date
        r'^python3?\s+[\w\-\.\/]+\.py',    # Run Python scripts
        r'^node\s+[\w\-\.\/]+\.js',        # Run Node.js scripts
        r'^npm\s+(install|test|build|run)', # NPM commands
        r'^pip\s+install\s+[\w\-\=\<\>]+', # Pip install
        r'^docker\s+(ps|logs|stats|images)', # Docker read-only
        r'^git\s+(status|log|diff|branch)', # Git read-only
        r'^grep\s+.*',                      # Search in files
        r'^find\s+[\w\-\.\/]+',            # Find files
        r'^wget\s+https?://.*',            # Download files
        r'^curl\s+https?://.*',            # HTTP requests
        r'^tar\s+[\w\-]+\s+[\w\-\.\/]+',  # Archive operations
        r'^unzip\s+[\w\-\.\/]+',          # Unzip files
        r'^cp\s+[\w\-\.\/\s]+',           # Copy files
        r'^mv\s+[\w\-\.\/\s]+',           # Move files
        r'^mkdir\s+[\w\-\.\/]+',          # Create directory
        r'^touch\s+[\w\-\.\/]+',          # Create file
        r'^chmod\s+[0-7]{3}\s+[\w\-\.\/]+', # Change permissions
        r'^ps\s+.*',                       # Process status
        r'^df\s+.*',                       # Disk free
        r'^du\s+.*',                       # Disk usage
        r'^free$',                         # Memory usage
        r'^top\s+.*',                      # Process monitor
        r'^htop$',                         # Better process monitor
        r'^systemctl\s+(status|show)',     # Systemd status
        r'^journalctl\s+.*',               # System logs
        r'^env$',                          # Environment variables
        r'^which\s+[\w\-]+',               # Find command path
    ]

    # Dangerous patterns to block
    BLACKLIST_PATTERNS = [
        r'rm\s+-rf\s+\/',                  # Recursive root deletion
        r':(){ :|:& };:',                  # Fork bomb
        r'>\s*\/dev\/sda',                 # Overwrite disk
        r'dd\s+.*of=\/dev\/',              # Direct disk write
        r'mkfs\.',                         # Format filesystem
        r'shutdown',                       # System shutdown
        r'reboot',                         # System reboot
        r'passwd',                         # Change password
        r'useradd',                        # Add user
        r'userdel',                        # Delete user
        r'visudo',                         # Edit sudoers
        r'crontab\s+-e',                   # Edit crontab
        r'nc\s+-l',                        # Netcat listener
        r'\/etc\/passwd',                  # Access passwd file
        r'\/etc\/shadow',                  # Access shadow file
        r'\.ssh\/.*key',                   # Access SSH keys
        r'sudo\s+',                        # Sudo commands
        r'su\s+',                          # Switch user
        r'eval\s+',                        # Eval command
        r'exec\s+',                        # Exec command
    ]

    @classmethod
    def validate(cls, command: str) -> Tuple[bool, Optional[str]]:
        """Validate command against security rules"""
        command = command.strip()

        # Check blacklist first
        for pattern in cls.BLACKLIST_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Command matches dangerous pattern: {pattern}"

        # Check whitelist
        for pattern in cls.WHITELIST_PATTERNS:
            if re.match(pattern, command, re.IGNORECASE):
                return True, None

        return False, "Command not in whitelist"


class SandboxEnvironment:
    """Isolated execution environment"""

    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path("/tmp/sandbox")
        self.sandbox_id = str(uuid.uuid4())
        self.sandbox_path: Optional[Path] = None
        self.process_group: Optional[int] = None

    async def setup(self) -> Path:
        """Create isolated environment"""
        # Create sandbox directory
        self.sandbox_path = self.base_path / self.sandbox_id
        self.sandbox_path.mkdir(parents=True, exist_ok=True)

        # Set restrictive permissions
        self.sandbox_path.chmod(0o700)

        # Create necessary subdirectories
        (self.sandbox_path / "tmp").mkdir(exist_ok=True)
        (self.sandbox_path / "work").mkdir(exist_ok=True)
        (self.sandbox_path / "logs").mkdir(exist_ok=True)

        # Copy minimal required files (if needed)
        # This could include specific scripts or data files

        return self.sandbox_path

    async def cleanup(self):
        """Clean up sandbox resources"""
        if self.sandbox_path and self.sandbox_path.exists():
            shutil.rmtree(self.sandbox_path, ignore_errors=True)

        # Kill any remaining processes in the process group
        if self.process_group:
            try:
                os.killpg(self.process_group, signal.SIGKILL)
            except ProcessLookupError:
                pass


class ResourceLimiter:
    """Applies resource limits to processes"""

    @staticmethod
    def apply_limits(process: subprocess.Popen, limits: ResourceLimits):
        """Apply resource limits to a process"""
        try:
            p = psutil.Process(process.pid)

            # Set CPU affinity (limit to specific cores)
            cpu_count = psutil.cpu_count()
            if cpu_count > 1:
                # Limit to half the available cores
                cores = list(range(cpu_count // 2))
                p.cpu_affinity(cores)

            # Set nice value (lower priority)
            p.nice(10)

            # Memory limit would require cgroups on Linux
            # This is a simplified version

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


class CommandRunner:
    """Secure command execution with sandboxing"""

    def __init__(self, validator: CommandValidator = None,
                 resource_limits: ResourceLimits = None):
        self.validator = validator or CommandValidator()
        self.resource_limits = resource_limits or ResourceLimits()
        self.sandbox = None

    async def execute(self, command: str, timeout: int = 300,
                     use_sandbox: bool = True) -> ExecutionResult:
        """Execute command with security controls"""

        # Validate command
        is_valid, error = self.validator.validate(command)
        if not is_valid:
            raise SecurityError(f"Command validation failed: {error}")

        # Set up sandbox if requested
        sandbox_path = None
        if use_sandbox:
            self.sandbox = SandboxEnvironment()
            sandbox_path = await self.sandbox.setup()

        # Prepare execution environment
        env = os.environ.copy()
        if sandbox_path:
            env['HOME'] = str(sandbox_path)
            env['TMPDIR'] = str(sandbox_path / "tmp")
            env['PATH'] = '/usr/local/bin:/usr/bin:/bin'  # Restricted PATH

        # Record start time
        start_time = datetime.now()

        try:
            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=sandbox_path if sandbox_path else None,
                env=env,
                preexec_fn=os.setsid if os.name == 'posix' else None
            )

            # Apply resource limits
            if os.name == 'posix':
                ResourceLimiter.apply_limits(process, self.resource_limits)

            # Monitor resource usage
            resource_monitor = self._monitor_resources(process.pid)

            # Execute with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                # Kill process group on timeout
                if os.name == 'posix':
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                else:
                    process.kill()
                await process.wait()
                raise TimeoutError(f"Command timed out after {timeout} seconds")

            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()

            # Get resource usage
            resource_usage = await resource_monitor

            return ExecutionResult(
                command=command,
                exit_code=process.returncode,
                stdout=stdout.decode('utf-8', errors='replace') if stdout else "",
                stderr=stderr.decode('utf-8', errors='replace') if stderr else "",
                duration=duration,
                resource_usage=resource_usage,
                success=process.returncode == 0,
                sandbox_path=str(sandbox_path) if sandbox_path else None
            )

        finally:
            # Clean up sandbox
            if self.sandbox:
                await self.sandbox.cleanup()

    async def _monitor_resources(self, pid: int) -> Dict[str, Any]:
        """Monitor resource usage of a process"""
        metrics = {
            'cpu_percent': 0,
            'memory_mb': 0,
            'disk_read_mb': 0,
            'disk_write_mb': 0,
            'num_threads': 0
        }

        try:
            process = psutil.Process(pid)

            # Sample metrics multiple times
            samples = []
            for _ in range(3):
                if not process.is_running():
                    break

                with process.oneshot():
                    samples.append({
                        'cpu_percent': process.cpu_percent(),
                        'memory_mb': process.memory_info().rss / 1024 / 1024,
                        'num_threads': process.num_threads()
                    })
                await asyncio.sleep(0.1)

            # Average the samples
            if samples:
                for key in ['cpu_percent', 'memory_mb', 'num_threads']:
                    metrics[key] = sum(s[key] for s in samples) / len(samples)

            # Get I/O counters
            io_counters = process.io_counters()
            metrics['disk_read_mb'] = io_counters.read_bytes / 1024 / 1024
            metrics['disk_write_mb'] = io_counters.write_bytes / 1024 / 1024

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        return metrics


class SystemOperations:
    """System-level operations handler"""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.workspace.mkdir(exist_ok=True)

    async def file_operation(self, operation: str, path: str,
                            data: Any = None) -> Dict[str, Any]:
        """Perform file system operations with validation"""

        # Validate path is within workspace
        target_path = Path(path)
        if not target_path.is_absolute():
            target_path = self.workspace / target_path

        if not str(target_path).startswith(str(self.workspace)):
            raise SecurityError(f"Path {path} is outside workspace")

        result = {"operation": operation, "path": str(target_path)}

        if operation == "read":
            if not target_path.exists():
                raise FileNotFoundError(f"File not found: {path}")

            async with aiofiles.open(target_path, 'r') as f:
                content = await f.read()
            result["content"] = content
            result["size"] = len(content)

        elif operation == "write":
            target_path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(target_path, 'w') as f:
                await f.write(str(data))
            result["bytes_written"] = len(str(data))

        elif operation == "delete":
            if target_path.exists():
                if target_path.is_file():
                    target_path.unlink()
                else:
                    shutil.rmtree(target_path)
            result["deleted"] = True

        elif operation == "list":
            if target_path.is_dir():
                files = list(target_path.glob("*"))
                result["files"] = [str(f.relative_to(self.workspace)) for f in files]
                result["count"] = len(files)
            else:
                raise NotADirectoryError(f"Not a directory: {path}")

        elif operation == "copy":
            dest_path = Path(data)
            if not dest_path.is_absolute():
                dest_path = self.workspace / dest_path

            if target_path.is_file():
                shutil.copy2(target_path, dest_path)
            else:
                shutil.copytree(target_path, dest_path)
            result["destination"] = str(dest_path)

        elif operation == "move":
            dest_path = Path(data)
            if not dest_path.is_absolute():
                dest_path = self.workspace / dest_path

            shutil.move(str(target_path), str(dest_path))
            result["destination"] = str(dest_path)

        else:
            raise ValueError(f"Unknown operation: {operation}")

        result["success"] = True
        return result

    async def process_operation(self, operation: str,
                               process_id: Optional[int] = None) -> Dict[str, Any]:
        """Manage system processes"""

        result = {"operation": operation}

        if operation == "list":
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            result["processes"] = processes[:20]  # Limit to 20 processes

        elif operation == "info" and process_id:
            try:
                proc = psutil.Process(process_id)
                result["info"] = {
                    "pid": proc.pid,
                    "name": proc.name(),
                    "status": proc.status(),
                    "cpu_percent": proc.cpu_percent(),
                    "memory_mb": proc.memory_info().rss / 1024 / 1024,
                    "num_threads": proc.num_threads(),
                    "create_time": datetime.fromtimestamp(proc.create_time()).isoformat()
                }
            except psutil.NoSuchProcess:
                raise ProcessLookupError(f"Process {process_id} not found")

        elif operation == "kill" and process_id:
            try:
                proc = psutil.Process(process_id)
                proc.terminate()
                proc.wait(timeout=5)
                result["terminated"] = True
            except psutil.NoSuchProcess:
                raise ProcessLookupError(f"Process {process_id} not found")
            except psutil.TimeoutExpired:
                proc.kill()
                result["killed"] = True

        else:
            raise ValueError(f"Invalid operation: {operation}")

        result["success"] = True
        return result

    async def network_operation(self, operation: str,
                               params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute network operations"""

        result = {"operation": operation}

        if operation == "http_request":
            import aiohttp

            method = params.get("method", "GET")
            url = params.get("url")
            headers = params.get("headers", {})
            data = params.get("data")

            async with aiohttp.ClientSession() as session:
                async with session.request(method, url,
                                          headers=headers,
                                          json=data) as response:
                    result["status_code"] = response.status
                    result["headers"] = dict(response.headers)
                    result["body"] = await response.text()

        elif operation == "ping":
            host = params.get("host")
            # Simplified ping using system command
            cmd = f"ping -c 4 {host}"
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            result["output"] = stdout.decode()
            result["success"] = process.returncode == 0

        else:
            raise ValueError(f"Unknown network operation: {operation}")

        return result


class DeploymentManager:
    """Automated deployment orchestration"""

    def __init__(self, deployment_path: Path):
        self.deployment_path = deployment_path
        self.deployment_path.mkdir(exist_ok=True)
        self.deployments: Dict[str, DeploymentState] = {}

    async def deploy(self, artifact: str, target: str,
                    config: Dict[str, Any]) -> DeploymentState:
        """Execute deployment pipeline"""

        deployment = DeploymentState(
            service_name=config.get("service_name", "service"),
            version=config.get("version", "latest"),
            environment=target,
            status="deploying"
        )

        self.deployments[deployment.deployment_id] = deployment

        try:
            # Pre-deployment checks
            await self._pre_deployment_checks(deployment, config)

            # Backup current version
            await self._backup_current_version(deployment)

            # Deploy new version
            await self._deploy_artifact(artifact, deployment, config)

            # Health checks
            await self._health_check(deployment, config)

            # Update load balancer
            await self._update_load_balancer(deployment, config)

            deployment.status = "deployed"
            deployment.deployed_at = datetime.now()
            deployment.health_status = "healthy"

        except Exception as e:
            deployment.status = "failed"
            deployment.health_status = "unhealthy"
            raise DeploymentError(f"Deployment failed: {str(e)}")

        return deployment

    async def rollback(self, deployment_id: str) -> DeploymentState:
        """Rollback to previous version"""

        if deployment_id not in self.deployments:
            raise ValueError(f"Deployment {deployment_id} not found")

        deployment = self.deployments[deployment_id]

        if not deployment.rollback_version:
            raise ValueError(f"No rollback version available for {deployment_id}")

        # Create rollback deployment
        rollback_deployment = DeploymentState(
            service_name=deployment.service_name,
            version=deployment.rollback_version,
            environment=deployment.environment,
            status="rolling_back"
        )

        try:
            # Restore previous version
            await self._restore_backup(rollback_deployment)

            # Health check
            await self._health_check(rollback_deployment, {})

            rollback_deployment.status = "deployed"
            rollback_deployment.deployed_at = datetime.now()
            rollback_deployment.health_status = "healthy"

            # Update original deployment
            deployment.status = "rolled_back"

        except Exception as e:
            rollback_deployment.status = "failed"
            raise DeploymentError(f"Rollback failed: {str(e)}")

        return rollback_deployment

    async def health_check(self, deployment_id: str) -> Dict[str, Any]:
        """Check deployment health"""

        if deployment_id not in self.deployments:
            raise ValueError(f"Deployment {deployment_id} not found")

        deployment = self.deployments[deployment_id]

        health = {
            "deployment_id": deployment_id,
            "service_name": deployment.service_name,
            "version": deployment.version,
            "status": deployment.status,
            "health_status": deployment.health_status,
            "checks": []
        }

        # Simulate health checks
        checks = [
            {"name": "service_running", "status": "pass"},
            {"name": "port_accessible", "status": "pass"},
            {"name": "database_connection", "status": "pass"},
            {"name": "memory_usage", "status": "pass", "value": "45%"},
            {"name": "cpu_usage", "status": "pass", "value": "25%"},
            {"name": "response_time", "status": "pass", "value": "120ms"}
        ]

        health["checks"] = checks
        health["overall_status"] = "healthy" if all(
            c["status"] == "pass" for c in checks
        ) else "unhealthy"

        return health

    async def _pre_deployment_checks(self, deployment: DeploymentState,
                                    config: Dict[str, Any]):
        """Perform pre-deployment validation"""

        # Check disk space
        disk_usage = psutil.disk_usage(str(self.deployment_path))
        if disk_usage.percent > 90:
            raise ResourceError("Insufficient disk space for deployment")

        # Check if service is already deploying
        active_deployments = [
            d for d in self.deployments.values()
            if d.service_name == deployment.service_name and d.status == "deploying"
        ]
        if len(active_deployments) > 1:
            raise DeploymentError(f"Service {deployment.service_name} is already being deployed")

    async def _backup_current_version(self, deployment: DeploymentState):
        """Backup current version before deployment"""

        backup_dir = self.deployment_path / "backups" / deployment.service_name
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_{timestamp}.tar.gz"

        # Simulate backup (in real implementation, would create actual backup)
        deployment.rollback_version = f"backup_{timestamp}"

    async def _deploy_artifact(self, artifact: str, deployment: DeploymentState,
                              config: Dict[str, Any]):
        """Deploy the artifact"""

        deploy_dir = self.deployment_path / deployment.service_name / deployment.version
        deploy_dir.mkdir(parents=True, exist_ok=True)

        # Simulate deployment steps
        deployment.metrics["deployment_steps"] = [
            {"step": "Extracting artifact", "status": "completed"},
            {"step": "Installing dependencies", "status": "completed"},
            {"step": "Configuring service", "status": "completed"},
            {"step": "Starting service", "status": "completed"}
        ]

    async def _health_check(self, deployment: DeploymentState, config: Dict[str, Any]):
        """Perform health check on deployment"""

        # Simulate health check
        await asyncio.sleep(1)
        deployment.health_status = "healthy"

    async def _update_load_balancer(self, deployment: DeploymentState,
                                   config: Dict[str, Any]):
        """Update load balancer configuration"""

        # Simulate load balancer update
        deployment.metrics["load_balancer_updated"] = True

    async def _restore_backup(self, deployment: DeploymentState):
        """Restore from backup"""

        # Simulate backup restoration
        await asyncio.sleep(1)


class ExecutionMonitor:
    """Real-time execution monitoring"""

    def __init__(self):
        self.active_executions: Dict[str, ExecutionState] = {}
        self.metrics_history: List[Dict[str, Any]] = []

    async def start_monitoring(self, execution_id: str, task: Task):
        """Begin monitoring execution"""

        self.active_executions[execution_id] = ExecutionState(
            task_id=task.id,
            start_time=datetime.now(),
            status="running",
            metrics={}
        )

    async def update_metrics(self, execution_id: str, metrics: Dict[str, Any]):
        """Update execution metrics"""

        if execution_id not in self.active_executions:
            return

        state = self.active_executions[execution_id]
        state.metrics.update(metrics)

        # Check for anomalies
        if metrics.get("cpu_percent", 0) > 90:
            state.metrics["warning"] = "High CPU usage detected"

        if metrics.get("memory_mb", 0) > 1024:
            state.metrics["warning"] = "High memory usage detected"

    async def complete_monitoring(self, execution_id: str, result: Any):
        """Finalize monitoring"""

        if execution_id not in self.active_executions:
            return

        state = self.active_executions[execution_id]
        state.end_time = datetime.now()
        state.duration = (state.end_time - state.start_time).total_seconds()
        state.status = "completed" if result else "failed"

        # Store in history
        self.metrics_history.append({
            "execution_id": execution_id,
            "task_id": state.task_id,
            "duration": state.duration,
            "status": state.status,
            "metrics": state.metrics
        })

        # Clean up
        del self.active_executions[execution_id]

    def get_active_executions(self) -> List[Dict[str, Any]]:
        """Get list of active executions"""

        return [
            {
                "execution_id": exec_id,
                "task_id": state.task_id,
                "status": state.status,
                "duration": (datetime.now() - state.start_time).total_seconds(),
                "metrics": state.metrics
            }
            for exec_id, state in self.active_executions.items()
        ]

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of execution metrics"""

        if not self.metrics_history:
            return {}

        total_executions = len(self.metrics_history)
        successful = sum(1 for m in self.metrics_history if m["status"] == "completed")
        failed = total_executions - successful

        durations = [m["duration"] for m in self.metrics_history if m["duration"]]
        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "total_executions": total_executions,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total_executions * 100) if total_executions else 0,
            "average_duration": avg_duration,
            "active_executions": len(self.active_executions)
        }


class ExecutionAgent(BaseAgent):
    """
    Enhanced Execution Agent with security and monitoring
    """

    def __init__(self, agent_id: Optional[str] = None,
                 name: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, name or "ExecutionAgent", config)

        # Configuration
        self.config = config or {}
        self.workspace = Path(self.config.get("workspace", "/tmp/execution_workspace"))
        self.workspace.mkdir(exist_ok=True)

        # Initialize components
        self.command_runner = CommandRunner()
        self.system_ops = SystemOperations(self.workspace)
        self.deployment_manager = DeploymentManager(self.workspace / "deployments")
        self.monitor = ExecutionMonitor()

        # Execution configuration
        self.default_timeout = self.config.get("default_timeout", 300)
        self.retry_count = self.config.get("retry_count", 3)
        self.retry_delay = self.config.get("retry_delay", 5)

        # Register capabilities
        self._register_execution_capabilities()

    def _register_execution_capabilities(self):
        """Register execution capabilities"""

        self.register_capability(AgentCapability(
            name="secure_execution",
            description="Execute commands with security controls",
            handler=self.execute_command
        ))

        self.register_capability(AgentCapability(
            name="file_operations",
            description="Perform file system operations",
            handler=self.file_operation
        ))

        self.register_capability(AgentCapability(
            name="process_management",
            description="Manage system processes",
            handler=self.process_operation
        ))

        self.register_capability(AgentCapability(
            name="deployment",
            description="Deploy and manage services",
            handler=self.deploy_service
        ))

        self.register_capability(AgentCapability(
            name="monitoring",
            description="Monitor execution and system metrics",
            handler=self.get_monitoring_data
        ))

    async def execute(self, task: Task) -> Any:
        """Execute task with monitoring"""

        execution_id = str(uuid.uuid4())

        # Start monitoring
        await self.monitor.start_monitoring(execution_id, task)

        try:
            self.logger.info(f"Executing task: {task.name}")

            task_type = task.parameters.get("type", "command")

            if task_type == "command":
                result = await self.execute_command(task.parameters)
            elif task_type == "file_operation":
                result = await self.file_operation(task.parameters)
            elif task_type == "process_operation":
                result = await self.process_operation(task.parameters)
            elif task_type == "deployment":
                result = await self.deploy_service(task.parameters)
            else:
                result = await self.execute_command(task.parameters)

            # Complete monitoring
            await self.monitor.complete_monitoring(execution_id, result)

            return result

        except Exception as e:
            await self.monitor.complete_monitoring(execution_id, None)
            raise

    async def execute_command(self, params: Dict[str, Any]) -> ExecutionResult:
        """Execute command with security and retry logic"""

        command = params.get("command")
        if not command:
            raise ValueError("Command is required")

        timeout = params.get("timeout", self.default_timeout)
        use_sandbox = params.get("use_sandbox", True)
        retry_on_failure = params.get("retry", True)

        last_error = None
        for attempt in range(self.retry_count if retry_on_failure else 1):
            try:
                self.logger.info(f"Executing command (attempt {attempt + 1}): {command}")

                result = await self.command_runner.execute(
                    command=command,
                    timeout=timeout,
                    use_sandbox=use_sandbox
                )

                if result.success:
                    return result
                else:
                    last_error = result.error or f"Command failed with exit code {result.exit_code}"

            except (TimeoutError, ResourceError) as e:
                last_error = str(e)
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")

                if attempt < self.retry_count - 1 and retry_on_failure:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise

        raise ExecutionError(f"Command failed after {self.retry_count} attempts: {last_error}")

    async def file_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform file system operation"""

        operation = params.get("operation")
        path = params.get("path")
        data = params.get("data")

        if not operation or not path:
            raise ValueError("Operation and path are required")

        return await self.system_ops.file_operation(operation, path, data)

    async def process_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform process management operation"""

        operation = params.get("operation")
        process_id = params.get("process_id")

        if not operation:
            raise ValueError("Operation is required")

        return await self.system_ops.process_operation(operation, process_id)

    async def deploy_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a service"""

        artifact = params.get("artifact")
        target = params.get("target", "production")
        config = params.get("config", {})

        if not artifact:
            raise ValueError("Artifact is required")

        deployment = await self.deployment_manager.deploy(artifact, target, config)

        return {
            "deployment_id": deployment.deployment_id,
            "service_name": deployment.service_name,
            "version": deployment.version,
            "environment": deployment.environment,
            "status": deployment.status,
            "health_status": deployment.health_status,
            "deployed_at": deployment.deployed_at.isoformat() if deployment.deployed_at else None,
            "metrics": deployment.metrics
        }

    async def rollback_deployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback a deployment"""

        deployment_id = params.get("deployment_id")

        if not deployment_id:
            raise ValueError("Deployment ID is required")

        deployment = await self.deployment_manager.rollback(deployment_id)

        return {
            "deployment_id": deployment.deployment_id,
            "service_name": deployment.service_name,
            "version": deployment.version,
            "status": deployment.status,
            "message": "Rollback completed successfully"
        }

    async def get_monitoring_data(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get monitoring data"""

        return {
            "active_executions": self.monitor.get_active_executions(),
            "metrics_summary": self.monitor.get_metrics_summary(),
            "system_info": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
            }
        }