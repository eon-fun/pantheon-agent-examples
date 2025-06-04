#!/bin/bash
# CreativityService - Usage Examples

# 1. Create lipsync v1
curl -X POST "http://localhost:8000/lipsyncs/" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world!",
    "avatar_id": "avatar_123",
    "voice_id": "voice_456",
    "response_format": "mp4"
  }'

# 2. Generate AI Short preview
curl -X POST "http://localhost:8000/ai_shorts/preview/" \
  -H "Content-Type: application/json" \
  -d '{
    "avatar_id": "avatar_789",
    "script": "This is an example AI short video script",
    "voice_id": "voice_101"
  }'

# 3. Check task status
curl "http://localhost:8000/lipsyncs_v2/task_123/"

# 4. Health check
curl "http://localhost:8000/_health/"