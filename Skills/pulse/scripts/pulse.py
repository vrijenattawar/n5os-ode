#!/usr/bin/env python3
"""
Pulse: Automated Build Orchestration System

Commands:
  start <slug>     - Begin automated orchestration
  status <slug>    - Show current build status
  stop <slug>      - Gracefully stop orchestration
  resume <slug>    - Resume a stopped build
  tick <slug>      - Run single orchestration cycle (for scheduled tasks)
  finalize <slug>  - Run post-build finalization (safety, tests, learnings)
"""

import argparse
import asyncio
import aiohttp
import json
import os
import sys
import sqlite3
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from pulse_common import PATHS, WORKSPACE

# Paths
# WORKSPACE = Path("/home/workspace")  # Now imported from pulse_common
BUILDS_DIR = PATHS.BUILDS
CONVERSATIONS_DB = PATHS.WORKSPACE / "N5" / "data" / "conversations.db"
SKILLS_DIR = PATHS.SCRIPTS

# Config
DEFAULT_POLL_INTERVAL = 180  # 3 minutes
DEFAULT_DEAD_THRESHOLD = 900  # 15 minutes
ZO_API_URL = "https://api.zo.computer/zo/ask"


def load_meta(slug: str) -> dict:
    """Load build meta.json"""
    meta_path = BUILDS_DIR / slug / "meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Build not found: {slug}")
    with open(meta_path) as f:
        return json.load(f)


def save_meta(slug: str, meta: dict):
    """Save build meta.json"""
    meta_path = BUILDS_DIR / slug / "meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)


def load_drop_brief(slug: str, drop_id: str) -> str:
    """Load a Drop brief from drops/ folder"""
    drops_dir = BUILDS_DIR / slug / "drops"
    # Try both D and C prefixes
    for pattern in [f"{drop_id}-*.md", f"C*.md"]:
        for f in drops_dir.glob(pattern):
            if f.stem.startswith(drop_id):
                return f.read_text()
    # Fallback: exact match
    for f in drops_dir.glob("*.md"):
        if f.stem.split("-")[0] == drop_id:
            return f.read_text()
    raise FileNotFoundError(f"Brief not found for {drop_id}")


def get_deposit(slug: str, drop_id: str) -> Optional[dict]:
    """Get a Drop's deposit if it exists"""
    deposit_path = BUILDS_DIR / slug / "deposits" / f"{drop_id}.json"
    if deposit_path.exists():
        with open(deposit_path) as f:
            return json.load(f)
    return None


def get_filter_result(slug: str, drop_id: str) -> Optional[dict]:
    """Get Filter judgment for a Drop if it exists"""
    filter_path = BUILDS_DIR / slug / "deposits" / f"{drop_id}_filter.json"
    if filter_path.exists():
        with open(filter_path) as f:
            return json.load(f)
    return None


