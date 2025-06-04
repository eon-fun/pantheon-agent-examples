# TwitterGorillaMarketingAgent

## Purpose & Scope
TwitterGorillaMarketingAgent is an autonomous AI agent that:
-  Discovers relevant Twitter discussions about Web3/AI technologies
-  Engages authentically in conversations to promote NFINITY project
-  Automates organic community growth through strategic commenting
- ️ Ensures brand-safe interactions using AI moderation

## Prerequisites

### System Requirements
- Python 3.10+
- Redis server (for tracking commented posts)
- Twitter API v2 access

### API Keys
| Service          | Environment Variable | How to Obtain |
|------------------|----------------------|---------------|
| Twitter API      | Configured via `TwitterAuthClient` | Twitter Developer Portal |
| OpenAI API       | Required for `send_openai_request` | OpenAI Platform |

### Python Dependencies
Key dependencies:
```bash
fastapi==0.95.2
ray[serve]==2.5.1
aiohttp==3.8.4
redis==4.5.5
```

## Quickstart

### 1. Deployment
```python
from ray import serve
from twitter_gorilla_agent import TwitterGorillaMarketingAgent

serve.run(
    TwitterGorillaMarketingAgent.bind(),
    route_prefix="/gorilla-marketing"
)
```

### 2. API Endpoint
```bash
POST /{goal}
```
Where `goal` format is: `username.keywords.themes`  
Example: `nfinityAI.web3,ai.decentralized,autonomous_agents`

### 3. Execution Flow
1. Searches Twitter for target keywords/themes
2. Filters tweets using AI safety checks
3. Posts organic comments on top 2 relevant tweets
4. Tracks engagement in Redis
