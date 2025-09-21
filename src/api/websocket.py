"""WebSocket Implementation"""
from fastapi import WebSocket, WebSocketDisconnect, Query, Depends
from typing import Dict, Set, List, Optional
from datetime import datetime
import json
import asyncio
from jose import jwt, JWTError

from .config import settings
from .services.auth import auth_service

class ConnectionManager:
    """Manages WebSocket connections and event subscriptions"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}
        self.message_queue: Dict[str, List[dict]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()

        # Send any queued messages
        if client_id in self.message_queue:
            for message in self.message_queue[client_id]:
                await self.send_message(client_id, message)
            self.message_queue[client_id] = []

        # Send connection confirmation
        await self.send_message(client_id, {
            "type": "connected",
            "data": {
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        })

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        self.active_connections.pop(client_id, None)
        self.subscriptions.pop(client_id, None)

    async def send_message(self, client_id: str, message: dict):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                print(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
        else:
            # Queue message for offline client
            if client_id not in self.message_queue:
                self.message_queue[client_id] = []
            self.message_queue[client_id].append(message)

            # Limit queue size
            if len(self.message_queue[client_id]) > 100:
                self.message_queue[client_id] = self.message_queue[client_id][-100:]

    async def broadcast(self, event_type: str, data: dict, exclude: Optional[str] = None):
        """Broadcast to all clients subscribed to this event type"""
        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

        disconnected = []
        for client_id, subscriptions in self.subscriptions.items():
            if client_id == exclude:
                continue

            if event_type in subscriptions or "*" in subscriptions:
                try:
                    await self.send_message(client_id, message)
                except WebSocketDisconnect:
                    disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)

    def subscribe(self, client_id: str, events: List[str]):
        """Subscribe a client to specific events"""
        if client_id in self.subscriptions:
            for event in events:
                self.subscriptions[client_id].add(event)

    def unsubscribe(self, client_id: str, events: List[str]):
        """Unsubscribe a client from specific events"""
        if client_id in self.subscriptions:
            for event in events:
                self.subscriptions[client_id].discard(event)

    async def heartbeat_check(self):
        """Periodic heartbeat check for all connections"""
        while True:
            await asyncio.sleep(settings.ws_heartbeat_interval)
            disconnected = []

            for client_id, websocket in self.active_connections.items():
                try:
                    await websocket.send_json({"type": "ping"})
                except:
                    disconnected.append(client_id)

            for client_id in disconnected:
                self.disconnect(client_id)

# Global connection manager
manager = ConnectionManager()

async def verify_websocket_token(token: str) -> Optional[str]:
    """Verify WebSocket authentication token"""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        username = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token")
):
    """
    WebSocket endpoint for real-time communication.

    Clients must provide a valid JWT token as a query parameter.
    Supports event subscription and bi-directional messaging.
    """
    # Verify authentication
    username = await verify_websocket_token(token)
    if not username:
        await websocket.close(code=1008, reason="Invalid authentication")
        return

    client_id = f"ws-{username}-{datetime.utcnow().timestamp()}"
    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")

            # Handle different message types
            if message_type == "subscribe":
                events = data.get("events", ["*"])
                manager.subscribe(client_id, events)
                await manager.send_message(client_id, {
                    "type": "subscribed",
                    "data": {"events": events}
                })

            elif message_type == "unsubscribe":
                events = data.get("events", [])
                manager.unsubscribe(client_id, events)
                await manager.send_message(client_id, {
                    "type": "unsubscribed",
                    "data": {"events": events}
                })

            elif message_type == "ping":
                await manager.send_message(client_id, {"type": "pong"})

            elif message_type == "message":
                # Handle custom messages
                await handle_custom_message(client_id, data.get("data"))

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast("client.disconnected", {
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude=client_id)
    except Exception as e:
        print(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)

async def handle_custom_message(client_id: str, data: dict):
    """Handle custom WebSocket messages"""
    # Implement custom message handling logic here
    pass

# Event emitter functions for system events
async def emit_event(event_type: str, data: dict):
    """Emit an event to all subscribed WebSocket clients"""
    await manager.broadcast(event_type, data)

async def emit_agent_event(event: str, agent_data: dict):
    """Emit agent-related events"""
    await emit_event(f"agent.{event}", agent_data)

async def emit_task_event(event: str, task_data: dict):
    """Emit task-related events"""
    await emit_event(f"task.{event}", task_data)

async def emit_system_event(event: str, system_data: dict):
    """Emit system-related events"""
    await emit_event(f"system.{event}", system_data)

# Event hooks for the hive system
async def on_agent_registered(agent):
    """Called when a new agent is registered"""
    await emit_agent_event("registered", agent.dict())

async def on_agent_status_changed(agent):
    """Called when an agent's status changes"""
    await emit_agent_event("status_changed", agent.dict())

async def on_agent_terminated(agent_id: str):
    """Called when an agent is terminated"""
    await emit_agent_event("terminated", {"agent_id": agent_id})

async def on_task_created(task):
    """Called when a new task is created"""
    await emit_task_event("created", task.dict())

async def on_task_updated(task):
    """Called when a task is updated"""
    await emit_task_event("updated", task.dict())

async def on_task_completed(task):
    """Called when a task is completed"""
    await emit_task_event("completed", task.dict())

async def on_task_failed(task, error: str):
    """Called when a task fails"""
    await emit_task_event("failed", {
        **task.dict(),
        "error": error
    })

async def on_metrics_update(metrics):
    """Called when system metrics are updated"""
    await emit_system_event("metrics_update", metrics)