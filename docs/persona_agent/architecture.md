# Architecture & Flow

## Overview
PersonaAgent combines vector search (Qdrant), persona storage (Redis), and text generation (OpenAI) to produce persona-specific content. It's deployed as a Ray Serve FastAPI application.

## Component Diagram
See [`architecture.puml`](./architecture.puml) showing:
- Client interaction via FastAPI
- Redis for persona metadata storage
- Qdrant for tweet similarity search
- OpenAI for text generation

## Flow Description
1. **Client POSTs** to `/{persona_name}` with a prompt
2. **Redis verification**:
   - Checks if persona exists (`{persona}:description`)
   - Retrieves persona description
3. **Qdrant search**:
   - Generates embedding for input prompt
   - Finds 5 most similar tweets from persona's collection
4. **OpenAI generation**:
   - Builds system message from Jinja2 template
   - Creates generation prompt with persona context
   - Calls OpenAI API with temperature=0.7
5. **Response formatting**:
   - Returns success status and generated text
   - Handles error cases (missing persona, etc.)

