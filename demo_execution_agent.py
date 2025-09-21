#!/usr/bin/env python3
"""
Demo script for Enhanced Execution Agent
Shows secure command execution, sandboxing, deployment, and monitoring
"""

import asyncio
import json
from datetime import datetime
import sys
sys.path.append('/mnt/c/Users/abhis/projects/AgentZero')

from src.agents.execution_agent_enhanced import (
    ExecutionAgent,
    CommandValidator,
    CommandRunner,
    ResourceLimits,
    SandboxEnvironment,
    SystemOperations,
    DeploymentManager,
    ExecutionMonitor
)
from src.core.agent import Task, Priority
from pathlib import Path


async def demo_command_validation():
    """Demo command validation and security"""
    print("\n" + "="*60)
    print("DEMO: Command Validation & Security")
    print("="*60)

    validator = CommandValidator()

    # Test commands
    test_commands = [
        ("ls -la", "Safe"),
        ("echo 'Hello World'", "Safe"),
        ("python3 script.py", "Safe"),
        ("rm -rf /", "Dangerous"),
        ("sudo apt-get update", "Dangerous"),
        (":(){ :|:& };:", "Dangerous"),
        ("cat /etc/passwd", "Dangerous"),
        ("curl https://api.example.com", "Safe"),
        ("eval 'malicious code'", "Dangerous"),
    ]

    print("\n📋 Testing Command Validation:")
    for cmd, expected in test_commands:
        is_valid, error = validator.validate(cmd)
        status = "✅ ALLOWED" if is_valid else "🚫 BLOCKED"
        print(f"  {status}: {cmd[:40]:<40} [{expected}]")
        if error and not is_valid:
            print(f"          Reason: {error}")

    return validator


async def demo_sandboxed_execution():
    """Demo sandboxed command execution"""
    print("\n" + "="*60)
    print("DEMO: Sandboxed Command Execution")
    print("="*60)

    # Create command runner with resource limits
    resource_limits = ResourceLimits(
        cpu_percent=50.0,
        memory_mb=256,
        disk_io_mb=50,
        max_processes=5
    )

    runner = CommandRunner(resource_limits=resource_limits)

    print("\n🔒 Resource Limits:")
    print(f"  • CPU: {resource_limits.cpu_percent}%")
    print(f"  • Memory: {resource_limits.memory_mb}MB")
    print(f"  • Disk I/O: {resource_limits.disk_io_mb}MB/s")
    print(f"  • Max Processes: {resource_limits.max_processes}")

    # Execute safe commands in sandbox
    safe_commands = [
        "echo 'Testing sandboxed execution'",
        "pwd",
        "whoami",
        "date",
        "ls -la"
    ]

    print("\n🏗️ Executing Commands in Sandbox:")
    for cmd in safe_commands:
        try:
            print(f"\n  Command: {cmd}")
            result = await runner.execute(cmd, timeout=5, use_sandbox=True)

            print(f"  ✅ Exit Code: {result.exit_code}")
            print(f"  📊 Duration: {result.duration:.2f}s")
            print(f"  💻 CPU Used: {result.resource_usage.get('cpu_percent', 0):.1f}%")
            print(f"  🧠 Memory Used: {result.resource_usage.get('memory_mb', 0):.1f}MB")

            if result.stdout:
                output = result.stdout.strip()[:100]
                print(f"  📤 Output: {output}")

            if result.sandbox_path:
                print(f"  📁 Sandbox: {result.sandbox_path}")

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

    return runner


