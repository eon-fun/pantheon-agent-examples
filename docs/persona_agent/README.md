# PersonaAgent

## Purpose & Scope
PersonaAgent is a FastAPI service that generates text (e.g., tweets) in the style of a specified persona using OpenAI, Qdrant vector search, and Redis for persona storage.

## Prerequisites
- Python 3.10+
- Running Redis instance
- Running Qdrant instance
- OpenAI API key
- Dependencies from PyPI (listed in `requirements.txt`)

### Required Environment Variables
- `OPENAI_API_KEY` - For text generation
- `REDIS_URL` - Redis connection string
- `QDRANT_URL` - Qdrant vector database URL
- `QDRANT_API_KEY` - Qdrant API key (if applicable)

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export REDIS_URL="redis://localhost:6379"
   export QDRANT_URL="http://localhost:6333"
   ```

3. **Run the agent:**
   ```bash
   serve run persona_agent:app
   ```

4. **Make requests:**
   ```bash
   curl -X POST "http://localhost:8000/{persona_name}" \
   -H "Content-Type: application/json" \
   -d '{"prompt": "your generation prompt"}'
   ```

**The agent will:**
- Verify persona exists in Redis
- Search for similar tweets in Qdrant
- Generate persona-appropriate text using OpenAI
- Return formatted response
