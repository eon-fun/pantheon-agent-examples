# Twitter Mentions Agent

An autonomous AI agent that monitors and responds to Twitter account mentions automatically.

## Overview

Twitter Mentions Agent is a service that periodically searches for mentions of your Twitter account, analyzes them using AI, and generates contextually relevant responses. This helps maintain an active social media presence and engage with your community without constant manual monitoring.

## Features

- **Automated Mention Monitoring**: Checks for new mentions every 15-30 minutes
- **Intelligent Reply Filtering**: Uses AI to determine which mentions require a response
- **Contextual Response Generation**: Creates personalized replies based on conversation context
- **Hashtag & Keyword Integration**: Incorporates relevant hashtags and keywords in responses
- **Rate Limiting**: Ensures appropriate delays between posts to avoid platform limitations
- **Persistence**: Tracks previously responded mentions to avoid duplicates

## Prerequisites

- Python 3.8+
- [Ray Serve](https://docs.ray.io/en/latest/serve/index.html) for deployment
- FastAPI for API endpoints
- Access to Twitter API via OAuth2
- Redis database for state persistence
- OpenAI API access for response generation
- Custom utility libraries:
  - `twitter_ambassador_utils`
  - `tweetscout_utils`
  - `redis_client`
  - `send_openai_request`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/twitter-mentions-agent.git
   cd twitter-mentions-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export TWITTER_CLIENT_ID=your_client_id
   export TWITTER_CLIENT_SECRET=your_client_secret
   export TWITTER_REDIRECT_URI=your_redirect_uri
   export TWITTER_BASIC_BEARER_TOKEN=your_bearer_token
   export TWEETSCOUT_API_KEY=your_tweetscout_api_key
   export OPENAI_API_KEY=your_openai_api_key
   # Redis configuration
   export REDIS_HOST=localhost
   export REDIS_PORT=6379
   export REDIS_PASSWORD=your_redis_password
   ```

## Usage

### Running the Agent

Start the agent using Ray Serve:

```bash
python -m twitter_mentions_agent
```

### Configuring Agent Goals

The agent accepts goals in the format:
```
username.keywords.hashtags
```

For example:
```
myaccount.blockchain,nft,web3.crypto,blockchain,nft
```

Where:
- `username`: Your Twitter username
- `keywords`: Comma-separated list of keywords to incorporate in replies
- `hashtags`: Comma-separated list of hashtags to use when relevant

### API Endpoints

- **POST /{goal}**: Triggers the agent to process mentions based on the specified goal

Example:
```bash
curl -X POST "http://localhost:8000/myaccount.blockchain,nft,web3.crypto,blockchain,nft"
```

## How It Works

1. **Initialization**: Agent starts and schedules periodic checks
2. **Mention Search**: Uses the Twitter API to find account mentions
3. **Filtering**: Checks if mentions require responses using AI
4. **Conversation Analysis**: Retrieves the full conversation thread for context
5. **Response Generation**: Creates a personalized reply using AI
6. **Posting**: Sends the reply to Twitter with appropriate rate limiting
7. **Persistence**: Records the interaction to avoid duplicate responses

## Customization

### Modifying Prompts

You can customize the AI prompts used for response generation by modifying the following variables in the code:

- `PROMPT_FOR_MENTION_REPLY`: Template for generating mention replies
- `PROMPT_CHECK_MENTION_REPLY`: Template for determining if a mention needs a reply

### Adjusting Timing

By default, the agent checks for new mentions every 15-30 minutes. You can modify this by changing:

```python
timeout = random.randint(900, 1800)  # 15-30 minutes in seconds
```

### Deployment Configuration

For production deployment, consider modifying the Ray Serve configuration in the `get_agent` function to adjust resources:

```python
@serve.deployment(
    num_replicas=2,  # Number of replicas
    ray_actor_options={"num_cpus": 1, "num_gpus": 0},  # Resource allocation
)
```

## Maintenance

- **Logs**: Monitor agent logs for insights and error tracking
- **Redis**: Periodically check Redis database to ensure proper storage of responded mentions
- **Token Rotation**: Ensure Twitter API tokens are refreshed when needed

## Troubleshooting

Common issues:

- **Rate Limiting**: If you receive rate limiting errors, increase the delay between posts
- **Token Expiration**: Ensure your Twitter OAuth tokens are valid and refresh when needed
- **Missing Mentions**: Verify your Twitter search query is correctly formatted