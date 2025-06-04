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

## Installing & Running Pre-commit

This repository uses pre-commit hooks to enforce code quality standards including formatting, linting, and type checking.

### Installation

1. **Install dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install pre-commit ruff mypy
   ```

2. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

### Running Pre-commit

* **Automatically on commit:** Pre-commit hooks will run automatically before each commit
* **Manually on all files:**
  ```bash
  pre-commit run --all-files
  ```
* **Manually on specific files:**
  ```bash
  pre-commit run --files path/to/file.py
  ```

### Pre-commit Tools

The repository uses the following tools:

* **Ruff**: Lightning-fast Python linter and formatter (replaces black, flake8, isort)
* **mypy**: Static type checker for Python
* **Standard hooks**: YAML validation, end-of-file fixing, trailing whitespace removal

### Code Quality Standards

- All Python code is automatically formatted with Ruff
- Type hints are enforced with mypy (in relaxed mode for legacy code)
- Print statements are allowed for debugging and logging
- Docstrings should end with periods and use proper punctuation

### Troubleshooting

If pre-commit fails:
1. Review the error messages
2. Fix the reported issues
3. Run `pre-commit run --all-files` to verify fixes
4. Commit your changes

For persistent issues with specific files, you can temporarily skip hooks:
```bash
git commit --no-verify
```
**Note:** Use `--no-verify` sparingly and only when necessary.
