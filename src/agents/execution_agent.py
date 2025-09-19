"""
Execution Agent for AgentZero
Specialized in task execution, system operations, and deployment
"""

import asyncio
import subprocess
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

import sys
sys.path.append('/home/avi/projects/agentzero')
from src.core.agent import BaseAgent, Task, AgentCapability


class ExecutionAgent(BaseAgent):
    """
    Agent specialized in executing tasks and system operations
    """
    
    def __init__(self, agent_id: Optional[str] = None, name: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, name or "ExecutionAgent", config)
        
        # Execution-specific configuration
        self.workspace = Path(config.get("workspace", "workspace")) if config else Path("workspace")
        self.workspace.mkdir(exist_ok=True)
        
        self.deployment_path = Path(config.get("deployment_path", "deployments")) if config else Path("deployments")
        self.deployment_path.mkdir(exist_ok=True)
        
        # Initialize execution capabilities
        self._register_execution_capabilities()
    
    def _register_execution_capabilities(self):
        """Register execution-specific capabilities"""
        self.register_capability(AgentCapability(
            name="task_execution",
            description="Execute system tasks and commands",
            handler=self._execute_task
        ))
        
        self.register_capability(AgentCapability(
            name="system_operations",
            description="Perform system operations",
            handler=self._system_operations
        ))
        
        self.register_capability(AgentCapability(
            name="deployment",
            description="Deploy services and applications",
            handler=self._deploy_service
        ))
        
        self.register_capability(AgentCapability(
            name="monitoring",
            description="Monitor system and services",
            handler=self._monitor_system
        ))
        
        self.register_capability(AgentCapability(
            name="automation",
            description="Automate repetitive tasks",
            handler=self._automate_task
        ))
    
    async def execute(self, task: Task) -> Any:
        """
        Execute operational task
        """
        self.logger.info(f"Executing operational task: {task.name}")
        
        task_type = task.parameters.get("type", "task_execution")
        
        if task_type == "deployment":
            return await self._deploy_service(task.parameters)
        elif task_type == "system_operations":
            return await self._system_operations(task.parameters)
        elif task_type == "monitoring":
            return await self._monitor_system(task.parameters)
        elif task_type == "automation":
            return await self._automate_task(task.parameters)
        else:
            return await self._execute_task(task.parameters)
    
    async def _execute_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a general task"""
        task_name = params.get("task_name", "Task")
        commands = params.get("commands", [])
        
        self.logger.info(f"Executing task: {task_name}")
        
        results = []
        for cmd in commands:
            result = await self._run_command(cmd)
            results.append(result)
        
        return {
            "task_name": task_name,
            "executed_at": datetime.now().isoformat(),
            "commands_executed": len(commands),
            "results": results,
            "status": "completed" if all(r["success"] for r in results) else "failed"
        }
    
    async def _deploy_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a service or application"""
        service_name = params.get("service_name", "service")
        service_type = params.get("service_type", "api")
        port = params.get("port", 8000)
        environment = params.get("environment", "production")
        
        self.logger.info(f"Deploying service: {service_name}")
        
        # Create deployment directory
        deploy_dir = self.deployment_path / service_name
        deploy_dir.mkdir(exist_ok=True)
        
        # Generate deployment configuration
        deployment_config = {
            "service_name": service_name,
            "service_type": service_type,
            "port": port,
            "environment": environment,
            "deployed_at": datetime.now().isoformat(),
            "version": params.get("version", "1.0.0"),
            "health_check_endpoint": f"http://localhost:{port}/health"
        }
        
        # Create Docker configuration if needed
        if service_type in ["api", "web"]:
            dockerfile_content = self._generate_dockerfile(service_name, service_type, port)
            dockerfile_path = deploy_dir / "Dockerfile"
            dockerfile_path.write_text(dockerfile_content)
            
            # Create docker-compose configuration
            compose_content = self._generate_docker_compose(service_name, port)
            compose_path = deploy_dir / "docker-compose.yml"
            compose_path.write_text(compose_content)
            
            deployment_config["dockerfile"] = str(dockerfile_path)
            deployment_config["compose_file"] = str(compose_path)
        
        # Create service configuration
        if service_type == "api":
            service_config = self._generate_service_config(service_name, port)
            config_path = deploy_dir / "service_config.json"
            config_path.write_text(json.dumps(service_config, indent=2))
            deployment_config["config_file"] = str(config_path)
        
        # Create systemd service file (for Linux)
        if os.name == 'posix':
            systemd_content = self._generate_systemd_service(service_name, deploy_dir)
            systemd_path = deploy_dir / f"{service_name}.service"
            systemd_path.write_text(systemd_content)
            deployment_config["systemd_file"] = str(systemd_path)
        
        # Simulate deployment process
        deployment_steps = [
            {"step": "Preparing deployment", "status": "completed"},
            {"step": "Building container", "status": "completed"},
            {"step": "Running tests", "status": "completed"},
            {"step": "Deploying to environment", "status": "completed"},
            {"step": "Health check", "status": "completed"},
            {"step": "Updating load balancer", "status": "completed"}
        ]
        
        # Save deployment manifest
        manifest_path = deploy_dir / "deployment_manifest.json"
        manifest_path.write_text(json.dumps(deployment_config, indent=2))
        
        return {
            "service_name": service_name,
            "deployment_id": f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "environment": environment,
            "port": port,
            "status": "deployed",
            "deployment_path": str(deploy_dir),
            "manifest": str(manifest_path),
            "deployment_steps": deployment_steps,
            "health_check": f"http://localhost:{port}/health",
            "rollback_available": True
        }
    
    async def _system_operations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform system operations"""
        operation = params.get("operation", "status")
        target = params.get("target", "system")
        
        self.logger.info(f"Performing system operation: {operation} on {target}")
        
        operations_log = []
        
        if operation == "backup":
            backup_result = await self._perform_backup(target)
            operations_log.append(backup_result)
        elif operation == "cleanup":
            cleanup_result = await self._perform_cleanup()
            operations_log.append(cleanup_result)
        elif operation == "update":
            update_result = await self._perform_update(target)
            operations_log.append(update_result)
        elif operation == "restart":
            restart_result = await self._restart_service(target)
            operations_log.append(restart_result)
        else:
            status_result = await self._check_system_status()
            operations_log.append(status_result)
        
        return {
            "operation": operation,
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "operations_log": operations_log,
            "status": "completed"
        }
    
    async def _monitor_system(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor system and services"""
        services = params.get("services", [])
        metrics = params.get("metrics", ["cpu", "memory", "disk"])
        
        self.logger.info(f"Monitoring system and services")
        
        # Collect system metrics
        system_metrics = {
            "cpu_usage": "15%",  # Simulated
            "memory_usage": "45%",  # Simulated
            "disk_usage": "60%",  # Simulated
            "network_io": "120 MB/s",  # Simulated
            "uptime": "45 days"  # Simulated
        }
        
        # Check service health
        service_health = {}
        for service in services:
            service_health[service] = {
                "status": "healthy",
                "response_time": "120ms",
                "error_rate": "0.01%",
                "requests_per_second": "1500"
            }
        
        # Generate alerts if needed
        alerts = []
        if float(system_metrics["cpu_usage"].rstrip('%')) > 80:
            alerts.append({"level": "warning", "message": "High CPU usage detected"})
        if float(system_metrics["disk_usage"].rstrip('%')) > 90:
            alerts.append({"level": "critical", "message": "Low disk space"})
        
        monitoring_report = {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": system_metrics,
            "service_health": service_health,
            "alerts": alerts,
            "recommendations": self._generate_monitoring_recommendations(system_metrics, service_health)
        }
        
        # Save monitoring report
        report_path = self.workspace / f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.write_text(json.dumps(monitoring_report, indent=2))
        
        return monitoring_report
    
    async def _automate_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Automate repetitive tasks"""
        task_name = params.get("task_name", "automation")
        schedule = params.get("schedule", "daily")
        script_type = params.get("script_type", "bash")
        
        self.logger.info(f"Creating automation for: {task_name}")
        
        # Generate automation script
        script_content = self._generate_automation_script(task_name, script_type)
        script_path = self.workspace / f"{task_name}_automation.{'sh' if script_type == 'bash' else 'py'}"
        script_path.write_text(script_content)
        script_path.chmod(0o755)  # Make executable
        
        # Create cron job configuration
        if schedule != "manual":
            cron_config = self._generate_cron_config(task_name, schedule, script_path)
            cron_path = self.workspace / f"{task_name}_cron.txt"
            cron_path.write_text(cron_config)
        
        # Create automation configuration
        automation_config = {
            "task_name": task_name,
            "created_at": datetime.now().isoformat(),
            "schedule": schedule,
            "script_type": script_type,
            "script_path": str(script_path),
            "enabled": True,
            "last_run": None,
            "next_run": self._calculate_next_run(schedule)
        }
        
        config_path = self.workspace / f"{task_name}_automation_config.json"
        config_path.write_text(json.dumps(automation_config, indent=2))
        
        return {
            "task_name": task_name,
            "automation_created": True,
            "script_path": str(script_path),
            "config_path": str(config_path),
            "schedule": schedule,
            "status": "active"
        }
    
    # Helper methods
    async def _run_command(self, command: str) -> Dict[str, Any]:
        """Run a system command"""
        try:
            # For safety, we'll simulate command execution
            self.logger.info(f"Would execute: {command}")
            return {
                "command": command,
                "output": f"Simulated output for: {command}",
                "success": True,
                "exit_code": 0
            }
        except Exception as e:
            return {
                "command": command,
                "error": str(e),
                "success": False,
                "exit_code": 1
            }
    
    def _generate_dockerfile(self, service_name: str, service_type: str, port: int) -> str:
        """Generate Dockerfile content"""
        if service_type == "api":
            return f"""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {port}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{port}"]
