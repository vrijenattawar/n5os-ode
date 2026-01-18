---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: worker_009_sites_protocol
---

# Sites Protocol

This document defines how web-shaped apps (sites) are created, organized, and deployed on a Zo workspace.

## Core Principle

**Staging is source of truth. Production is deployment output only.**

All code edits happen in staging. Production is a deployment copy, never edited directly.

---

## 1. Canonical Locations

All web apps must live under `Sites/`.

### Directory Pattern

Each site uses a **kebab-case slug** (e.g., `my-dashboard`, `task-tracker`).

```
Sites/
├── <slug>/                 # Production (deployment output)
└── <slug>-staging/         # Staging (source of truth for edits)
```

### Examples

```
Sites/
├── my-dashboard/
├── my-dashboard-staging/
├── task-tracker/
└── task-tracker-staging/
```

### Inbox Snapshots

Inbox copies like `Inbox/2025..._<slug>/` are **snapshots only**, never canonical. Always move to the proper `Sites/` location.

---

## 2. Service Conventions

### Production Services

Each production site has a user service:

| Property | Value |
|----------|-------|
| **Label** | `<slug>` |
| **Workdir** | `Sites/<slug>` |
| **Entrypoint** | `bun run prod` (or framework-specific) |
| **Port** | From `zosite.json.publish.published_port` or explicit config |

### Staging Services (Optional)

Staging may have its own service for development:

| Property | Value |
|----------|-------|
| **Label** | `<slug>-staging` |
| **Workdir** | `Sites/<slug>-staging` |
| **Entrypoint** | `bun run dev` |
| **Port** | **Must differ** from production |

If the app supports `process.env.PORT`, staging sets `PORT` to its own port.

### Example

For a site with slug `my-dashboard`:

- **Prod:** `Sites/my-dashboard/` ← service `my-dashboard` on port `50171`
- **Staging:** `Sites/my-dashboard-staging/` ← service `my-dashboard-staging` on port `50172`

---

## 3. Creation Protocol

When creating a new site:

1. **Choose a slug** in kebab-case (e.g., `new-site-demo`).
2. **Scaffold under Sites:**
   - Use Zo's site creation so code lands at `Sites/<slug>/` **or** `Sites/<slug>-staging/`.
   - Never create sites at the workspace root.
3. **Add `zosite.json`** under the site root:
   ```json
   {
     "name": "<slug>",
     "local_port": <dev_port>,
     "publish": {
       "entrypoint": "<start_command>",
       "published_port": <prod_port>
     }
   }
   ```
4. **Register production service** to point at `Sites/<slug>`.

---

## 4. Staging vs Production Workflow

### The Golden Rule

- **Staging** (`Sites/<slug>-staging/`) is the **source of truth for code edits**.
- **Production** (`Sites/<slug>/`) is a **deployment copy**, not edited directly.

### Normal Flow

1. Edit code in staging.
2. Verify behavior via the staging service/URL.
3. When ready, promote staging → prod using the promotion flow.

### Reset Scenario

If staging becomes too messy, it can be reset from production by copying prod back into staging. This should be done intentionally.

---

## 5. Promotion Flow (Staging → Prod)

Promotion updates production code to match staging.

### High-Level Steps

1. **Pre-checks**
   - Ensure both `Sites/<slug>` and `Sites/<slug>-staging` exist.
   - Optionally run protection checks if your system has them.

2. **Sync Code**
   - Copy from `Sites/<slug>-staging/` into `Sites/<slug>/`.
   - Exclude `node_modules/` and other environment-specific directories.
   - Delete files in prod that were removed in staging (clean sync).

3. **Restart Production Service**
   - Restart the user service labeled `<slug>` so it picks up the new code.

### Helper Script Pattern

For convenience, use a helper script for promotion:

```bash
# Dry-run to see what would change
bash promote_site.sh <slug> --dry-run

# Actual promotion (staging → prod)
bash promote_site.sh <slug>
```

**Expected behavior:**
- Syncs `Sites/<slug>-staging/` → `Sites/<slug>/` using rsync
- Excludes `node_modules/`
- Supports `--dry-run` to preview changes
- Prints a reminder to restart the `<slug>` service afterwards

---

## 6. Protection Rules

### Global Protection

- `Sites/.n5protected` marks the entire Sites tree as protected.

### Per-Site Protection

Critical sites can have their own `.n5protected` files:

```
Sites/
├── .n5protected
├── my-dashboard/
│   └── .n5protected
└── my-dashboard-staging/
    └── .n5protected
```

### Operational Rules

- No agent or script should move or delete anything under `Sites/**` without explicit confirmation.
- If a site-shaped directory (contains `zosite.json` and `package.json`) is detected **outside** `Sites/`, it is considered misfiled and should be relocated into `Sites/<slug>-staging` or `Sites/<slug>`.

---

## 7. Future Integration (Optional)

### Git/GitHub Integration

Git can be layered on for version control:

- `Sites/<slug>-staging` as the primary working copy tied to a Git repo.
- `Sites/<slug>` as a deployment copy synced from a specific branch/commit.

### Delta Analysis

Git tools can then summarize changes before promotion:
- `git diff` to see what changed
- Branch-based deployment workflow
- Rollback capabilities

---

## Summary

| Concept | Rule |
|---------|------|
| **Location** | All sites under `Sites/` only |
| **Naming** | Kebab-case slugs with `-staging` suffix for dev |
| **Source of Truth** | Staging is where you edit |
| **Production** | Deployment output, never edited directly |
| **Promotion** | Use `promote_site.sh` to sync staging → prod |
| **Protection** | Sites tree is protected from accidental moves/deletes |