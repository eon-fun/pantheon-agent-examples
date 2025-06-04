# Architecture & Flow

## Overview
CreativityService acts as a gateway to Creatify's media generation API with:

1. **API Layer**:
   - FastAPI endpoint routing
   - Request validation
   - Response formatting

2. **Service Layer**:
   - HTTP client management
   - Error handling
   - Request tracing

3. **Integration Layer**:
   - Creatify API communication
   - Authentication handling
   - Timeout management

## Component Diagram
See [`architecture.puml`](./architecture.puml) showing:
- Client-facing FastAPI interface
- Ray Serve deployment
- Creatify API integration
- Data flow paths

## Error Handling
- HTTP status code translation
- Detailed error logging
- Request ID tracing
