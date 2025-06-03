#!/bin/bash
# ExampleAgent - Usage Examples

# 1. Execute simple workflow
curl -X POST "http://localhost:8000/sample_goal" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": {
      "steps": [
        {"name": "step1", "action": "test"}
      ]
    },
    "context": {"test": true}
  }'

# 2. Check agent status
curl "http://localhost:8000/status"

# 3. Execute empty workflow (testing)
curl -X POST "http://localhost:8000/test" \
  -H "Content-Type: application/json" \
  -d '{"workflow": {"steps": []}}'
