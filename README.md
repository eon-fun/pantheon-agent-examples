# Pantheon Agent Examples

This repository contains example AI agents built for the Pantheon infrastructure using Ray Serve and FastAPI.

## Purpose

To demonstrate how to build scalable, goal-driven AI agents as modular services. Each agent follows a standardized interface and is deployable using Ray Serve.

## Structure

```
pantheon-agent-examples/
├── src/
│   └── agents/          # Folder containing agent implementations
├── .coveragerc
├── .gitignore
├── LICENSE
├── CODE_OF_CONDUCT.md
└── README.md
```

## Example Agent: `TwitterLikerAgent`

The `TwitterLikerAgent` is designed to like tweets based on a given goal containing a username, keywords, and themes. It integrates with:

* FastAPI for HTTP routing
* Redis for tracking previously liked tweets
* Twitter API for interacting with tweets
* Ray Serve for deployment and scalability

### Sample Flow

1. Parses the goal (e.g., `username.keywords.themes`)
2. Searches for tweets using the extracted keywords and themes
3. Filters out already liked tweets using Redis
4. Likes a random subset of new tweets
5. Updates the state in Redis

## Requirements

* Python 3.10+
* Ray Serve
* FastAPI
* Redis
* Twitter API credentials
