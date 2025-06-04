# ExampleAgent

## Purpose & Scope
ExampleAgent serves as a template for creating new agents in the system. It demonstrates the base structure including:
- FastAPI endpoint handling
- Ray Serve deployment patterns
- Workflow execution framework
- Configuration management

## Prerequisites
- Python 3.10+
- Ray Serve environment
- Base agent framework installed
- Dependencies from PyPI (listed in `requirements.txt`)

### Required Environment Variables
- `RAY_ADDRESS` - Ray cluster address (default: "auto")
- `AGENT_CONFIG_PATH` - Path to agent configuration (optional)

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the agent:**
   ```bash
   python example_agent/main.py
   ```

3. **Make requests:**
   ```bash
   curl -X POST "http://localhost:8000/sample_goal" \
   -H "Content-Type: application/json" \
   -d '{"workflow": {"steps": []}, "context": {}}'
   ```

**The agent provides:**
- Base agent functionality
- Custom workflow execution
- Ray Serve scaling capabilities
- Example sub-agent pattern