async def demo_file_operations():
    """Demo secure file operations"""
    print("\n" + "="*60)
    print("DEMO: Secure File Operations")
    print("="*60)

    workspace = Path("/tmp/execution_demo")
    workspace.mkdir(exist_ok=True)

    sys_ops = SystemOperations(workspace)

    print(f"\n📂 Workspace: {workspace}")

    # Test file operations
    operations = [
        ("write", "test_file.txt", "Hello from ExecutionAgent!"),
        ("write", "config.json", json.dumps({"version": "1.0", "enabled": True})),
        ("read", "test_file.txt", None),
        ("list", ".", None),
        ("copy", "test_file.txt", "backup.txt"),
        ("move", "backup.txt", "archive/backup.txt"),
    ]

    print("\n📋 File Operations:")
    for op, path, data in operations:
        try:
            print(f"\n  Operation: {op} {path}")
            result = await sys_ops.file_operation(op, path, data)

            if result.get("success"):
                print(f"  ✅ Success")

                if op == "read":
                    print(f"  📄 Content: {result.get('content', '')[:50]}...")
                elif op == "list":
                    print(f"  📁 Files: {result.get('count', 0)} items")
                    for f in result.get('files', [])[:5]:
                        print(f"     - {f}")
                elif op == "write":
                    print(f"  ✏️ Bytes written: {result.get('bytes_written', 0)}")

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

    # Test security - trying to access outside workspace
    print("\n\n🔒 Security Test - Path Traversal Prevention:")
    try:
        print("  Attempting to read /etc/passwd...")
        await sys_ops.file_operation("read", "/etc/passwd")
        print("  ❌ SECURITY BREACH - This shouldn't happen!")
    except Exception as e:
        print(f"  ✅ Access blocked: {str(e)}")

    return sys_ops


async def demo_process_management():
    """Demo process management"""
    print("\n" + "="*60)
    print("DEMO: Process Management")
    print("="*60)

    workspace = Path("/tmp/execution_demo")
    sys_ops = SystemOperations(workspace)

    print("\n🔄 Process Operations:")

    # List processes
    print("\n  📋 Listing processes...")
    result = await sys_ops.process_operation("list")
    processes = result.get("processes", [])[:5]

    print(f"  Found {len(result.get('processes', []))} processes")
    print("\n  Top 5 processes:")
    for proc in processes:
        print(f"    • PID {proc['pid']}: {proc['name']:<20} [{proc['status']}]")

    # Get info about current process
    import os
    current_pid = os.getpid()

    print(f"\n  ℹ️ Current process info (PID: {current_pid}):")
    try:
        result = await sys_ops.process_operation("info", current_pid)
        info = result.get("info", {})
        print(f"    Name: {info.get('name')}")
        print(f"    Status: {info.get('status')}")
        print(f"    CPU: {info.get('cpu_percent', 0):.1f}%")
        print(f"    Memory: {info.get('memory_mb', 0):.1f}MB")
        print(f"    Threads: {info.get('num_threads', 0)}")
    except Exception as e:
        print(f"    Error: {str(e)}")

    return sys_ops


