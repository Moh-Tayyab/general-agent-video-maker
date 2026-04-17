---
name: python-code-style
description: >
  Python code quality — formatting, linting, type checking, naming conventions, and
  documentation standards. Use when: writing new Python code, refactoring, code review,
  fixing linting errors, setting up a new Python module, or questions about Python
  style. Conventions from CLAUDE.md: ruff (formatter/linter), mypy strict mode,
  Google-style docstrings, 120-char line length, Python 3.12+ minimum.
allowed-tools: Bash(ruff *), Bash(mypy *), Bash(python3 *)
---

# Python Code Style

Enforces: ruff + mypy strict mode + Google-style docstrings. Python 3.12+.

## The Two Tools

| Tool | Role | Invoked as |
|------|------|-----------|
| **ruff** | Format + lint (replaces flake8, isort, black) | `ruff check`, `ruff format` |
| **mypy** | Static type checking (strict mode) | `mypy --strict` |

## Ruff Quick Reference

```bash
# Check all Python files (recursive)
ruff check .

# Auto-fix what can be auto-fixed (imports, some rules)
ruff check . --fix

# Format code (like black, but faster)
ruff format .

# Check a specific file
ruff check path/to/file.py

# Show which rule is violated (e.g. E501 = line too long)
ruff check path/to/file.py --show-fixes --output-format=text
```

### Key Ruff Settings (pyproject.toml)

```toml
[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "I",     # isort (import sorting)
    "B",     # flake8-builtins
    "C4",    # flake8-comprehensions
    "UP",    # pyupgrade
    "SIM",   # flake8-simplify
    "RUF",   # ruff-specific rules
]
ignore = [
    "E501",  # line-length handled separately
    "B008",  # do not perform function calls in argument defaults
]
```

## mypy Quick Reference

```bash
# Check a module (--strict = all checks on)
mypy --strict path/to/module

# Check the whole project
mypy --strict .

# Check a single file
mypy --strict path/to/file.py

# Ignore missing imports (if stubs not installed)
mypy --strict --ignore-missing-imports .

# Report per-file
mypy --strict --namespace-packages --no-error-summary path/
```

### Key mypy Settings

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_ignores = true
ignore_missing_imports = false
namespace_packages = true
```

**Critical `--strict` flags used in this workspace:**

```
--check-untyped-defs   ← ALL functions must be typed (no body untyped)
--disallow-any-decorated ← don't allow Any return types on decorated funcs
--disallow-any-generics ← don't allow generic types with Any params
--disallow-subclassing-dict ← don't subclass dict
--disallow-untyped-defs  ← every def needs type annotations
--no-implicit-optional   ← must write Optional[X], not X | None without annotation
--warn-redundant-casts  ← catch redundant cast()
--warn-return-any        ← don't return Any from typed functions
--warn-unused-ignores    ← remove `# type: ignore` when no longer needed
```

## Naming Conventions

| What | Convention | Example |
|------|-----------|---------|
| Modules | `snake_case.py` | `video_bridge.py` |
| Classes | `PascalCase` | `CaptionBridge` |
| Functions | `snake_case` | `transcribe_audio()` |
| Variables | `snake_case` | `video_path` |
| Constants | `UPPER_SNAKE` | `MAX_DURATION` |
| Type variables | `PascalCase` | `T = TypeVar("T")` |
| Private attrs | `_snake_case` | `_cache` |
| Runtime type guard | `is_<type>` | `is_str_list(x)` |

**Never:**
- Single-letter variable names except in comprehensions / very short lambdas
- `my_list` / `temp_dict` / `data` / `result` — name for what it *is*
- CamelCase for anything except classes and type variables

## Google-Style Docstrings

Every function that is not trivial must have a docstring.

```python
def transcribe_audio(audio_path: str, project_id: str) -> STTResult:
    """Generate SRT captions from an audio file using ElevenLabs Scribe.

    Uses word-level timestamps from the Scribe API to generate karaoke-ready
    captions. Falls back to placeholder timing if STT is unavailable.

    Args:
        audio_path: Path to audio file (.wav, .mp3).
        project_id: Project folder name — output goes to WORKSPACE/<project_id>.

    Returns:
        STTResult with success flag, SRT path, and word timestamp array.

    Raises:
        FileNotFoundError: If audio_path does not exist.
        subprocess.TimeoutExpired: If STT times out (>120s).

    Example:
        >>> result = transcribe_audio("/tmp/vo.wav", "my-project")
        >>> print(result.srt_path)
        /home/user/bootlogix/production/output/my-project/captions.srt
    """
