#!/usr/bin/env python3
"""
Build Orchestrator v2 - LLM-Driven Project Coordination

The LLM defines the build plan and worker breakdown.
This script handles:
1. Storing the build plan
2. Tracking worker status
3. Identifying ready workers (dependencies met)
4. Generating spawn commands

Usage:
    # Initialize a build with LLM-provided plan
    python3 build_orchestrator_v2.py init --project "my-project" --plan-file plan.json
    
    # Check status
    python3 build_orchestrator_v2.py status --project "my-project"
    
    # Get ready workers (can be spawned)
    python3 build_orchestrator_v2.py ready --project "my-project"
    
    # Mark worker complete
    python3 build_orchestrator_v2.py complete --project "my-project" --worker worker_schema
    
    # Generate spawn command for a worker
    python3 build_orchestrator_v2.py spawn-cmd --project "my-project" --worker worker_schema --parent con_XXX
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from N5.lib.paths import N5_BUILDS_DIR
    ORCHESTRATION_DIR = N5_BUILDS_DIR
except ImportError:
    ORCHESTRATION_DIR = Path("/home/workspace/N5/builds")


def get_project_dir(project: str) -> Path:
    """Get the directory for a project's orchestration data."""
    return ORCHESTRATION_DIR / project


def init_project(project: str, plan: dict) -> dict:
    """Initialize a new build project with LLM-provided plan."""
    project_dir = get_project_dir(project)
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Store the plan
    plan_file = project_dir / "plan.json"
    
    # Add metadata
    plan["_meta"] = {
        "project": project,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "active"
    }
    
    # Initialize worker statuses
    for worker in plan.get("workers", []):
        worker["status"] = worker.get("status", "pending")
        worker["completed_at"] = None
        worker["spawned_conversation"] = None
    
    plan_file.write_text(json.dumps(plan, indent=2))
    
    # Create a markdown overview
    overview = generate_overview_md(plan)
    (project_dir / "README.md").write_text(overview)
    
    return {
        "success": True,
        "project": project,
        "workers_count": len(plan.get("workers", [])),
        "project_dir": str(project_dir)
    }


def generate_overview_md(plan: dict) -> str:
    """Generate a markdown overview of the build plan."""
    md = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
last_edited: {datetime.now().strftime('%Y-%m-%d')}
version: 1.0
---

# {plan.get('name', 'Build Project')}

{plan.get('description', '')}

## Objective

{plan.get('objective', 'Not specified')}

## Workers

| ID | Component | Status | Dependencies | Est. Hours |
|----|-----------|--------|--------------|------------|
"""
    
    for w in plan.get("workers", []):
        deps = ", ".join(w.get("dependencies", [])) or "-"
        hours = w.get("estimated_hours", "?")
        md += f"| {w['id']} | {w['component']} | {w.get('status', 'pending')} | {deps} | {hours}h |\n"
    
    md += f"""
## Key Decisions

"""
    for decision in plan.get("key_decisions", []):
        md += f"- {decision}\n"
    
    md += f"""
## Relevant Files