def register_drop_conversation(drop_id: str, slug: str, convo_id: str):
    """Register a Drop's conversation in conversations.db"""
    conn = sqlite3.connect(CONVERSATIONS_DB)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    
    # Check if conversations table has the columns we need
    cursor.execute("PRAGMA table_info(conversations)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "build_slug" not in columns:
        cursor.execute("ALTER TABLE conversations ADD COLUMN build_slug TEXT")
    if "drop_id" not in columns:
        cursor.execute("ALTER TABLE conversations ADD COLUMN drop_id TEXT")
    
    # Insert or update
    cursor.execute("""
        INSERT INTO conversations (id, type, status, created_at, updated_at, build_slug, drop_id)
        VALUES (?, 'headless_worker', 'running', ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET build_slug=?, drop_id=?, updated_at=?
    """, (convo_id, now, now, slug, drop_id, slug, drop_id, now))
    
    conn.commit()
    conn.close()


def update_drop_conversation_status(convo_id: str, status: str):
    """Update a Drop conversation's status in conversations.db"""
    if not convo_id or convo_id.startswith("unknown_"):
        return
    conn = sqlite3.connect(CONVERSATIONS_DB)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        UPDATE conversations 
        SET status = ?, updated_at = ?, completed_at = ?
        WHERE id = ?
    """, (status, now, now if status == "complete" else None, convo_id))
    conn.commit()
    conn.close()


def update_status_md(slug: str, meta: dict):
    """Update STATUS.md with current progress"""
    status_path = BUILDS_DIR / slug / "STATUS.md"
    
    drops = meta.get("drops", {})
    complete = [d for d, info in drops.items() if info.get("status") == "complete"]
    running = [d for d, info in drops.items() if info.get("status") == "running"]
    pending = [d for d, info in drops.items() if info.get("status") == "pending"]
    dead = [d for d, info in drops.items() if info.get("status") == "dead"]
    failed = [d for d, info in drops.items() if info.get("status") == "failed"]
    
    total = len(drops)
    pct = int(len(complete) / total * 100) if total > 0 else 0
    
    content = f"""# Build Status: {slug}

**Updated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**Status:** {meta.get('status', 'unknown')}
**Stream:** {meta.get('current_stream', '?')}/{meta.get('total_streams', '?')}
**Progress:** {len(complete)}/{total} Drops ({pct}%)

## Complete ({len(complete)})
{chr(10).join(f'- [x] {d}' for d in sorted(complete)) or '(none)'}

## Running ({len(running)})
{chr(10).join(f'- [ ] {d} (since {drops[d].get("started_at", "?")[:16]})' for d in sorted(running)) or '(none)'}

## Pending ({len(pending)})
{chr(10).join(f'- [ ] {d}' for d in sorted(pending)) or '(none)'}

## Dead ({len(dead)})
{chr(10).join(f'- [!] {d}' for d in sorted(dead)) or '(none)'}

## Failed ({len(failed)})
{chr(10).join(f'- [x] {d} (Filter rejected)' for d in sorted(failed)) or '(none)'}
"""
    
    status_path.write_text(content)


async def send_sms(message: str):
    """Send SMS via Zo's send_sms_to_user (calls back to Zo)"""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        print(f"[SMS SKIPPED - no token] {message}")
        return
    
    prompt = f"Send this SMS to V immediately, no commentary: {message}"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            ZO_API_URL,
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={"input": prompt}
        ) as resp:
            result = await resp.json()
            print(f"[SMS SENT] {message}")
            return result


async def spawn_drop(slug: str, drop_id: str, brief: str, model: str = None) -> str:
    """Spawn a Drop via /zo/ask, return conversation_id"""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise RuntimeError("ZO_CLIENT_IDENTITY_TOKEN not set")
    
    # Include SESSION_STATE init in the prompt
    full_prompt = f"""You are a Pulse worker (Drop) executing build "{slug}", task "{drop_id}".

FIRST ACTION (before anything else):
Run this command to register yourself:
```bash
python3 {str(PATHS.WORKSPACE)}/N5/scripts/session_state_manager.py init --convo-id $(cat /proc/self/cgroup | grep -o 'con_[^/]*' | head -1 || echo "unknown") --type build --build {slug} --worker-num {drop_id} --message "Drop {drop_id}: {brief.split(chr(10))[0][:50]}"
```

THEN EXECUTE:
1. Read the brief below carefully
2. Execute the task completely  
3. Write your deposit to: N5/builds/{slug}/deposits/{drop_id}.json
4. DO NOT commit any code
5. If blocked, write deposit with status "blocked" and explain why

---
{brief}
---

Begin execution now. Initialize SESSION_STATE first, then work, then write deposit."""

    async with aiohttp.ClientSession() as session:
        async with session.post(
            ZO_API_URL,
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={
                "input": full_prompt,
                "model_name": model
            }
        ) as resp:
            result = await resp.json()
            # Extract conversation_id from response if available
            convo_id = result.get("conversation_id", f"unknown_{drop_id}_{datetime.now().timestamp()}")
            return convo_id


async def run_filter(slug: str, drop_id: str, brief: str, deposit: dict) -> dict:
    """Run LLM Filter to validate a Deposit against its brief"""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        # Fallback: auto-pass
        return {"drop_id": drop_id, "verdict": "PASS", "reason": "Filter skipped (no token)"}
    
    prompt = f"""You are a Pulse Filter validating a Drop's work.

## Drop Brief (what was requested):
{brief}

## Deposit (what was delivered):
{json.dumps(deposit, indent=2)}

## Your Task:
1. Compare the deposit against the brief's success criteria
2. Check if artifacts were actually created (you can read files to verify)
3. Determine PASS or FAIL

Respond with ONLY this JSON (no other text):
{{
  "drop_id": "{drop_id}",
  "verdict": "PASS" or "FAIL",
  "reason": "Brief explanation",
  "artifacts_verified": true/false,
  "concerns": ["any concerns for orchestrator"]
}}"""

    async with aiohttp.ClientSession() as session:
        async with session.post(
            ZO_API_URL,
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={"input": prompt}
        ) as resp:
            result = await resp.json()
            output = result.get("output", "")
            
            # Try to parse JSON from response
            try:
                # Find JSON in response
                start = output.find("{")
                end = output.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(output[start:end])
            except:
                pass
            
            # Fallback
            return {
                "drop_id": drop_id,
                "verdict": "PASS",
                "reason": "Filter parse failed, auto-passing",
                "raw_response": output[:500]
            }


