---
description: |
  Orchestrate a multi-worker build project.
  
  The LLM defines the build plan with workers, dependencies, and context.
  The script handles tracking, status, and generating spawn commands.
  
  **Initialize:** Define plan as JSON, then init
  **Track:** Check status, get ready workers, mark complete
  **Spawn:** Generate spawn commands with full context
tool: true
tags:
  - build
  - orchestration
  - workers
  - parallel
---

# Build Orchestrator

## Workflow

### 1. Define Your Build Plan (LLM Does This)

Create a JSON plan with:
- Project name and objective
- Workers with dependencies
- Key decisions and relevant files

```json
{
  "name": "Authentication System",
  "description": "Implement OAuth2 + SSO for N5 services",
  "objective": "Secure, user-friendly authentication with provider flexibility",
  "key_decisions": [
    "SQLite for credential storage",
    "JWT for sessions",
    "Support Google, GitHub, custom OIDC"
  ],
  "relevant_files": [
    "N5/services/auth/README.md",
    "N5/schemas/auth.sql"
  ],
  "workers": [
    {
      "id": "worker_schema",
      "component": "database_schema",
      "description": "Create SQLite schema for users, sessions, providers",
      "dependencies": [],
      "estimated_hours": 2
    },
    {
      "id": "worker_oauth",
      "component": "oauth_flow",
      "description": "Implement OAuth2 authorization code flow",
      "dependencies": ["worker_schema"],
      "estimated_hours": 4
    },
    {
      "id": "worker_jwt",
      "component": "jwt_sessions",
      "description": "JWT token generation and validation",
      "dependencies": ["worker_schema"],
      "estimated_hours": 3
    },
    {
      "id": "worker_providers",
      "component": "provider_config",
      "description": "Google, GitHub, custom OIDC provider support",
      "dependencies": ["worker_oauth"],
      "estimated_hours": 3
    }
  ]
}
```

### 2. Initialize the Project

```bash
# Save plan to file first, or use inline
python3 N5/scripts/build_orchestrator_v2.py init \
    --project auth-system \
    --plan-file /path/to/plan.json
```

### 3. Check What's Ready

```bash
python3 N5/scripts/build_orchestrator_v2.py ready --project auth-system
```

Returns workers whose dependencies are met.

### 4. Spawn Workers

```bash
# Get spawn command for a ready worker
python3 N5/scripts/build_orchestrator_v2.py spawn-cmd \
    --project auth-system \
    --worker worker_schema \
    --parent con_XXXXX
```

This generates a `spawn_worker_v2.py` command with full context.

### 5. Mark Complete

When a worker finishes:

```bash
python3 N5/scripts/build_orchestrator_v2.py complete \
    --project auth-system \
    --worker worker_schema \
    --output "N5/services/auth/schema.sql"
```

### 6. Check Overall Status

```bash
python3 N5/scripts/build_orchestrator_v2.py status --project auth-system
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `init --project X --plan-file Y` | Start new project |
| `status --project X` | Show all workers and status |
| `ready --project X` | Show workers ready to spawn |
| `complete --project X --worker Y` | Mark worker done |
| `spawn-cmd --project X --worker Y --parent Z` | Get spawn command |
| `list` | List all projects |

## Project Data

Projects are stored in `N5/builds/{project}/`:
- `plan.json` - Full plan with worker status
- `README.md` - Auto-generated overview

## Tips

1. **Start with ready workers** - Check `ready` to see what can be parallelized
2. **Update frequently** - Mark workers complete so dependent workers become ready
3. **The LLM drives everything** - Plan definition, spawning decisions, context
4. **Script just tracks** - No AI in the script, just state management

## Spawning Workers via /zo/ask API

When spawning workers using the `/zo/ask` API, **always use fire-and-forget with file-based results**:

```python
#!/usr/bin/env python3
"""Spawn workers via /zo/ask - fire and forget pattern."""
import asyncio
import aiohttp
import os
import json
from pathlib import Path

RESULTS_FILE = Path("/home/workspace/N5/builds/{project}/spawn_results.jsonl")

async def spawn_worker(session, worker_id: str, assignment_content: str):
    """Spawn a single worker and write result to file."""
    try:
        async with session.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
                "content-type": "application/json"
            },
            json={"input": assignment_content},
            timeout=aiohttp.ClientTimeout(total=600)  # 10 min timeout per worker
        ) as resp:
            result = await resp.json()
            return {"worker_id": worker_id, "status": "completed", "conversation_id": result.get("conversation_id"), "output_preview": result.get("output", "")[:500]}
    except asyncio.TimeoutError:
        return {"worker_id": worker_id, "status": "timeout", "error": "Worker timed out after 10 minutes"}
    except Exception as e:
        return {"worker_id": worker_id, "status": "error", "error": str(e)}

async def main():
    # Load worker assignments from build directory
    workers = [...] # Your worker definitions
    
    async with aiohttp.ClientSession() as session:
        tasks = [spawn_worker(session, w["id"], w["content"]) for w in workers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Write results to file (not stdout) so they persist even if parent times out
    with open(RESULTS_FILE, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    
    print(f"Results written to {RESULTS_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Key Pattern: Fire-and-Forget with Polling

**DO NOT** wait for spawn script to complete in a blocking tool call. Instead:

1. **Write spawn script** to conversation workspace
2. **Run with nohup**: `nohup python3 spawn_workers.py > /dev/null 2>&1 &`
3. **Return immediately** to user: "Workers spawned. Check `N5/builds/{project}/spawn_results.jsonl` for status."
4. **Poll later** or let user trigger status check

This prevents tool timeouts from losing worker results.

### Why This Matters

- `/zo/ask` spawns can take 5-15 minutes per worker
- Zo tool runner has its own timeout
- If the tool times out, you lose visibility into what happened
- File-based results persist regardless of parent timeout


