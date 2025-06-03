#!/bin/bash
# TelegramListenerAgent - Basic Interaction Examples

# 1. Start the listener service
curl -s -X POST \
  http://localhost:8000/control/start

# Expected response:
# {
#   "status": "Listener start requested"
# }

# 2. Check listener status
curl -s \
  http://localhost:8000/control/status

# Expected response format:
# {
#   "status": "running",
#   "client_connected": true,
#   "phone": "+1234567890",
#   "target_chat": "-1001234567890"
# }

# 3. Stop the listener service
curl -s -X POST \
  http://localhost:8000/control/stop

# Expected response:
# {
#   "status": "Listener stop requested"
# }

# 4. Example error case (missing auth)
# Simulate by stopping then checking status
curl -s -X POST http://localhost:8000/control/stop
sleep 2
curl -s http://localhost:8000/control/status

# Expected error state response:
# {
#   "status": "stopped",
#   "client_connected": false,
#   "phone": "+1234567890",
#   "target_chat": "-1001234567890"
# }