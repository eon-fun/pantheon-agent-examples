# Twitter Summary AI Agent

## Description

Twitter Summary AI Agent is an automated tool that monitors selected Twitter accounts for new tweets, processes them using OpenAI, and posts AI-generated summaries to a Telegram channel. The agent specializes in cryptocurrency and celebrity news, transforming multiple related tweets into concise, informative summaries with relevant context and implications.

## Features

- **Automated Tweet Monitoring**: Continuously checks for new tweets from subscribed Twitter accounts.
- **AI-Powered Summaries**: Leverages OpenAI to create coherent summaries of related tweets.
- **Context-Rich Content**: Highlights key events, potential consequences, and involved parties.
- **HTML Formatting**: Produces visually appealing posts for Telegram channels.
- **Persistent Storage**: Tracks processed tweets using Redis to prevent duplicates.

## Requirements

- Python 3.10+
- Telegram Bot Token
- Twitter API Bearer Token
- OpenAI API access
- Redis database

## Usage

1. Manage subscriptions to Twitter accounts:
   - Add a new account to monitor:
     ```
     /add_account @ElonMusk
     ```

2. The agent will automatically:
   - Check for new tweets every 30 minutes (Time can be changed)
   - Process new tweets using OpenAI
   - Post summaries to your Telegram channel

## How It Works

1. **Initialization**: The agent connects to Redis, and initializes the Telegram bot.
2. **Periodic Checking**: Every 30 minutes, it checks for new tweets from subscribed accounts.
3. **Tweet Processing**:
   - Fetches user IDs from Twitter API
   - Retrieves recent tweets
   - Filters out already processed tweets
4. **AI Summarization**:
   - Groups related tweets together
   - Sends them to OpenAI with a specialized prompt
   - Formats the summary for Telegram
5. **Publishing**: Posts the summary to the specified Telegram channel with HTML formatting.
6. **Tracking**: Updates Redis with processed tweet IDs to prevent duplicates.

## Troubleshooting

- **No Tweets Being Processed**: Check your Twitter API bearer token and rate limits.
- **Redis Connection Issues**: Verify Redis server is running and accessible.
- **Message Sending Failures**: Confirm your bot has posting permissions in the channel.

## Security Notes

- Keep your API tokens secure and never commit them to version control.
- Twitter API has rate limits - monitor usage to avoid service interruptions.
- Consider using encryption for sensitive API keys in production.
