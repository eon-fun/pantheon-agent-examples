# Creativity Agent

This agent acts as a Ray Serve service providing an HTTP interface to the Creatify API (https://creativity.ai/). It allows other services or agents within the PantheonAI ecosystem to generate AI shorts and perform lipsync tasks without needing direct access to the Creatify API keys or implementation details.

## Features

- Exposes Creatify API endpoints for:
  - AI Shorts (create, preview, render, get by ID)
  - Lipsync v1 (create, preview, render, get by ID)
  - Lipsync v2 (create, preview, render, get by ID)
- Runs as a scalable Ray Serve deployment.
- Configurable via `.env` file.

## Setup

1. **Environment Variables:** Create a `.env` file in the `agents/creativity-agent/` directory with the following content:

   ```dotenv
   # .env file for Creativity Agent
   CREATIVITY_BASE_URL=https://api.creativity.ai/v1 # Optional: Override default
   CREATIVITY_API_ID="YOUR_CREATIVITY_API_ID_HERE"
   CREATIVITY_API_KEY="YOUR_CREATIVITY_API_KEY_HERE"

   # Optional Ray Serve settings
   # DEPLOYMENT_NAME=CreativityService
   # NUM_REPLICAS=1
   ```

   Replace placeholders with your actual Creatify API credentials.

2. **Install Dependencies:**

   ```bash
   cd agents/creativity-agent
   poetry install
   ```

## Running

### Locally with Ray Serve

1. Start Ray (if not already running): `ray start --head`
2. Run the agent using Ray Serve CLI:

   ```bash
   serve run src.creativity_agent.ray_entrypoint:agent_builder
   ```

   The service will typically be available at `http://localhost:8000`.

### With Docker

1. Build the Docker image:
   ```bash
   docker build -t creativity-agent agents/creativity-agent/
   ```
2. Run the Docker container:
   ```bash
   # Make sure to pass your API keys as environment variables
   docker run -p 8000:8000 \\
     -e CREATIVITY_API_ID="YOUR_CREATIVITY_API_ID_HERE" \\
     -e CREATIVITY_API_KEY="YOUR_CREATIVITY_API_KEY_HERE" \\
     creativity-agent
   ```

## API Endpoints

The agent exposes the Creatify API functionality via HTTP endpoints relative to the deployment's route prefix (default is `/`). See the FastAPI documentation available at `/docs` when the service is running for details on request/response schemas.

- `/ai_shorts/` (POST)
- `/ai_shorts/preview/` (POST)
- `/ai_shorts/{short_id}/render/` (POST)
- `/ai_shorts/{short_id}/` (GET)
- `/lipsyncs/` (POST)
- `/lipsyncs/preview/` (POST)
- `/lipsyncs/{lipsync_id}/render/` (POST)
- `/lipsyncs/{lipsync_id}/` (GET)
- `/lipsyncs_v2/` (POST)
- `/lipsyncs_v2/preview/` (POST)
- `/lipsyncs_v2/{lipsync_id}/render/` (POST)
- `/lipsyncs_v2/{lipsync_id}/` (GET)
- `/_health/` (GET) - Health check
