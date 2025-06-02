# Telegram Listener Agent

This agent listens to messages in a specified Telegram chat, processes them, and stores them in a knowledge base (PostgreSQL and Qdrant).

## Functionality

- Connects to Telegram using a pre-configured account via `TelethonClientManager` (fetches session from Redis).
- Listens for new messages in a specific target chat/channel.
- Provides API endpoints (`/control/start`, `/control/stop`, `/control/status`) to manage the listening process.
- For each new message:
  - Extracts relevant data (message ID, chat ID, user ID, username, text, timestamp).
  - Stores structured data in a PostgreSQL table (`telegram_messages`).
  - Generates text embeddings using OpenAI (`text-embedding-3-large`).
  - Stores the embedding, message ID (from Postgres), and other metadata in a Qdrant collection (`telegram_messages`).
- Automatically creates the PostgreSQL table and Qdrant collection if they don't exist upon startup.
