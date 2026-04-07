# python-code-style

**Hub group:** `mcp-development`
**Type:** Code style guide
**Entry:** `SKILL.md`

---

## What This Is

Python code style, linting, formatting, naming conventions, and documentation standards. Covers `ruff` + `mypy` setup, Google-style docstrings, and project documentation structure.

## Tooling

| Tool | Role |
|------|------|
| `ruff` | Linter + formatter (replaces flake8, isort, black) |
| `mypy` / `pyright` | Type checker |

## Quick Setup

```bash
pip install ruff mypy

# pyproject.toml
[tool.ruff]
line-length = 120
target-version = "py312"

[tool.mypy]
strict = true
```

## Naming Conventions

```python
# Files/modules: snake_case
user_repository.py
http_client.py

# Classes: PascalCase
class UserRepository:
class HTTPClientFactory:

# Functions/variables: snake_case
def get_user_by_email(email: str) -> User | None:
    retry_count = 3

# Constants: SCREAMING_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
API_BASE_URL = "https://api.example.com"
```

## Import Order

```python
# 1. Standard library
import os
from collections.abc import Callable
from typing import Any

# 2. Third-party
import httpx
from pydantic import BaseModel

# 3. Local
from myproject.models import User
```

## Docstring Style (Google)

```python
def process_batch(
    items: list[Item],
    max_workers: int = 4,
    on_progress: Callable[[int, int], None] | None = None,
) -> BatchResult:
    """Process items concurrently using a worker pool.

    Processes each item in the batch using the configured number of
    workers. Progress can be monitored via the optional callback.

    Args:
        items: The items to process. Must not be empty.
        max_workers: Maximum concurrent workers. Defaults to 4.
        on_progress: Optional callback receiving (completed, total) counts.

    Returns:
        BatchResult containing succeeded items and any failures.

    Raises:
        ValueError: If items is empty.
        ProcessingError: If the batch cannot be processed.
    """
```

## Integration Points

| Connected Skill | How |
|-----------------|-----|
| `mcp-builder` | Follow these conventions when building Python MCP servers |
| `javascript-typescript-jest` | Both are code quality guides — use alongside each other |

## CI Integration

```bash
# Run on every commit
ruff check --fix .
ruff format .
mypy .
```
