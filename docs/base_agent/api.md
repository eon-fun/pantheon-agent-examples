# API & Configuration Reference

## Core Methods

### `handle()`
Main entry point for agent requests

### `chat()`
Handles conversational interactions

### `handoff()`
Delegates tasks to other agents

## Memory Management

### `store_interaction(goal, plan, result, context)`
Saves completed interactions

### `get_past_interactions(goal)`
Retrieves relevant past interactions

### `store_knowledge(filename, content)`
Adds to knowledge base

## Configuration

### Required Services
| Service | Purpose |
|---------|---------|
| Redis | Memory storage |
| LightRAG | Knowledge management |
| AI Registry | Agent discovery |

### Environment Variables
Configured through `BasicAgentConfig`
