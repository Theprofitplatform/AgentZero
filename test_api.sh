#!/bin/bash

# API Testing Script
API_URL="http://localhost:8000"
TOKEN=""

echo "🔐 Testing Authentication..."
TOKEN=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secret"}' | jq -r '.access_token')

echo "Token obtained: ${TOKEN:0:20}..."

echo -e "\n📊 Testing Health Check..."
curl -s "$API_URL/health" | jq '.'

echo -e "\n🤖 Testing Agent Endpoints..."
echo "Getting all agents:"
curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/api/v1/agents" | jq '.[0]'

echo -e "\n📋 Testing Task Endpoints..."
echo "Getting all tasks:"
curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/api/v1/tasks" | jq '.[0]'

echo -e "\n➕ Creating a new task:"
curl -s -X POST "$API_URL/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Task from API",
    "description": "Testing task creation via API",
    "type": "general",
    "priority": "normal",
    "tags": ["test", "api"]
  }' | jq '.'

echo -e "\n📈 Getting task statistics:"
curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/api/v1/tasks/stats/summary" | jq '.'

echo -e "\n✅ All API tests completed!"