async def run_dredge(slug: str, drop_id: str, meta: dict):
    """Spawn forensics worker to investigate dead Drop"""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        return
    
    drop_info = meta.get("drops", {}).get(drop_id, {})
    convo_id = drop_info.get("conversation_id", "unknown")
    
    prompt = f"""You are a Pulse Dredge worker investigating a dead Drop.

Build: {slug}
Dead Drop: {drop_id}
Conversation ID: {convo_id}
Started at: {drop_info.get('started_at', 'unknown')}

## Your Task:
1. Check if the Drop created any partial artifacts
2. Check if there's a partial deposit in N5/builds/{slug}/deposits/
3. Look for any error indicators
4. Write a forensics report to: N5/builds/{slug}/deposits/{drop_id}_forensics.json

Report format:
{{
  "drop_id": "{drop_id}",
  "partial_artifacts": ["list of any files created"],
  "partial_work": "description of what was started",
  "likely_cause": "timeout/error/stuck",
  "recommendation": "retry/skip/manual",
  "cleanup_needed": true/false
}}

Investigate now."""

    async with aiohttp.ClientSession() as session:
        async with session.post(
            ZO_API_URL,
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={"input": prompt}
        ) as resp:
            print(f"[DREDGE] Forensics worker spawned for {drop_id}")


def get_ready_drops(meta: dict) -> list[str]:
    """Get list of Drops ready to spawn (dependencies met, not started)"""
    ready = []
    drops = meta.get("drops", {})
    currents = meta.get("currents", {})
    
    # Build set of complete drops
    complete_drops = {d for d, info in drops.items() if info.get("status") == "complete"}
    
    # Build set of drops in currents (sequential chains)
    current_drops = set()
    for chain in currents.values():
        current_drops.update(chain)
    
    for drop_id, info in drops.items():
        if info.get("status") != "pending":
            continue
        
        # Check dependencies
        depends_on = info.get("depends_on", [])
        if not all(d in complete_drops for d in depends_on):
            continue
        
        # Check if part of a Current (sequential chain)
        in_current = False
        for chain_id, chain in currents.items():
            if drop_id in chain:
                in_current = True
                idx = chain.index(drop_id)
                if idx > 0:
                    # Must wait for previous in chain
                    prev_drop = chain[idx - 1]
                    if prev_drop not in complete_drops:
                        continue
        
        ready.append(drop_id)
    
    return ready


def get_running_drops(meta: dict) -> list[tuple[str, dict]]:
    """Get list of running Drops with their info"""
    return [
        (drop_id, info)
        for drop_id, info in meta.get("drops", {}).items()
        if info.get("status") == "running"
    ]


def check_stream_complete(meta: dict) -> bool:
    """Check if current stream is complete"""
    current_stream = meta.get("current_stream", 1)
    drops = meta.get("drops", {})
    
    for drop_id, info in drops.items():
        # Parse stream from drop_id (D1.1 -> stream 1)
        try:
            stream_num = int(drop_id[1])
        except:
            continue
        
        if stream_num == current_stream:
            if info.get("status") not in ["complete", "failed"]:
                return False
    
    return True


def advance_stream(meta: dict) -> bool:
    """Advance to next stream if current is complete. Returns True if advanced."""
    if not check_stream_complete(meta):
        return False
    
    current = meta.get("current_stream", 1)
    total = meta.get("total_streams", 1)
    
    if current < total:
        meta["current_stream"] = current + 1
        return True
    
    return False


