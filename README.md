# Charcoal - Stacked Pull Requests CLI

A Python CLI tool for managing stacked git branches and pull requests, migrated from the TypeScript-based Graphite CLI.

## Overview

Charcoal (also accessible as `gt` or `graphite`) is a command-line interface for managing complex git workflows with stacked branches and pull requests. It helps developers maintain clean, logical branch hierarchies and streamline PR workflows.

## Installation

### Prerequisites

- Python 3.11 or higher
- Poetry 1.8 or higher
- Git

### Install from source

```bash
# Clone the repository
git clone https://github.com/danerwilliams/charcoal.git
cd charcoal

# Install dependencies
poetry install

# Run the CLI
poetry run gt --help
# or
poetry run graphite --help
```

## Features

- **Stack Management**: Create and manage hierarchies of related branches
- **PR Workflows**: Streamlined pull request creation and updates
- **Branch Navigation**: Easy navigation through branch stacks
- **Repository Configuration**: Flexible configuration at repository and user levels
- **GitHub Integration**: Direct integration with GitHub PRs

## Usage

```bash
# Show version
gt --version

# Get help
gt --help

# Initialize a repository (coming in future milestones)
gt repo init
```

## Development

### Project Structure

```
charcoal/
├── __init__.py              # Package root
├── __main__.py              # CLI entry point
├── commands/                # CLI command definitions
├── actions/                 # Business logic implementations
└── lib/
    ├── git/                # Git operations
    ├── config/             # Configuration management
    ├── engine/             # Stack/graph engine
    ├── utils/              # Utility functions
    └── api/                # GitHub API integration
```

### Running Tests

```bash
poetry run pytest
```

### Code Quality

```bash
# Type checking
poetry run mypy charcoal

# Linting
poetry run ruff check charcoal

# Formatting
poetry run black charcoal
```

## Migration Status

This project is actively being migrated from TypeScript to Python. The modernization follows a phased approach:

- **Phase 1 (In Progress)**: Foundation - CLI framework, configuration, git runner
- **Phase 2**: Core features - Stack operations and branch management
- **Phase 3**: PR and remote workflows
- **Phase 4**: Hardening and distribution

## License

MIT

## Source

Migrated from: https://github.com/Khachatour/charcoal-pr-stacking.git

## Related Projects

- [Graphite CLI](https://graphite.dev/) - Original TypeScript implementation
