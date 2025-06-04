# Architecture & Flow

## Overview
BaseAgent implements the core agent pattern with:

1. **Core Components**:
   - Workflow Runner - Executes generated plans
   - Prompt Builder - Constructs LLM prompts
   - Agent Executor - Handles LLM interactions

2. **Memory Systems**:
   - Redis - Short-term memory and chat history
   - LightRAG - Long-term knowledge storage

3. **Coordination**:
   - AI Registry - Agent and tool discovery
   - Handoff protocol - Task delegation

## Component Diagram
See [`architecture.puml`](./architecture.puml) showing:
- Core agent components
- External service integrations
- Data flow paths

## Extension Points
1. Override `handle()` for custom logic
2. Implement `reconfigure()` for runtime changes
3. Extend memory systems
4. Customize plan generation