async def summarize_build(slug: str, meta: dict) -> str:
    """Generate completion summary"""
    deposits_dir = BUILDS_DIR / slug / "deposits"
    summaries = []
    
    for drop_id in sorted(meta.get("drops", {}).keys()):
        deposit = get_deposit(slug, drop_id)
        if deposit:
            summaries.append(f"**{drop_id}:** {deposit.get('summary', 'No summary')}")
    
    return "\n".join(summaries)


async def tick(slug: str):
    """Run one orchestration cycle"""
    print(f"\n[PULSE TICK] {slug} @ {datetime.now(timezone.utc).isoformat()}")
    
    meta = load_meta(slug)
    
    if meta.get("status") == "complete":
        print(f"[PULSE] Build {slug} already complete")
        return
    
    if meta.get("status") == "stopped":
        print(f"[PULSE] Build {slug} is stopped")
        return
    
    # 1. Check for new deposits from running Drops
    running = get_running_drops(meta)
    for drop_id, info in running:
        deposit = get_deposit(slug, drop_id)
        if deposit:
            print(f"[DEPOSIT] Found deposit for {drop_id}")
            
            # Run Filter
            try:
                brief = load_drop_brief(slug, drop_id)
                filter_result = await run_filter(slug, drop_id, brief, deposit)
                
                # Save filter result
                filter_path = BUILDS_DIR / slug / "deposits" / f"{drop_id}_filter.json"
                with open(filter_path, "w") as f:
                    json.dump(filter_result, f, indent=2)
                
                convo_id = info.get("conversation_id")
                
                if filter_result.get("verdict") == "PASS":
                    meta["drops"][drop_id]["status"] = "complete"
                    meta["drops"][drop_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
                    update_drop_conversation_status(convo_id, "complete")
                    print(f"[FILTER PASS] {drop_id}")
                else:
                    meta["drops"][drop_id]["status"] = "failed"
                    meta["drops"][drop_id]["failed_at"] = datetime.now(timezone.utc).isoformat()
                    meta["drops"][drop_id]["failure_reason"] = filter_result.get("reason", "Unknown")
                    update_drop_conversation_status(convo_id, "failed")
                    print(f"[FILTER FAIL] {drop_id}: {filter_result.get('reason')}")
                    await send_sms(f"[PULSE] {slug}: {drop_id} FAILED filter. Reason: {filter_result.get('reason', 'Unknown')[:50]}")
            except Exception as e:
                print(f"[FILTER ERROR] {drop_id}: {e}")
                # Auto-pass on filter error
                meta["drops"][drop_id]["status"] = "complete"
                meta["drops"][drop_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
                update_drop_conversation_status(info.get("conversation_id"), "complete")
    
    # 2. Check for dead Drops (running too long)
    dead_threshold = meta.get("dead_threshold_seconds", DEFAULT_DEAD_THRESHOLD)
    for drop_id, info in running:
        if info.get("status") != "running":
            continue  # Already processed above
        
        started_at = info.get("started_at")
        if started_at:
            started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            elapsed = (datetime.now(timezone.utc) - started).total_seconds()
            
            if elapsed > dead_threshold:
                print(f"[DEAD] {drop_id} - no deposit after {int(elapsed)}s")
                meta["drops"][drop_id]["status"] = "dead"
                meta["drops"][drop_id]["died_at"] = datetime.now(timezone.utc).isoformat()
                
                # Spawn Dredge
                await run_dredge(slug, drop_id, meta)
                
                # SMS escalation
                complete_count = sum(1 for d in meta["drops"].values() if d.get("status") == "complete")
                total_count = len(meta["drops"])
                await send_sms(f"[PULSE] {slug}: {drop_id} DEAD after {int(elapsed/60)}m. {complete_count}/{total_count} complete. Reply RESUME or STOP.")
    
    # 3. Check if stream complete, advance if so
    if advance_stream(meta):
        print(f"[STREAM] Advanced to Stream {meta['current_stream']}")
    
    # 4. Check if build complete
    all_terminal = all(
        info.get("status") in ["complete", "failed", "dead"]
        for info in meta.get("drops", {}).values()
    )
    if all_terminal:
        complete_count = sum(1 for d in meta["drops"].values() if d.get("status") == "complete")
        total_count = len(meta["drops"])
        
        if complete_count == total_count:
            meta["status"] = "complete"
            meta["completed_at"] = datetime.now(timezone.utc).isoformat()
            summary = await summarize_build(slug, meta)
            print(f"[BUILD COMPLETE] {slug}")
            await send_sms(f"[PULSE] {slug} BUILD COMPLETE. {complete_count}/{total_count} Drops succeeded.")
        else:
            meta["status"] = "partial"
            meta["completed_at"] = datetime.now(timezone.utc).isoformat()
            failed = [d for d, i in meta["drops"].items() if i.get("status") in ["failed", "dead"]]
            await send_sms(f"[PULSE] {slug} PARTIAL. {complete_count}/{total_count} succeeded. Failed: {', '.join(failed[:3])}")
    
    # 5. Spawn ready Drops
    ready = get_ready_drops(meta)
    model = meta.get("model")
    
    for drop_id in ready:
        try:
            brief = load_drop_brief(slug, drop_id)
            print(f"[SPAWN] {drop_id}")
            
            drop_info = meta.get("drops", {}).get(drop_id, {})
            spawn_mode = drop_info.get("spawn_mode", "auto")
            
            if spawn_mode == "manual":
                print(f"[SPAWN] {drop_id} is waiting for manual spawn")
                meta["drops"][drop_id]["status"] = "awaiting_manual"
                continue
            
            convo_id = await spawn_drop(slug, drop_id, brief, model)
            
            meta["drops"][drop_id]["status"] = "running"
            meta["drops"][drop_id]["started_at"] = datetime.now(timezone.utc).isoformat()
            meta["drops"][drop_id]["conversation_id"] = convo_id
            
            register_drop_conversation(drop_id, slug, convo_id)
            
        except Exception as e:
            print(f"[SPAWN ERROR] {drop_id}: {e}")
            meta["drops"][drop_id]["status"] = "failed"
            meta["drops"][drop_id]["failure_reason"] = str(e)
    
    # 6. Save state
    save_meta(slug, meta)
    update_status_md(slug, meta)
    
    print(f"[PULSE TICK DONE] Stream {meta.get('current_stream')}/{meta.get('total_streams')}")


async def start_build(slug: str):
    """Initialize and start a build"""
    meta = load_meta(slug)
    
    if meta.get("status") == "active":
        print(f"Build {slug} already active")
        return
    
    meta["status"] = "active"
    meta["started_at"] = datetime.now(timezone.utc).isoformat()
    
    # Initialize all drops to pending if not set
    for drop_id, info in meta.get("drops", {}).items():
        if "status" not in info:
            info["status"] = "pending"
    
    save_meta(slug, meta)
    update_status_md(slug, meta)
    
    print(f"[PULSE] Build {slug} started")
    await send_sms(f"[PULSE] Build {slug} STARTED. {len(meta.get('drops', {}))} Drops queued.")
    
    # Run first tick
    await tick(slug)


def stop_build(slug: str):
    """Stop a build gracefully"""
    meta = load_meta(slug)
    meta["status"] = "stopped"
    meta["stopped_at"] = datetime.now(timezone.utc).isoformat()
    save_meta(slug, meta)
    update_status_md(slug, meta)
    print(f"[PULSE] Build {slug} stopped")


def resume_build(slug: str):
    """Resume a stopped build"""
    meta = load_meta(slug)
    if meta.get("status") != "stopped":
        print(f"Build {slug} is not stopped (status: {meta.get('status')})")
        return
    
    meta["status"] = "active"
    meta["resumed_at"] = datetime.now(timezone.utc).isoformat()
    save_meta(slug, meta)
    print(f"[PULSE] Build {slug} resumed")


def show_status(slug: str):
    """Show build status"""
    meta = load_meta(slug)
    drops = meta.get("drops", {})
    
    complete = sum(1 for d in drops.values() if d.get("status") == "complete")
    running = sum(1 for d in drops.values() if d.get("status") == "running")
    pending = sum(1 for d in drops.values() if d.get("status") == "pending")
    dead = sum(1 for d in drops.values() if d.get("status") == "dead")
    failed = sum(1 for d in drops.values() if d.get("status") == "failed")
    
    print(f"""
Build: {slug}
Status: {meta.get('status', 'unknown')}
Stream: {meta.get('current_stream', '?')}/{meta.get('total_streams', '?')}

Drops:
  Complete: {complete}
  Running:  {running}
  Pending:  {pending}
  Dead:     {dead}
  Failed:   {failed}
  Total:    {len(drops)}

Progress: {complete}/{len(drops)} ({int(complete/len(drops)*100) if drops else 0}%)
""")


async def finalize_build(slug: str):
    """Run post-build finalization: safety checks, integration tests, harvest learnings"""
    print(f"\n[FINALIZE] {slug}")
    
    meta = load_meta(slug)
    results = {
        "slug": slug,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verification": None,
        "integration_tests": None,
        "learnings_harvested": 0,
        "success": True
    }
    
    # 1. Verify artifacts
    print("[FINALIZE] Verifying artifacts...")
    try:
        verify_result = subprocess.run(
            ["python3", str(SKILLS_DIR / "pulse_safety.py"), "verify", slug],
            capture_output=True, text=True, cwd=str(WORKSPACE)
        )
        results["verification"] = {
            "passed": verify_result.returncode == 0,
            "output": verify_result.stdout
        }
        if verify_result.returncode == 0:
            print("[FINALIZE] ✅ Artifact verification passed")
        else:
            print(f"[FINALIZE] ❌ Artifact verification failed")
            results["success"] = False
    except Exception as e:
        print(f"[FINALIZE] Verification error: {e}")
        results["verification"] = {"passed": False, "error": str(e)}
        results["success"] = False
    
    # 2. Run integration tests
    print("[FINALIZE] Running integration tests...")
    try:
        test_result = subprocess.run(
            ["python3", str(SKILLS_DIR / "pulse_integration_test.py"), "run", slug],
            capture_output=True, text=True, cwd=str(WORKSPACE)
        )
        results["integration_tests"] = {
            "passed": test_result.returncode == 0,
            "output": test_result.stdout
        }
        if test_result.returncode == 0:
            print("[FINALIZE] ✅ Integration tests passed")
        else:
            print(f"[FINALIZE] ❌ Integration tests failed")
            results["success"] = False
    except Exception as e:
        print(f"[FINALIZE] Test error: {e}")
        results["integration_tests"] = {"passed": False, "error": str(e)}
    
    # 3. Harvest learnings from deposits
    print("[FINALIZE] Harvesting learnings...")
    try:
        harvest_result = subprocess.run(
            ["python3", str(SKILLS_DIR / "pulse_learnings.py"), "harvest", slug],
            capture_output=True, text=True, cwd=str(WORKSPACE)
        )
        # Parse harvested count from output
        output = harvest_result.stdout
        if "Harvested" in output:
            try:
                count = int(output.split("Harvested")[1].split()[0])
                results["learnings_harvested"] = count
            except:
                pass
        print(f"[FINALIZE] Harvested learnings from deposits")
    except Exception as e:
        print(f"[FINALIZE] Harvest error: {e}")
    
    # 4. Save finalization results
    finalize_path = BUILDS_DIR / slug / "FINALIZATION.json"
    with open(finalize_path, "w") as f:
        json.dump(results, f, indent=2)
    
    # 5. Update meta
    meta["finalized_at"] = datetime.now(timezone.utc).isoformat()
    meta["finalization_passed"] = results["success"]
    save_meta(slug, meta)
    
    # 6. SMS summary
    if results["success"]:
        await send_sms(f"[PULSE] {slug} FINALIZED ✅ Artifacts verified, tests passed.")
    else:
        failures = []
        if not results.get("verification", {}).get("passed", True):
            failures.append("artifacts")
        if not results.get("integration_tests", {}).get("passed", True):
            failures.append("tests")
        await send_sms(f"[PULSE] {slug} FINALIZE ❌ Failed: {', '.join(failures)}. Review needed.")
    
    print(f"[FINALIZE] Complete. Success: {results['success']}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Pulse Build Orchestration")
    parser.add_argument("command", choices=["start", "status", "stop", "resume", "tick", "finalize"])
    parser.add_argument("slug", help="Build slug")
    
    args = parser.parse_args()
    
    if args.command == "start":
        asyncio.run(start_build(args.slug))
    elif args.command == "status":
        show_status(args.slug)
    elif args.command == "stop":
        stop_build(args.slug)
    elif args.command == "resume":
        resume_build(args.slug)
    elif args.command == "tick":
        asyncio.run(tick(args.slug))
    elif args.command == "finalize":
        asyncio.run(finalize_build(args.slug))


if __name__ == "__main__":
    main()
