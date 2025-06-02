# Telegram AI Dialogue Manager

## Description

Telegram AI Dialogue Manager is an intelligent assistant that collects, analyzes, and processes unread messages, mentions, and replies from your Telegram chats. Using OpenAI API, the agent creates concise and informative summaries of all important interactions, eliminating the need to review each message individually.

## Features

- **Automatic Message Collection**: The agent tracks and saves all unread messages, mentions of you, and replies to your messages.
- **Intelligent Summaries**: Creates a brief summary of all collected messages using OpenAI API.
- **Read Message Cleanup**: Automatically removes messages from the database once they've been read.
- **Command-Based Summaries**: Get an on-demand summary of unread interactions by using the `/summary` command.
- **Cross-Chat Monitoring**: Works across all your personal and group chats.

## Requirements

- Python 3.10+
- Telegram API credentials (API_ID and API_HASH)
- OpenAI API access
- Redis database

## Usage

1. On first run, you'll be prompted to enter:
   - Your phone number (in international format)
   - The verification code sent to your Telegram
   - Your Two-Factor Authentication password (if enabled)

2. Once authenticated, the agent will start monitoring your chats automatically.

3. To get a summary of unread messages, simply send `/summary` in any chat.

## How It Works

1. The agent listens for new messages across all your Telegram chats.
2. It saves unread messages, mentions, and replies to a Redis database.
3. When you request a summary with `/summary`, it:
   - Cleans already read messages from the database
   - Formats the remaining messages with contextual information
   - Sends them to OpenAI with a specific prompt
   - Returns a concise summary of all interactions
   
## Security Notes

- Your Telegram session is stored locally in the `my_telegram_session` file.
- Never share your API credentials or session file with anyone.
- The application uses your Telegram user account, not a bot token.

## Troubleshooting

- If you encounter authentication issues, delete the `my_telegram_session` file and restart the application.
- Ensure Redis is running properly if messages aren't being stored.
- Check your OpenAI API key and quota if summaries aren't being generated.