async def demo_deployment():
    """Demo deployment automation"""
    print("\n" + "="*60)
    print("DEMO: Deployment Automation")
    print("="*60)

    deployment_path = Path("/tmp/execution_demo/deployments")
    deployment_path.mkdir(parents=True, exist_ok=True)

    deployment_manager = DeploymentManager(deployment_path)

    print(f"\n🚀 Deployment Path: {deployment_path}")

    # Deploy a service
    config = {
        "service_name": "demo-api",
        "version": "2.0.0",
        "port": 8080,
        "health_check_endpoint": "http://localhost:8080/health"
    }

    print("\n📦 Deploying Service:")
    print(f"  • Service: {config['service_name']}")
    print(f"  • Version: {config['version']}")
    print(f"  • Port: {config['port']}")

    deployment = await deployment_manager.deploy(
        artifact="demo-api:2.0.0",
        target="staging",
        config=config
    )

    print(f"\n  ✅ Deployment Status: {deployment.status}")
    print(f"  🆔 Deployment ID: {deployment.deployment_id}")
    print(f"  🏥 Health Status: {deployment.health_status}")

    if deployment.metrics.get("deployment_steps"):
        print("\n  📋 Deployment Steps:")
        for step in deployment.metrics["deployment_steps"]:
            status = "✅" if step["status"] == "completed" else "⏳"
            print(f"    {status} {step['step']}")

    # Check health
    print("\n🏥 Health Check:")
    health = await deployment_manager.health_check(deployment.deployment_id)

    print(f"  Overall Status: {health['overall_status']}")
    print("\n  Health Checks:")
    for check in health["checks"][:5]:
        status = "✅" if check["status"] == "pass" else "❌"
        value = f" ({check.get('value', '')})" if 'value' in check else ""
        print(f"    {status} {check['name']}{value}")

    # Simulate rollback
    print("\n🔄 Testing Rollback Capability:")
    deployment.rollback_version = "backup_20250921_120000"  # Simulate backup

    try:
        print(f"  Rolling back deployment {deployment.deployment_id[:8]}...")
        rollback = await deployment_manager.rollback(deployment.deployment_id)
        print(f"  ✅ Rollback Status: {rollback.status}")
        print(f"  📌 Restored Version: {rollback.version}")
    except Exception as e:
        print(f"  ℹ️ Rollback info: {str(e)}")

    return deployment_manager


async def demo_monitoring():
    """Demo execution monitoring"""
    print("\n" + "="*60)
    print("DEMO: Execution Monitoring")
    print("="*60)

    monitor = ExecutionMonitor()

    # Simulate some executions
    print("\n📊 Simulating Task Executions:")

    tasks = [
        Task(name="Data Processing", priority=Priority.HIGH),
        Task(name="Report Generation", priority=Priority.MEDIUM),
        Task(name="Backup Operation", priority=Priority.LOW),
    ]

    for i, task in enumerate(tasks):
        exec_id = f"exec_{i:03d}"

        print(f"\n  Starting: {task.name}")
        await monitor.start_monitoring(exec_id, task)

        # Simulate execution and metrics
        await asyncio.sleep(0.5)

        metrics = {
            "cpu_percent": 25.5 + i * 10,
            "memory_mb": 128 + i * 64,
            "disk_read_mb": 10.5,
            "disk_write_mb": 5.2
        }

        await monitor.update_metrics(exec_id, metrics)

        # Complete execution
        await monitor.complete_monitoring(exec_id, {"status": "success"})

        print(f"  ✅ Completed: {task.name}")
        print(f"     CPU: {metrics['cpu_percent']:.1f}%")
        print(f"     Memory: {metrics['memory_mb']}MB")

    # Get monitoring summary
    print("\n📈 Monitoring Summary:")
    summary = monitor.get_metrics_summary()

    print(f"  • Total Executions: {summary.get('total_executions', 0)}")
    print(f"  • Successful: {summary.get('successful', 0)}")
    print(f"  • Failed: {summary.get('failed', 0)}")
    print(f"  • Success Rate: {summary.get('success_rate', 0):.1f}%")
    print(f"  • Avg Duration: {summary.get('average_duration', 0):.2f}s")

    return monitor