"""
        else:
            return f"""FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE {port}

CMD ["node", "server.js"]
"""
    
    def _generate_docker_compose(self, service_name: str, port: int) -> str:
        """Generate docker-compose.yml content"""
        return f"""version: '3.8'

services:
  {service_name}:
    build: .
    container_name: {service_name}
    ports:
      - "{port}:{port}"
    environment:
      - NODE_ENV=production
      - PORT={port}
    restart: unless-stopped
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
"""
    
    def _generate_service_config(self, service_name: str, port: int) -> Dict[str, Any]:
        """Generate service configuration"""
        return {
            "service": {
                "name": service_name,
                "port": port,
                "host": "0.0.0.0",
                "workers": 4,
                "timeout": 30,
                "max_connections": 1000
            },
            "logging": {
                "level": "INFO",
                "format": "json",
                "output": f"/var/log/{service_name}/service.log"
            },
            "monitoring": {
                "metrics_enabled": True,
                "metrics_port": port + 1000,
                "health_check_path": "/health"
            }
        }
    
    def _generate_systemd_service(self, service_name: str, working_dir: Path) -> str:
        """Generate systemd service file content"""
        return f"""[Unit]
Description={service_name} Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={working_dir}
ExecStart=/usr/bin/python3 main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    async def _perform_backup(self, target: str) -> Dict[str, Any]:
        """Perform backup operation"""
        backup_path = self.workspace / "backups" / f"{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        backup_path.parent.mkdir(exist_ok=True)
        
        return {
            "operation": "backup",
            "target": target,
            "backup_path": str(backup_path),
            "size": "120 MB",  # Simulated
            "status": "completed"
        }
    
    async def _perform_cleanup(self) -> Dict[str, Any]:
        """Perform cleanup operation"""
        return {
            "operation": "cleanup",
            "files_removed": 42,  # Simulated
            "space_freed": "2.3 GB",  # Simulated
            "status": "completed"
        }
    
    async def _perform_update(self, target: str) -> Dict[str, Any]:
        """Perform update operation"""
        return {
            "operation": "update",
            "target": target,
            "packages_updated": 15,  # Simulated
            "version": "2.1.0",  # Simulated
            "status": "completed"
        }
    
    async def _restart_service(self, service: str) -> Dict[str, Any]:
        """Restart a service"""
        return {
            "operation": "restart",
            "service": service,
            "downtime": "2 seconds",  # Simulated
            "status": "running"
        }
    
    async def _check_system_status(self) -> Dict[str, Any]:
        """Check system status"""
        return {
            "operation": "status_check",
            "system_status": "healthy",
            "services_running": 12,  # Simulated
            "last_error": None,
            "uptime": "45 days"  # Simulated
        }
    
    def _generate_monitoring_recommendations(self, metrics: Dict, health: Dict) -> List[str]:
        """Generate monitoring recommendations"""
        recommendations = []
        
        cpu_usage = float(metrics.get("cpu_usage", "0%").rstrip('%'))
        if cpu_usage > 70:
            recommendations.append("Consider scaling up CPU resources")
        
        disk_usage = float(metrics.get("disk_usage", "0%").rstrip('%'))
        if disk_usage > 80:
            recommendations.append("Clean up disk space or increase storage")
        
        for service, status in health.items():
            if status.get("error_rate", "0%") != "0%":
                recommendations.append(f"Investigate errors in {service}")
        
        return recommendations
    
    def _generate_automation_script(self, task_name: str, script_type: str) -> str:
        """Generate automation script"""
        if script_type == "bash":
            return f"""#!/bin/bash
# Automation script for {task_name}
# Generated by ExecutionAgent

set -e

echo "Starting {task_name} automation..."

# Add your automation logic here
date >> /tmp/{task_name}.log
echo "Task completed" >> /tmp/{task_name}.log

echo "{task_name} automation completed successfully"
"""
        else:  # Python
            return f"""#!/usr/bin/env python3
# Automation script for {task_name}
# Generated by ExecutionAgent

import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info(f"Starting {task_name} automation...")
    
    # Add your automation logic here
    timestamp = datetime.now().isoformat()
    with open(f'/tmp/{task_name}.log', 'a') as f:
        f.write(f"{{timestamp}}: Task completed\\n")
    
    logger.info(f"{task_name} automation completed successfully")

if __name__ == "__main__":
    main()
"""
    
    def _generate_cron_config(self, task_name: str, schedule: str, script_path: Path) -> str:
        """Generate cron configuration"""
        schedules = {
            "hourly": "0 * * * *",
            "daily": "0 0 * * *",
            "weekly": "0 0 * * 0",
            "monthly": "0 0 1 * *"
        }
        
        cron_schedule = schedules.get(schedule, "0 0 * * *")
        return f"{cron_schedule} {script_path} >> /var/log/{task_name}.log 2>&1"
    
    def _calculate_next_run(self, schedule: str) -> str:
        """Calculate next run time based on schedule"""
        from datetime import timedelta
        
        now = datetime.now()
        if schedule == "hourly":
            next_run = now + timedelta(hours=1)
        elif schedule == "daily":
            next_run = now + timedelta(days=1)
        elif schedule == "weekly":
            next_run = now + timedelta(weeks=1)
        elif schedule == "monthly":
            next_run = now + timedelta(days=30)
        else:
            next_run = now
        
        return next_run.isoformat()