#!/usr/bin/env python3
"""Regression test for Pulse spend guards.

Reproduces the 2026-09-02 runaway-spend incident shape without any network
calls, then asserts the guards hold:

1. No hardcoded model / provider id: inherit by default, env override wins.
2. Wave fan-out respects PULSE_MAX_CONCURRENT_SPAWNS (defers, does not fail).
3. A 402 / auth / model-config spawn failure blocks the build (R0), and a
   blocked build's tick is a no-op (no spawns).
4. Total spawn ceiling blocks the build once exhausted.
5. `resume` clears the blocked state.
6. spawn_drop has no silent fallback path to a different model.

Run: python3 Skills/pulse/scripts/test_spend_guards.py
Exit code 0 on pass, 1 on failure.
"""

import inspect
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault("PULSE_MAX_CONCURRENT_SPAWNS", "3")
os.environ.pop("ZO_ASK_MODEL_NAME", None)

import pulse  # noqa: E402
from pulse_common import PATHS  # noqa: E402

SLUG = "test-spend-guards"
BUILD_DIR = PATHS.BUILDS / SLUG


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def check(cond: bool, msg: str) -> None:
    if not cond:
        fail(msg)
    print(f"  ok  {msg}")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fresh_build(n_drops: int = 7) -> dict:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    for sub in ("drops", "deposits", "artifacts"):
        (BUILD_DIR / sub).mkdir(parents=True)
    drops = {}
    for i in range(1, n_drops + 1):
        did = f"D{i}"
        (BUILD_DIR / "drops" / f"{did}-smoke.md").write_text(
            f"---\ncreated: 2026-09-03\nlast_edited: 2026-09-03\nversion: 1.0\n"
            f"provenance: test-spend-guards\n---\n\n# {did}\n\nSmoke.\n"
        )
        drops[did] = {"status": "pending", "wave": "W1", "blocking": True, "spawn_mode": "auto"}
    meta = {
        "schema_version": 3,
        "slug": SLUG,
        "title": "Spend Guard Test",
        "status": "active",
        "started_at": now(),
        "waves": {"W1": {"drops": list(drops.keys()), "status": "active"}},
        "active_wave": "W1",
        "drops": drops,
    }
    (BUILD_DIR / "meta.json").write_text(json.dumps(meta, indent=2))
    return meta


def main() -> int:
    print("[1] model policy")
    check(pulse.resolve_spawn_model(None) is None, "no model → inherit (None)")
    check(pulse.resolve_spawn_model("inherit") is None, "'inherit' → None")
    check("model_name" not in pulse.build_zo_ask_body("x"), "inherit body omits model_name")
    check(pulse.build_zo_ask_body("x", "anthropic:foo")["model_name"] == "anthropic:foo", "explicit override honored")
    os.environ["ZO_ASK_MODEL_NAME"] = "openai:bar"
    check(pulse.resolve_spawn_model(None) == "openai:bar", "env override honored")
    os.environ.pop("ZO_ASK_MODEL_NAME")
    src = Path(pulse.__file__).read_text()
    check("byok:" not in src.replace("startswith(\"byok:\")", ""), "no provider connection id committed in pulse.py")
    check("retrying with default model" not in src, "silent model fallback removed")
    check(not hasattr(pulse, "DEFAULT_ZO_ASK_MODEL") and not hasattr(pulse, "DEFAULT_SPAWN_MODEL"),
          "no DEFAULT_*_MODEL constant")

    print("[2] non-retryable classification")
    for sig in (
        "API returned 402: Add credits or bring your own provider to continue.",
        "API returned 400: BYOK model config 'abc' was not found for this workspace.",
        "Spawn error: API returned 401: unauthorized",
    ):
        check(pulse.is_non_retryable_spawn_error(sig), f"non-retryable: {sig[:40]}…")
    for sig in (
        "API returned 429: Only 5 concurrent /zo/ask requests allowed",
        "API returned 503: temporarily unavailable",
        "Spawn error: spawn handshake timeout after 180s",
    ):
        check(not pulse.is_non_retryable_spawn_error(sig), f"retryable: {sig[:40]}…")

    print("[3] concurrency cap on wave fan-out (7 ready drops, cap 3)")
    fresh_build(7)
    launched = []
    pulse.launch_spawn_worker = lambda slug, drop_id, model=None: launched.append((drop_id, model)) or 4242
    pulse._pid_is_running = lambda pid: True
    pulse.register_drop_conversation = lambda *a, **k: None
    import asyncio
    asyncio.run(pulse._tick_inner(SLUG, "test"))
    meta = pulse.load_meta(SLUG)
    check(len(launched) == 3, f"exactly 3 spawned (got {len(launched)})")
    check(all(m is None for _, m in launched), "spawned with inherited model (None)")
    running = [d for d, i in meta["drops"].items() if i["status"] == "running"]
    pending = [d for d, i in meta["drops"].items() if i["status"] == "pending"]
    check(len(running) == 3 and len(pending) == 4, f"3 running / 4 deferred (got {len(running)}/{len(pending)})")
    check(meta.get("total_spawn_attempts") == 3, "total_spawn_attempts tracked")

    print("[4] 402 blocks the build; blocked tick is a no-op")
    pulse._record_spawn_failure(SLUG, "D1", "API returned 402: Add credits or bring your own provider to continue.")
    meta = pulse.load_meta(SLUG)
    check(meta["status"] == "blocked", "build blocked on 402")
    check(meta["drops"]["D1"].get("non_retryable") is True, "drop flagged non_retryable")
    launched.clear()
    asyncio.run(pulse._tick_inner(SLUG, "test"))
    check(launched == [], "blocked tick spawned nothing")
    meta = pulse.load_meta(SLUG)
    check(meta["drops"]["D1"].get("retry_count", 0) == 0, "no auto-retry of 402 drop")

    print("[5] resume clears blocked")
    check(pulse.resume_build(SLUG), "resume returns True")
    meta = pulse.load_meta(SLUG)
    check(meta["status"] == "active" and "blocked_reason" not in meta, "status active, reason cleared")

    print("[6] total spawn ceiling")
    fresh_build(2)
    meta = pulse.load_meta(SLUG)
    meta["max_total_spawns"] = 1
    pulse.save_meta(SLUG, meta)
    launched.clear()
    asyncio.run(pulse._tick_inner(SLUG, "test"))
    meta = pulse.load_meta(SLUG)
    check(len(launched) == 1, "one spawn allowed")
    check(meta["status"] == "blocked" and "ceiling" in meta["blocked_reason"].lower(), "ceiling blocks build")

    print("[7] R2 retry still works for transient errors but respects ceiling")
    fresh_build(1)
    meta = pulse.load_meta(SLUG)
    meta["drops"]["D1"].update({"status": "failed", "failure_reason": "Spawn error: API returned 429: busy", "retry_count": 0})
    pulse.save_meta(SLUG, meta)
    launched.clear()
    asyncio.run(pulse._tick_inner(SLUG, "test"))
    meta = pulse.load_meta(SLUG)
    check(meta["drops"]["D1"]["retry_count"] == 1, "429 auto-retried once (R2)")
    check(len(launched) == 1, "retried drop re-spawned under cap")

    sig = inspect.signature(pulse.spawn_drop)
    check("model" in sig.parameters, "spawn_drop still accepts explicit model override")

    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    print("PASS: spend guards hold (model inherit, concurrency cap, 402 block, ceiling, resume)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
