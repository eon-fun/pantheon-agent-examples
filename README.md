# Pantheon Agent Examples

This repository contains example AI agents built for the Pantheon infrastructure using Ray Serve and FastAPI.

## Purpose

To demonstrate how to build scalable, goal-driven AI agents as modular services. Each agent follows a standardized interface and is deployable using Ray Serve.

## Structure

```
pantheon-agent-examples/
├── agents/              # Agent implementations
│   ├── base-agent/      # Base agent template
│   ├── ai_apy_pool_agent/
│   ├── ai_avatar/
│   ├── ai_dialogue_manager/
│   ├── ai_predicts_manager/
│   ├── ai_smm_manager/
│   ├── ai_twitter_summary/
│   ├── twitter-ambassador-*/  # Ambassador agent suite
│   └── ... (and more agents)
├── docs/                # Documentation
│   └── CONTRIBUTING.md  # Development guide
├── .github/             # GitHub workflows and templates
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
├── pyproject.toml       # Poetry dependencies
├── poetry.lock
├── LICENSE
├── CHANGELOG.md
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
* [Poetry](https://python-poetry.org/) for dependency management

## Installation

```bash
poetry install
```

## Running Tests

```bash
poetry run pytest
```

## Adding New Agents

To add a new agent to the PanthEON Agent Examples repository:

1. **Create a new directory** under `agents/` with your agent name
2. **Implement the agent** following the standardized interface
3. **Add configuration** for Ray Serve deployment
4. **Include documentation** explaining the agent's purpose and usage
5. **Add tests** to ensure agent functionality
6. **Update this README** with information about your agent

Each agent should follow the established patterns for:
- Goal parsing and validation
- State management with Redis
- API integration
- Error handling and logging
- Ray Serve deployment configuration

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

## Support

### Getting Help

If you need help or have questions about the PanthEON Agent Examples:

- **GitHub Issues**: For bug reports and feature requests, please use our [issue templates](https://github.com/eon-fun/pantheon-agent-examples/issues/new/choose)
- **GitHub Discussions**: For general questions and community discussions, visit our [discussions page](https://github.com/eon-fun/pantheon-agent-examples/discussions)
- **Documentation**: Check our [contributing guide](docs/CONTRIBUTING.md) for development workflows

### Response Time

We aim to respond to issues and discussions within **48 hours** during business days. Please be patient as our maintainers are volunteers.

### Breaking Changes Policy

We follow semantic versioning and maintain backward compatibility:

- **MAJOR version bumps**: We will maintain backward compatibility for at least **6 months** before removing deprecated features
- **MINOR version bumps**: Only add new features, no breaking changes
- **PATCH version bumps**: Bug fixes and security updates only

All breaking changes will be clearly documented in our [CHANGELOG.md](CHANGELOG.md) and announced in advance.

## Maintainers

This project is maintained by:

- **Technical Lead**: [@golemxiv](https://github.com/golemxiv)
- **Primary Maintainer**: [@k1llzz](https://github.com/k1llzz)
- **Core Maintainer**: [@polkadot21](https://github.com/polkadot21)
- **Infrastructure Maintainer**: [@drobotukhin](https://github.com/drobotukhin)

### Maintainer Responsibilities

- Review and merge pull requests
- Triage and respond to issues
- Release new versions
- Maintain project roadmap and direction

### Becoming a Maintainer

We welcome new maintainers! If you're interested in helping maintain this project:

1. **Contribute regularly**: Submit quality PRs and help with issue triage
2. **Show commitment**: Demonstrate sustained involvement over 3+ months
3. **Express interest**: Reach out to existing maintainers via GitHub Discussions
4. **Onboarding**: Current maintainers will provide access and guidance

### Maintainer Rotation

- Maintainers may step down at any time by notifying the team
- Inactive maintainers (6+ months) will be asked about their continued involvement
- New maintainers require approval from at least 2 existing maintainers
