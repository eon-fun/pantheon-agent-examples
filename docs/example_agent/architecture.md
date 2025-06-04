# Architecture & Flow

## Overview
ExampleAgent implements the standard agent pattern with:

1. **Public Interface**:
   - FastAPI endpoint at `/{goal}`
   - Workflow execution handler
   - Context-aware processing

2. **Internal Components**:
   - SubAgent for scaled processing
   - Base agent functionality
   - Configuration management

## Component Diagram
See [`architecture.puml`](./architecture.puml) showing:
- Public FastAPI interface
- Ray Serve deployment structure
- Internal SubAgent component
- Workflow execution path

## Extension Points
1. Override `handle()` method
2. Add new SubAgents
3. Extend Workflow model
4. Customize bootstrap process
