# Charcoal - Git Stack Management CLI

A Python CLI for managing Git stacks and pull requests. This is a modern reimplementation of the Graphite CLI in Python, providing powerful tools for managing stacked pull requests and streamlined Git workflows.

## Overview

Charcoal helps developers work with stacked pull requests - a workflow where multiple interdependent branches are built on top of each other. This approach enables breaking large features into smaller, reviewable chunks while maintaining dependencies between them.

## Features (In Development)

- **Branch Management**: Create, track, and navigate through stacked branches
- **Stack Operations**: Restack, rebase, and manage branch hierarchies
- **PR Integration**: Submit and sync pull requests with GitHub
- **Visualization**: View branch stacks and their relationships
- **Configuration**: Flexible repository and user-level configuration

## Installation

This project uses Poetry for dependency management. To install:

```bash
# Install dependencies
poetry install

# Run the CLI
poetry run gt --help
# or
poetry run graphite --help
```

## Development

### Requirements

- Python 3.11 or higher
- Poetry 1.8+
- Git

### Project Structure

```
charcoal/
├── __init__.py          # Package root
├── __main__.py          # CLI entry point
├── commands/            # CLI command definitions
├── actions/             # Business logic
└── lib/                 # Core library modules
    ├── git/            # Git operations
    ├── config/         # Configuration management
    ├── engine/         # Stack/graph logic
    ├── api/            # GitHub integration
    ├── errors/         # Error handling
    └── utils/          # Utilities
```

### Running Tests

```bash
poetry run pytest
```

### Code Quality

```bash
# Run linter
poetry run ruff check charcoal tests

# Run type checker
poetry run mypy charcoal

# Format code
poetry run black charcoal tests
```

## Project Status

This project is currently in early development as part of a TypeScript-to-Python migration. The initial milestone focuses on establishing the foundational infrastructure including:

- CLI framework with Click
- Configuration management with Pydantic
- Git operations abstraction
- Error handling framework

## Source

This is a Python reimplementation of the Graphite CLI originally written in TypeScript.

Source: https://github.com/Khachatour/charcoal-pr-stacking.git

## License

None