"""
    for f in plan.get("relevant_files", []):
        md += f"- `{f}`\n"
    
    return md


def load_plan(project: str) -> dict:
    """Load the plan for a project."""
    plan_file = get_project_dir(project) / "plan.json"
    if not plan_file.exists():
        return None
    return json.loads(plan_file.read_text())


def save_plan(project: str, plan: dict):
    """Save the plan for a project."""
    plan_file = get_project_dir(project) / "plan.json"
    plan_file.write_text(json.dumps(plan, indent=2))


def get_status(project: str) -> dict:
    """Get current status of all workers."""
    plan = load_plan(project)
    if not plan:
        return {"error": f"Project '{project}' not found"}
    
    workers = plan.get("workers", [])
    
    status_counts = {"pending": 0, "in_progress": 0, "review_pending": 0, "completed": 0, "blocked": 0}
    for w in workers:
        status_counts[w.get("status", "pending")] = status_counts.get(w.get("status", "pending"), 0) + 1
    
    return {
        "project": project,
        "name": plan.get("name"),
        "total_workers": len(workers),
        "status_counts": status_counts,
        "workers": workers
    }


def get_ready_workers(project: str) -> dict:
    """Get workers whose dependencies are met and can be spawned."""
    plan = load_plan(project)
    if not plan:
        return {"error": f"Project '{project}' not found"}
    
    workers = {w["id"]: w for w in plan.get("workers", [])}
    
    ready = []
    for worker in workers.values():
        if worker.get("status") == "pending":
            # Check if all dependencies are complete
            deps_complete = all(
                workers.get(dep, {}).get("status") == "completed"
                for dep in worker.get("dependencies", [])
            )
            if deps_complete:
                ready.append(worker)
    
    return {
        "project": project,
        "ready_count": len(ready),
        "ready_workers": ready
    }


def mark_complete(project: str, worker_id: str, output_path: str = None) -> dict:
    """Mark a worker as complete."""
    plan = load_plan(project)
    if not plan:
        return {"error": f"Project '{project}' not found"}
    
    for w in plan.get("workers", []):
        if w["id"] == worker_id:
            w["status"] = "completed"
            w["completed_at"] = datetime.now(timezone.utc).isoformat()
            if output_path:
                w["output_path"] = output_path
            save_plan(project, plan)
            
            # Update README
            overview = generate_overview_md(plan)
            (get_project_dir(project) / "README.md").write_text(overview)
            
            return {
                "success": True,
                "worker_id": worker_id,
                "status": "completed"
            }
    
    return {"error": f"Worker '{worker_id}' not found"}


def submit_work(project: str, worker_id: str, files: str, summary: str) -> dict:
    """Submit work for review (Worker -> Orchestrator)."""
    plan = load_plan(project)
    if not plan:
        return {"error": f"Project '{project}' not found"}
    
    for w in plan.get("workers", []):
        if w["id"] == worker_id:
            w["status"] = "review_pending"
            w["submitted_at"] = datetime.now(timezone.utc).isoformat()
            w["submitted_files"] = files
            w["submitted_summary"] = summary
            save_plan(project, plan)
            
            # Update README
            overview = generate_overview_md(plan)
            (get_project_dir(project) / "README.md").write_text(overview)
            
            return {"success": True, "status": "review_pending"}
    
    return {"error": f"Worker '{worker_id}' not found"}


def list_reviews(project: str) -> dict:
    """List workers waiting for review."""
    plan = load_plan(project)
    if not plan:
        return {"error": f"Project '{project}' not found"}
    
    pending = [w for w in plan.get("workers", []) if w.get("status") == "review_pending"]
    return {"project": project, "pending_reviews": len(pending), "reviews": pending}


def approve_work(project: str, worker_id: str) -> dict:
    """Approve submitted work (transition review_pending -> completed)."""
    # This is effectively mark_complete but semantically distinct
    return mark_complete(project, worker_id)


def generate_spawn_command(project: str, worker_id: str, parent_id: str) -> dict:
    """Generate copy-paste spawn instructions with BUILD_CONTEXT for a worker.
    
    Returns instructions that can be pasted into a new conversation to spawn
    the worker with proper build context for tracking.
    """
    plan = load_plan(project)
    if not plan:
        return {"error": f"Project '{project}' not found"}
    
    worker = None
    for w in plan.get("workers", []):
        if w["id"] == worker_id:
            worker = w
            break
    
    if not worker:
        return {"error": f"Worker '{worker_id}' not found"}
    
    # Extract worker number from id (e.g., "worker_1" -> 1, or just "1" -> 1)
    worker_num = worker_id
    if worker_id.startswith("worker_"):
        worker_num = worker_id.replace("worker_", "")
    
    # Build the spawn instructions with BUILD_CONTEXT
    project_name = plan.get("name", project)
    component = worker.get("component", worker_id)
    description = worker.get("description", f"Complete {component}")
    relevant_files = worker.get("relevant_files", plan.get("relevant_files", []))
    dependencies = worker.get("dependencies", [])
    
    files_list = "\n".join(f"- `file '{f}'`" for f in relevant_files) if relevant_files else "- See DESIGN.md"
    deps_note = f"Dependencies: {', '.join(dependencies)}" if dependencies else "No dependencies"
    
    instructions = f"""Execute Worker {worker_num} ({component}):