```

### Docstring Sections (in order)

1. **One-line summary** — what the function does (imperative: "Do X", not "Does X" or "X")
2. **Extended description** — only if needed for non-obvious behavior
3. **Args** — each arg on its own line, 4-space indent, `:param name: description`
4. **Returns** — `:returns:` or `:returns: description` — always note the type
5. **Raises** — list exceptions and when
6. **Example** — ````python >>> ... ```` block, only if it adds value

### What NOT to document

- Obvious: don't docstring `x = 1` or `self.items.append(item)` type one-liners
- Don't restate types already in the signature (mypy handles this)
- Don't add docstrings to `__init__` unless there's non-trivial initialization

## File Structure

Every Python module should be organized as:

```python
"""Module-level docstring: what this module provides."""

from __future__ import annotations

import os
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Private module-level state (if any)
_CACHE: dict[str, object] = {}


# ─── Public API ────────────────────────────────────────────────────────────────


@dataclass
class MyResult:
    success: bool
    path: str
    message: str


def do_something(path: str, project_id: str) -> MyResult:
    """One-line summary of what this does."""
    if not os.path.exists(path):
        return MyResult(False, "", f"File not found: {path}")
    # ... implementation
    return MyResult(True, output_path, "Done")


# ─── Private helpers ──────────────────────────────────────────────────────────


def _internal_helper(x: int) -> int:
    """Private helper — no external docs needed."""
    return x * 2
```

## Type Annotations

### Required everywhere — no exceptions

```python
# ✅ Correct
def add(x: int, y: int) -> int:
    return x + y

# ❌ Wrong — untyped def in typed codebase
def add(x, y):
    return x + y
```

### Generic types

```python
from typing import TypeVar, Generic

T = TypeVar("T")

# ❌ Wrong — bare list/dict without type param
def first(items: list) -> object: ...

# ✅ Correct
def first(items: list[T]) -> T: ...

# ❌ Wrong — bare Optional
def find(path: Optional[str]) -> str | None: ...

# ✅ Correct
def find(path: str | None) -> str | None:
    ...
```

### Callable and functools

```python
from typing import Callable

# Callback with specific signature
Callback = Callable[[int, str], bool]

def register(cb: Callback) -> None:
    ...
```

## Imports

```python
# Standard library first
from __future__ import annotations
import os
import logging
from typing import Optional

# Third-party (pip-installed)
from pydantic import BaseModel

# Local project
from production.bridges.captions import CaptionBridge

# Never:
# from production.bridges import *  (explicit imports only)
```

## Error Handling

```python
# ✅ Specific exceptions
def read_file(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path) as fh:
        return fh.read()

# ✅ Graceful degradation with known failure mode
def get_duration(video: str) -> float:
    try:
        cmd = [FFPROBE, "-v", "error", "-show_entries",
               "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video]
        return float(subprocess.check_output(cmd).decode().strip())
    except subprocess.CalledProcessError:
        return 0.0  # degrade gracefully

# ❌ Bare except — catches KeyboardInterrupt, SystemExit
try:
    something()
except:
    pass
```

## Async

```python
import asyncio
from collections.abc import AsyncIterator

async def stream_results(items: list[str]) -> AsyncIterator[str]:
    for item in items:
        await asyncio.sleep(0)  # yield control
        yield item
```

## Data Classes and Pydantic

Prefer `@dataclass` or Pydantic over raw dicts for structured return values:

```python
from dataclasses import dataclass

@dataclass
class UpscaleResult:
    success: bool
    output_path: str
    resolution: str
    message: str
```

For anything needing validation at runtime (API inputs, config), use Pydantic:

```python
from pydantic import BaseModel, Field

class UploadRequest(BaseModel):
    video_path: str = Field(..., description="Path to video file")
    title: str = Field(..., max_length=100)
    privacy: str = Field(default="public", pattern="^(public|unlisted|private)$")
```

## Logging

```python
import logging

logger = logging.getLogger(__name__)

def process_video(path: str) -> None:
    logger.info("Processing video: %s", path)
    logger.debug("Input params: duration=%s, size=%s", dur, size)
    try:
        result = _do_work(path)
        logger.info("Success: %s → %s", path, result.output_path)
    except Exception:
        logger.exception("Failed to process %s", path)  # includes traceback
        raise
```

## Testing Conventions

Tests go next to the code, not in a separate `tests/` directory (workspace convention):

```
production/bridges/
├── captions.py          ← source
├── captions_test.py    ← tests (NOT tests/test_captions.py)
```

## Ruff Lint Rules to Never Suppress

```python
# These rules catch real bugs — never ignore with noqa:
# E501 line-too-long       ← use line-length=120, split long lines instead
# F401 imported but unused ← remove unused imports
# F811 redefinition of name ← don't redefine builtins
# B008 do-not-call-with-mutable ← don't use mutable defaults (anti-pattern)
# UP035 deprecated import   ← use newer syntax
```

## Quick Validation Before Committing

```bash
# One-liner that checks everything
ruff check . --fix && ruff format . && mypy --strict .

# Per-file (faster during active editing)
ruff check path/to/file.py && mypy --strict path/to/file.py
```