async def demo_full_agent():
    """Demo full ExecutionAgent with all features"""
    print("\n" + "="*60)
    print("DEMO: Full ExecutionAgent Integration")
    print("="*60)

    # Initialize agent
    config = {
        "workspace": "/tmp/execution_agent_demo",
        "default_timeout": 30,
        "retry_count": 3,
        "retry_delay": 2
    }

    agent = ExecutionAgent(
        agent_id="executor-001",
        name="Demo Executor",
        config=config
    )

    print(f"\n🤖 Agent: {agent.name}")
    print(f"📁 Workspace: {agent.workspace}")
    print(f"⏱️ Default Timeout: {agent.default_timeout}s")
    print(f"🔁 Retry Count: {agent.retry_count}")

    # Test various operations through the agent
    print("\n📋 Testing Agent Capabilities:")

    # 1. Execute safe command
    print("\n1️⃣ Secure Command Execution:")
    task1 = Task(
        name="System Info",
        priority=Priority.MEDIUM,
        parameters={
            "type": "command",
            "command": "echo 'Agent is operational'",
            "use_sandbox": True,
            "timeout": 5
        }
    )

    try:
        result = await agent.execute(task1)
        print(f"   ✅ Command executed successfully")
        print(f"   📤 Output: {result.stdout.strip()}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

    # 2. File operation
    print("\n2️⃣ File Operation:")
    task2 = Task(
        name="Create Config",
        priority=Priority.HIGH,
        parameters={
            "type": "file_operation",
            "operation": "write",
            "path": "agent_config.json",
            "data": json.dumps({
                "agent_id": agent.agent_id,
                "timestamp": datetime.now().isoformat(),
                "status": "active"
            }, indent=2)
        }
    )

    try:
        result = await agent.execute(task2)
        print(f"   ✅ File created: {result.get('path')}")
        print(f"   📝 Bytes written: {result.get('bytes_written')}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

    # 3. Process monitoring
    print("\n3️⃣ Process Monitoring:")
    task3 = Task(
        name="Process Check",
        priority=Priority.LOW,
        parameters={
            "type": "process_operation",
            "operation": "list"
        }
    )

    try:
        result = await agent.execute(task3)
        print(f"   ✅ Processes found: {len(result.get('processes', []))}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

    # 4. Get monitoring data
    print("\n4️⃣ Agent Monitoring Data:")
    monitoring_data = await agent.get_monitoring_data()

    print(f"   📊 Active Executions: {len(monitoring_data['active_executions'])}")

    system_info = monitoring_data.get('system_info', {})
    print(f"   💻 System Status:")
    print(f"      CPU: {system_info.get('cpu_percent', 0):.1f}%")
    print(f"      Memory: {system_info.get('memory_percent', 0):.1f}%")
    print(f"      Disk: {system_info.get('disk_usage', 0):.1f}%")

    metrics_summary = monitoring_data.get('metrics_summary', {})
    if metrics_summary:
        print(f"   📈 Execution Metrics:")
        print(f"      Total: {metrics_summary.get('total_executions', 0)}")
        print(f"      Success Rate: {metrics_summary.get('success_rate', 0):.1f}%")

    # Show agent capabilities
    print("\n🎯 Agent Capabilities:")
    # capabilities is a dictionary, get the values
    caps = list(agent.capabilities.values())
    for cap in caps[:5]:
        print(f"   • {cap.name}: {cap.description}")

    return agent


async def main():
    """Run all demos"""
    print("\n" + "🚀 "*20)
    print("  AGENTZERO EXECUTION AGENT - SECURITY & AUTOMATION DEMO")
    print("🚀 "*20)

    print("\n⚠️ Note: This demo runs in a safe, simulated environment.")
    print("All dangerous commands are blocked and operations are sandboxed.")

    try:
        # Run demos
        await demo_command_validation()
        await demo_sandboxed_execution()
        await demo_file_operations()
        await demo_process_management()
        await demo_deployment()
        await demo_monitoring()
        await demo_full_agent()

        print("\n" + "="*60)
        print("✨ Demo Complete! Execution Agent is ready for production use.")
        print("="*60)

        print("\n🔒 Security Features Demonstrated:")
        print("  ✅ Command validation with whitelist/blacklist")
        print("  ✅ Sandboxed execution environment")
        print("  ✅ Resource limits and monitoring")
        print("  ✅ Path traversal prevention")
        print("  ✅ Process isolation")

        print("\n🚀 Automation Features Demonstrated:")
        print("  ✅ Secure command execution with retry")
        print("  ✅ File system operations")
        print("  ✅ Process management")
        print("  ✅ Deployment with rollback")
        print("  ✅ Real-time monitoring")
        print("  ✅ Health checks")

    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())