BUILD_CONTEXT:
  build: {project}
  worker: {worker_num}
  parent_topic: {project_name}

CONTEXT:
{deps_note}
Relevant files:
{files_list}

INSTRUCTIONS:
- Read: `file 'N5/builds/{project}/DESIGN.md'`
- Read: `file 'N5/builds/{project}/PLAN.md'`

DELIVERABLES:
{description}

When complete:
1. Update `file 'N5/builds/{project}/STATUS.md'` with results
2. Run close conversation workflow (will auto-notify orchestrator)
"""
    
    return {
        "worker_id": worker_id,
        "worker_num": worker_num,
        "component": component,
        "instructions": instructions,
        "note": "Copy and paste these instructions into a new conversation to spawn the worker"
    }


def list_projects() -> dict:
    """List all orchestration projects."""
    if not ORCHESTRATION_DIR.exists():
        return {"projects": []}
    
    projects = []
    for d in ORCHESTRATION_DIR.iterdir():
        if d.is_dir() and (d / "plan.json").exists():
            plan = json.loads((d / "plan.json").read_text())
            projects.append({
                "project": d.name,
                "name": plan.get("name"),
                "status": plan.get("_meta", {}).get("status", "unknown"),
                "workers": len(plan.get("workers", []))
            })
    
    return {"projects": projects}


def main():
    parser = argparse.ArgumentParser(description="Build Orchestrator v2")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new build project")
    init_parser.add_argument("--project", required=True, help="Project identifier")
    init_parser.add_argument("--plan-file", help="Path to JSON plan file")
    init_parser.add_argument("--plan", help="Inline JSON plan")
    
    # status
    status_parser = subparsers.add_parser("status", help="Get project status")
    status_parser.add_argument("--project", required=True)
    
    # ready
    ready_parser = subparsers.add_parser("ready", help="Get workers ready to spawn")
    ready_parser.add_argument("--project", required=True)
    
    # complete
    complete_parser = subparsers.add_parser("complete", help="Mark worker complete")
    complete_parser.add_argument("--project", required=True)
    complete_parser.add_argument("--worker", required=True)
    complete_parser.add_argument("--output", help="Path to worker output")    # submit (used by worker)
    submit_parser = subparsers.add_parser("submit", help="Submit worker output for review")
    submit_parser.add_argument("--project", required=True)
    submit_parser.add_argument("--worker", required=True)
    submit_parser.add_argument("--files", help="Created files")
    submit_parser.add_argument("--summary", help="Work summary")

    # review (used by operator)
    review_parser = subparsers.add_parser("review", help="Review pending submissions")
    review_parser.add_argument("--project", required=True)

    # approve (used by operator)
    approve_parser = subparsers.add_parser("approve", help="Approve submitted work")
    approve_parser.add_argument("--project", required=True)
    approve_parser.add_argument("--worker", required=True)
    
    # spawn-cmd
    spawn_parser = subparsers.add_parser("spawn-cmd", help="Generate spawn command")
    spawn_parser.add_argument("--project", required=True)
    spawn_parser.add_argument("--worker", required=True)
    spawn_parser.add_argument("--parent", required=True, help="Parent conversation ID")
    
    # list
    subparsers.add_parser("list", help="List all projects")
    
    args = parser.parse_args()
    
    if args.command == "init":
        if args.plan_file:
            plan = json.loads(Path(args.plan_file).read_text())
        elif args.plan:
            plan = json.loads(args.plan)
        else:
            print("Error: --plan-file or --plan required", file=sys.stderr)
            return 1
        result = init_project(args.project, plan)
    
    elif args.command == "status":
        result = get_status(args.project)
    
    elif args.command == "ready":
        result = get_ready_workers(args.project)
    
    elif args.command == "complete":
        result = mark_complete(args.project, args.worker, args.output)
    
    elif args.command == "submit":
        result = submit_work(args.project, args.worker, args.files, args.summary)
    
    elif args.command == "review":
        result = list_reviews(args.project)
        
    elif args.command == "approve":
        result = approve_work(args.project, args.worker)
    
    elif args.command == "spawn-cmd":
        result = generate_spawn_command(args.project, args.worker, args.parent)
    
    elif args.command == "list":
        result = list_projects()
    
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())




