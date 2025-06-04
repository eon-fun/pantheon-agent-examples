# CreativityService

## Purpose & Scope
CreativityService provides AI-powered media generation capabilities including:
- Lip-sync video generation (v1 and v2)
- AI Short video creation
- Preview generation
- Rendering management

## Prerequisites
- Python 3.10+
- Ray Serve environment
- Creatify API credentials
- Dependencies from PyPI (listed in `requirements.txt`)

### Required Environment Variables
- `CREATIVITY_BASE_URL` - Base URL for Creatify API
- `CREATIVITY_API_ID` - API authentication ID
- `CREATIVITY_API_KEY` - API authentication key
- `LOG_LEVEL` - Logging level (default: "info")

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export CREATIVITY_BASE_URL="https://api.creatify.ai"
   export CREATIVITY_API_ID="your-api-id"
   export CREATIVITY_API_KEY="your-api-key"
   ```

3. **Run the agent:**
   ```bash
   serve run creativity_service:agent_builder
   ```

4. **Generate content:**
   ```bash
   # Create lipsync video
   curl -X POST "http://localhost:8000/lipsyncs/" \
   -H "Content-Type: application/json" \
   -d '{
     "text": "Hello world",
     "avatar_id": "avatar_123",
     "voice_id": "voice_456"
   }'
   ```

**Key Features:**
- Multiple media generation endpoints
- Preview functionality
- Async rendering
- Status tracking

