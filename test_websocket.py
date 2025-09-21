#!/usr/bin/env python3
"""Test WebSocket connection"""
import asyncio
import json
import websockets

async def test_websocket():
    # Get auth token first
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"username": "admin", "password": "secret"}
        )
        token_data = response.json()
        token = token_data["access_token"]
        print(f"✅ Got auth token: {token[:30]}...")

    # Connect to WebSocket
    uri = f"ws://localhost:8000/ws?token={token}"
    print(f"\n🔌 Connecting to WebSocket...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")

            # Subscribe to all events
            await websocket.send(json.dumps({
                "type": "subscribe",
                "events": ["*"]
            }))

            # Wait for subscription confirmation
            response = await websocket.recv()
            print(f"📨 Received: {response}")

            # Send ping
            await websocket.send(json.dumps({"type": "ping"}))

            # Wait for pong
            response = await websocket.recv()
            print(f"📨 Received: {response}")

            print("\n✅ WebSocket test successful!")

    except Exception as e:
        print(f"❌ WebSocket error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())