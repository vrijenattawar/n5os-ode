# n5OS-Ode Dependencies

## Python Requirements

**Python Version:** 3.10+

### Standard Library (No Installation Required)
- `argparse` - CLI argument parsing
- `sqlite3` - Database operations
- `json` - JSON handling
- `pathlib` - Path operations
- `datetime` - Date/time handling
- `re` - Regular expressions
- `hashlib` - Hashing functions
- `uuid` - UUID generation
- `logging` - Logging framework
- `subprocess` - Process execution
- `tempfile` - Temporary files
- `os`, `sys`, `shutil` - System operations

### Optional Dependencies
- `pyyaml` - YAML parsing (for `n5_load_context.py`)
  ```bash
  pip install pyyaml
  ```

## System Requirements

- **Editor:** nano (default) or any editor via `$EDITOR` env var
- **Shell:** bash-compatible shell
- **Filesystem:** Read/write access to `/home/workspace`

## Installation

```bash
# Install optional dependencies
pip install pyyaml

# Make scripts executable
chmod +x N5/scripts/*.py
```

## Database Files

Scripts automatically create SQLite databases in `N5/data/`:

| Database | Script | Purpose |
|----------|--------|---------|
| `journal.db` | `journal.py` | Journal entries |
| `content_library.db` | `content_ingest.py` | Content library |
| `conversations.db` | `session_state_manager.py` | Conversation tracking |

## Directory Setup

The following directories are auto-created as needed:

```
N5/
├── data/           # Databases
├── runtime/        # Logs and temporary files
│   └── runs/       # Run logs
Knowledge/
└── content-library/
    ├── articles/
    ├── papers/
    ├── decks/
    └── ...
```
