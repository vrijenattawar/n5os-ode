#!/usr/bin/env python3
"""
persona_sync.py — Personas-as-code sync tool.

N5/personas/ is the git-tracked SSOT for Zo persona prompts.
Live Zo personas are a deploy target reached via the /zo/ask bridge.

Subcommands:
    export [--out N5/personas]   Fetch all live personas -> SSOT files + registry.json
    diff   [slug ...]            Compare live prompts vs SSOT bodies (0 clean / 1 drift / 2 error)
    push   [slug ...] [--force]  SSOT -> live via edit_persona, with guards + snapshots
    check                        Offline consistency checks (0 ok / 1 problems)
    --self-test                  Run inline unit tests for slug + path-extraction logic

Auth: ZO_CLIENT_IDENTITY_TOKEN env var. No live mutation except `push`.
"""

import argparse
import ast
import difflib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml

WORKSPACE = Path(__file__).resolve().parents[2]
DEFAULT_SSOT = WORKSPACE / "N5" / "personas"
CONTRACT_PATH = WORKSPACE / "N5" / "prefs" / "system" / "persona_routing_contract.md"
API_URL = "https://api.zo.computer/zo/ask"
MCP_URL = "https://api.zo.computer/mcp"
TIMEOUT = 300
RETRIES = 2

PATH_RE = re.compile(
    r"\b(?:N5|Skills|Documents|Sites|Research|Prompts|Personal|Knowledge)"
    r"/[\w\-./]+\.(?:md|py|json|yaml|ts|txt)\b"
)
VERSION_RE = re.compile(r"^version:\s*['\"]?([0-9][\w.\-]*)['\"]?\s*$", re.MULTILINE)
UUID_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")


# ---------------------------------------------------------------- utilities

def slugify(name: str) -> str:
    n = name.strip()
    if n.lower().startswith("vibe "):
        n = n[5:]
    return n.strip().lower().replace(" ", "-")


def extract_paths(text: str) -> list:
    return sorted(set(PATH_RE.findall(text)))


def missing_paths(text: str) -> list:
    return [p for p in extract_paths(text) if not (WORKSPACE / p).exists()]


def parse_version(prompt: str) -> str:
    m = VERSION_RE.search(prompt)
    return m.group(1) if m else "unknown"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def snapshot_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def atomic_write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=path.suffix)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def render_persona_file(meta: dict, body: str) -> str:
    fm = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return f"---\n{fm}---\n{body}"


def parse_persona_file(path: Path):
    """Return (frontmatter dict, exact body). Body is everything after the closing ---."""
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        raise ValueError(f"{path}: missing frontmatter opener")
    end = raw.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path}: missing frontmatter closer")
    meta = yaml.safe_load(raw[4:end + 1])
    body = raw[end + len("\n---\n"):]
    return meta, body


def char_delta(ssot: str, live: str):
    sm = difflib.SequenceMatcher(None, ssot, live, autojunk=False)
    plus = minus = 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op in ("insert", "replace"):
            plus += j2 - j1
        if op in ("delete", "replace"):
            minus += i2 - i1
    return plus, minus


# ---------------------------------------------------------------- bridge

class BridgeError(Exception):
    pass


def _mcp_call(name: str, arguments: dict) -> dict:
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise BridgeError("ZO_CLIENT_IDENTITY_TOKEN not set")
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
    }
    resp = requests.post(
        MCP_URL,
        headers={
            "authorization": token,
            "content-type": "application/json",
            "accept": "application/json",
        },
        json=payload,
        timeout=TIMEOUT,
    )
    if resp.status_code != 200:
        raise BridgeError(f"MCP HTTP {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    if data.get("error"):
        raise BridgeError(f"MCP {name} error: {data['error']}")
    return data.get("result") or {}


def _decode_tool_value(value: str) -> str:
    out = []
    i = 0
    while i < len(value):
        ch = value[i]
        if ch != "\\" or i + 1 >= len(value):
            out.append(ch)
            i += 1
            continue
        nxt = value[i + 1]
        if nxt == "n":
            out.append("\n")
            i += 2
        elif nxt == "r":
            out.append("\r")
            i += 2
        elif nxt == "t":
            out.append("\t")
            i += 2
        elif nxt in {"'", '"', "\\"}:
            out.append(nxt)
            i += 2
        elif nxt == "u" and i + 5 < len(value):
            try:
                out.append(chr(int(value[i + 2:i + 6], 16)))
                i += 6
            except ValueError:
                out.append(nxt)
                i += 2
        elif nxt == "U" and i + 9 < len(value):
            try:
                out.append(chr(int(value[i + 2:i + 10], 16)))
                i += 10
            except ValueError:
                out.append(nxt)
                i += 2
        else:
            out.append(nxt)
            i += 2
    decoded = "".join(out)
    return decoded.encode("utf-16", "surrogatepass").decode("utf-16")


def _parse_mcp_personas(result: dict) -> list:
    content = result.get("content") or []
    if not content:
        raise BridgeError("MCP list_personas returned no content")
    text = content[0].get("text", "") if isinstance(content[0], dict) else ""
    if not text:
        raise BridgeError("MCP list_personas returned empty text")

    try:
        items = ast.literal_eval(text)
    except (SyntaxError, ValueError) as e:
        raise BridgeError(f"could not parse MCP list_personas payload: {e}") from e
    if not isinstance(items, list):
        raise BridgeError("MCP list_personas payload was not a list")

    pat = re.compile(
        r"^id='(?P<id>[^']+)' name='(?P<name>(?:\\'|[^'])*)' "
        r"prompt='(?P<prompt>(?:\\'|[^'])*)' model=(?P<rest>.*)$",
        re.S,
    )
    personas = []
    for i, item in enumerate(items, start=1):
        if not isinstance(item, str):
            raise BridgeError(f"MCP list_personas item {i} was not a string")
        m = pat.match(item)
        if not m:
            raise BridgeError(f"MCP list_personas item {i} had unexpected format: {item[:120]}")
        personas.append({
            "id": m.group("id"),
            "name": _decode_tool_value(m.group("name")),
            "prompt": _decode_tool_value(m.group("prompt")),
        })
    return personas


def fetch_all_live_mcp() -> list:
    return _parse_mcp_personas(_mcp_call("list_personas", {}))


def push_persona_prompt_mcp(pid: str, text: str) -> dict:
    raise BridgeError(
        "MCP backend exposes merge-style edit_persona, not exact prompt replacement; "
        "set PERSONA_SYNC_BACKEND=zoask for push"
    )


def bridge_ask(input_text: str, output_format: dict) -> dict:
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise BridgeError("ZO_CLIENT_IDENTITY_TOKEN not set")
    last_err = None
    for attempt in range(RETRIES + 1):
        try:
            resp = requests.post(
                API_URL,
                headers={"authorization": token, "content-type": "application/json"},
                json={"input": input_text, "output_format": output_format},
                timeout=TIMEOUT,
            )
            if resp.status_code >= 500:
                last_err = BridgeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
                continue
            if resp.status_code != 200:
                raise BridgeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
            output = resp.json().get("output")
            if isinstance(output, str):
                try:
                    output = json.loads(output)
                except json.JSONDecodeError:
                    raise BridgeError(f"non-JSON output: {output[:200]}")
            if not isinstance(output, dict):
                raise BridgeError(f"unexpected output type: {type(output).__name__}")
            return output
        except (requests.Timeout, requests.ConnectionError) as e:
            last_err = e
    raise BridgeError(f"bridge failed after {RETRIES + 1} attempts: {last_err}")


def fetch_persona_index() -> list:
    """Fetch id+name for all live personas (no prompts, avoids truncation)."""
    out = bridge_ask(
        "Run list_personas and return a JSON object with key 'personas': an array of "
        "objects with fields 'id' and 'name' ONLY (no prompts), one per persona, "
        "covering every persona. No commentary.",
        {
            "type": "object",
            "properties": {
                "personas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
                        "required": ["id", "name"],
                    },
                }
            },
            "required": ["personas"],
        },
    )
    personas = out.get("personas") or []
    if not personas:
        raise BridgeError("list_personas returned no personas")
    return personas


def fetch_persona_prompt(pid: str) -> dict:
    """Fetch one persona's full record: id, name, prompt (verbatim)."""
    if os.environ.get("PERSONA_SYNC_BACKEND", "mcp").lower() == "mcp":
        for rec in fetch_all_live_mcp():
            if rec["id"] == pid:
                return rec
        raise BridgeError(f"MCP list_personas did not include {pid}")

    out = bridge_ask(
        f"Run list_personas and return ONLY the JSON object for the persona with id {pid}, "
        "with fields 'id', 'name', and 'prompt'. The 'prompt' field must be the EXACT, "
        "complete, verbatim prompt text with no truncation, no summarization, no edits.",
        {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "prompt": {"type": "string"},
            },
            "required": ["id", "name", "prompt"],
        },
    )
    if out.get("id") != pid:
        raise BridgeError(f"asked for {pid}, got {out.get('id')}")
    if not out.get("prompt"):
        raise BridgeError(f"empty prompt returned for {pid}")
    return out


def push_persona_prompt(pid: str, text: str) -> dict:
    if os.environ.get("PERSONA_SYNC_BACKEND", "mcp").lower() == "mcp":
        return push_persona_prompt_mcp(pid, text)

    out = bridge_ask(
        f"Run edit_persona with persona_id={pid} and set the prompt EXACTLY to the "
        "following text (no additions, no summaries, no trimming — the entire text "
        "between the BEGIN and END markers, exclusive of the markers themselves):\n"
        f"---BEGIN PROMPT---\n{text}\n---END PROMPT---\n"
        "Then return a JSON object {\"success\": true|false, \"error\": \"...\"} describing the result.",
        {
            "type": "object",
            "properties": {"success": {"type": "boolean"}, "error": {"type": "string"}},
            "required": ["success"],
        },
    )
    return out


def fetch_all_live() -> list:
    """Full fetch: index then per-persona prompts. Returns list of {id,name,prompt}."""
    if os.environ.get("PERSONA_SYNC_BACKEND", "mcp").lower() == "mcp":
        return fetch_all_live_mcp()

    index = fetch_persona_index()
    result = []
    for entry in index:
        rec = fetch_persona_prompt(entry["id"])
        result.append(rec)
    return result


def load_persona_dump(path: Path) -> list:
    """Load persona records from a JSON dump produced by list_personas-style tooling."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw = raw.get("personas", raw.get("data", raw.get("output", raw)))
    if isinstance(raw, dict) and "personas" in raw:
        raw = raw["personas"]
    if not isinstance(raw, list):
        raise ValueError(f"{path}: expected JSON list or object with personas[]")

    personas = []
    for i, rec in enumerate(raw, start=1):
        if not isinstance(rec, dict):
            raise ValueError(f"{path}: record {i} is not an object")
        pid = rec.get("id")
        name = rec.get("name")
        prompt = rec.get("prompt")
        if not pid or not name or prompt is None:
            raise ValueError(f"{path}: record {i} missing id/name/prompt")
        personas.append({"id": str(pid), "name": str(name), "prompt": str(prompt)})
    if not personas:
        raise ValueError(f"{path}: no personas found")
    return personas


# ---------------------------------------------------------------- SSOT I/O

def load_ssot(ssot_dir: Path) -> dict:
    """Return {slug: {"meta": dict, "body": str, "path": Path}} for all persona files."""
    out = {}
    for f in sorted(ssot_dir.glob("*.md")):
        if f.name == "README.md":
            continue
        meta, body = parse_persona_file(f)
        slug = meta.get("slug") or slugify(meta.get("name", f.stem))
        out[slug] = {"meta": meta, "body": body, "path": f}
    return out


def load_registry(ssot_dir: Path) -> list:
    reg_path = ssot_dir / "registry.json"
    if not reg_path.exists():
        return []
    return json.loads(reg_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- commands

def cmd_export(args) -> int:
    ssot_dir = Path(args.out)
    if not ssot_dir.is_absolute():
        ssot_dir = WORKSPACE / ssot_dir
    try:
        live = load_persona_dump(Path(args.from_json)) if args.from_json else fetch_all_live()
    except (BridgeError, ValueError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    exported = utc_now()
    registry = []
    for rec in sorted(live, key=lambda r: slugify(r["name"])):
        slug = slugify(rec["name"])
        prompt = rec["prompt"]
        meta = {
            "id": rec["id"],
            "name": rec["name"],
            "slug": slug,
            "version": parse_version(prompt),
            "exported": exported,
            "char_count": len(prompt),
        }
        atomic_write(ssot_dir / f"{slug}.md", render_persona_file(meta, prompt))
        registry.append({
            "id": rec["id"], "slug": slug, "name": rec["name"],
            "version": meta["version"], "file": f"{slug}.md",
            "char_count": len(prompt), "exported": exported,
        })
        print(f"  exported {slug}.md ({len(prompt)} chars, v{meta['version']})")
    atomic_write(ssot_dir / "registry.json", json.dumps(registry, indent=2) + "\n")
    print(f"Export complete: {len(registry)} personas -> {ssot_dir}")
    return 0


def _resolve_slugs(requested, ssot: dict, registry: list) -> list:
    known = set(ssot) | {r["slug"] for r in registry}
    if not requested:
        return sorted(known)
    bad = [s for s in requested if s not in known]
    if bad:
        raise KeyError(f"unknown slug(s): {', '.join(bad)}")
    return list(requested)


def cmd_diff(args) -> int:
    ssot_dir = DEFAULT_SSOT
    try:
        ssot = load_ssot(ssot_dir)
        registry = load_registry(ssot_dir)
        slugs = _resolve_slugs(args.slugs, ssot, registry)
        live = {slugify(r["name"]): r for r in fetch_all_live()}
    except BridgeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except (KeyError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    drift = False
    for slug in slugs:
        in_ssot, in_live = slug in ssot, slug in live
        if in_ssot and not in_live:
            print(f"  {slug}: missing-in-live")
            drift = True
        elif in_live and not in_ssot:
            print(f"  {slug}: missing-in-ssot")
            drift = True
        elif ssot[slug]["body"] == live[slug]["prompt"]:
            print(f"  {slug}: clean")
        else:
            plus, minus = char_delta(ssot[slug]["body"], live[slug]["prompt"])
            print(f"  {slug}: drift (+{plus}/-{minus} chars)")
            drift = True
    # live personas not covered by explicit slug filter are only reported in full diff
    if not args.slugs:
        for slug in sorted(set(live) - set(slugs)):
            print(f"  {slug}: missing-in-ssot")
            drift = True
    print("RESULT: drift detected" if drift else "RESULT: all clean")
    return 1 if drift else 0


def cmd_push(args) -> int:
    ssot_dir = DEFAULT_SSOT
    try:
        ssot = load_ssot(ssot_dir)
        registry = load_registry(ssot_dir)
        slugs = _resolve_slugs(args.slugs, ssot, registry)
    except (KeyError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    slugs = [s for s in slugs if s in ssot]

    # Guard (a): broken workspace references
    broken = {}
    for slug in slugs:
        miss = missing_paths(ssot[slug]["body"])
        if miss:
            broken[slug] = miss
    if broken and not args.force:
        print("REFUSING push: SSOT bodies reference missing workspace paths "
              "(use --force to override):", file=sys.stderr)
        for slug, miss in broken.items():
            for p in miss:
                print(f"  {slug}: {p}", file=sys.stderr)
        return 1
    if broken:
        print("WARNING: --force used; pushing despite missing paths.")

    ts = snapshot_ts()
    failed = False
    try:
        for slug in slugs:
            rec = ssot[slug]
            pid = rec["meta"]["id"]
            live = fetch_persona_prompt(pid)
            if live["prompt"] == rec["body"]:
                print(f"  {slug}: clean (skipped)")
                continue

            # Guard (b): snapshot current live prompt BEFORE overwrite
            snap_meta = {
                "id": pid, "name": live["name"], "slug": slug,
                "snapshot": utc_now(), "char_count": len(live["prompt"]),
                "note": "pre-push live snapshot",
            }
            snap_path = ssot_dir / ".snapshots" / ts / f"{slug}.md"
            atomic_write(snap_path, render_persona_file(snap_meta, live["prompt"]))

            result = push_persona_prompt(pid, rec["body"])
            if not result.get("success"):
                print(f"  {slug}: PUSH FAILED — {result.get('error', 'unknown error')}")
                failed = True
                continue

            # Guard (c): post-push verify
            verify = fetch_persona_prompt(pid)
            if verify["prompt"] == rec["body"]:
                print(f"  {slug}: pushed + verified clean (snapshot {ts}/{slug}.md)")
            else:
                plus, minus = char_delta(rec["body"], verify["prompt"])
                print(f"  {slug}: PUSHED BUT VERIFY MISMATCH (+{plus}/-{minus} chars) "
                      f"— live snapshot preserved at .snapshots/{ts}/{slug}.md")
                failed = True
    except BridgeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    return 1 if failed else 0


def _contract_persona_names(contract_text: str) -> list:
    """Extract persona names the contract refers to.

    Rules: bold names starting with 'Vibe ' (e.g. **Vibe Librarian**), and bold
    names immediately followed by a backticked UUID (e.g. **Librarian** (`uuid`)).
    """
    names = set()
    for m in re.finditer(r"\*\*Vibe ([A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)*)\*\*", contract_text):
        names.add(m.group(1))
    for m in re.finditer(
        r"\*\*([A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)*)\*\*\s*\(`" + UUID_RE.pattern.strip(r"\b") + r"`\)",
        contract_text,
    ):
        names.add(m.group(1))
    return sorted(names)


def cmd_check(args) -> int:
    ssot_dir = DEFAULT_SSOT
    problems = []

    # 1. SSOT files parse
    ssot = {}
    for f in sorted(ssot_dir.glob("*.md")):
        if f.name == "README.md":
            continue
        try:
            meta, body = parse_persona_file(f)
            slug = meta.get("slug")
            if not meta.get("id") or not slug:
                problems.append(f"{f.name}: frontmatter missing id/slug")
                continue
            if slug != f.stem:
                problems.append(f"{f.name}: slug '{slug}' != filename stem")
            ssot[slug] = {"meta": meta, "body": body}
        except (ValueError, yaml.YAMLError) as e:
            problems.append(f"{f.name}: parse error: {e}")

    # 2. Registry <-> files 1:1, IDs unique
    registry = load_registry(ssot_dir)
    if not registry:
        problems.append("registry.json missing or empty")
    reg_slugs = {r["slug"] for r in registry}
    reg_ids = [r["id"] for r in registry]
    if len(reg_ids) != len(set(reg_ids)):
        problems.append("registry.json contains duplicate IDs")
    for r in registry:
        if r["slug"] not in ssot:
            problems.append(f"registry entry '{r['slug']}' has no SSOT file")
        elif ssot[r["slug"]]["meta"].get("id") != r["id"]:
            problems.append(f"registry/frontmatter ID mismatch for '{r['slug']}'")
    for slug in ssot:
        if slug not in reg_slugs:
            problems.append(f"SSOT file '{slug}.md' not in registry.json")

    # 3. Referenced workspace paths exist
    for slug, rec in sorted(ssot.items()):
        for p in missing_paths(rec["body"]):
            problems.append(f"{slug}.md references missing path: {p}")

    # 4. Contract persona names ⊆ registry
    if CONTRACT_PATH.exists():
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        reg_names = {r["name"].lower() for r in registry}
        reg_names |= {n[5:] for n in reg_names if n.startswith("vibe ")}
        reg_names |= {"vibe " + n for n in set(reg_names)}
        for name in _contract_persona_names(contract):
            if name.lower() not in reg_names:
                problems.append(f"contract names persona '{name}' not in registry")
        reg_id_set = set(reg_ids)
        for uid in sorted(set(UUID_RE.findall(contract))):
            if uid not in reg_id_set:
                problems.append(f"contract references unknown persona ID: {uid}")
    else:
        problems.append(f"routing contract not found: {CONTRACT_PATH}")

    if problems:
        print(f"CHECK FAILED — {len(problems)} problem(s):")
        for p in problems:
            print(f"  ✗ {p}")
        return 1
    print(f"CHECK OK — {len(ssot)} personas, registry consistent, all paths exist, "
          "contract names resolve.")
    return 0


# ---------------------------------------------------------------- self-test

def self_test() -> int:
    fails = []

    def eq(actual, expected, label):
        if actual != expected:
            fails.append(f"{label}: got {actual!r}, want {expected!r}")

    eq(slugify("Vibe Level Upper"), "level-upper", "slug: Vibe Level Upper")
    eq(slugify("Operator"), "operator", "slug: Operator")
    eq(slugify("Vibe Nutritionist"), "nutritionist", "slug: Vibe Nutritionist")
    eq(slugify("  Vibe Writer "), "writer", "slug: whitespace")

    text = ("See N5/prefs/system/git-governance.md and Skills/pulse/SKILL.md, "
            "plus Sites/vibe-trainer/**/latest_report.json and "
            "Documents/System/Maintainer-Playbook.md; also nonpath/foo.md and "
            "N5/scripts/persona_sync.py.")
    eq(extract_paths(text), [
        "Documents/System/Maintainer-Playbook.md",
        "N5/prefs/system/git-governance.md",
        "N5/scripts/persona_sync.py",
        "Skills/pulse/SKILL.md",
    ], "path extraction")

    eq(parse_version("name: Operator\nversion: '4.1'\nupdated: x"), "4.1", "version quoted")
    eq(parse_version("version: 2.0\n"), "2.0", "version bare")
    eq(parse_version("no version here"), "unknown", "version missing")

    meta = {"id": "x", "name": "Test", "slug": "test"}
    body = "line1\n---\nweird body with --- inside\n"
    rendered = render_persona_file(meta, body)
    tmp = Path(tempfile.mkdtemp()) / "test.md"
    tmp.write_text(rendered, encoding="utf-8")
    m2, b2 = parse_persona_file(tmp)
    eq(b2, body, "roundtrip body exact")
    eq(m2["id"], "x", "roundtrip meta")

    names = _contract_persona_names(
        "**Vibe Librarian** does X. **Librarian** (`1bb66f53-9e2a-4152-9b18-75c2ee2c25a3`) "
        "and **Routing:** stuff and **substantial** words. **Vibe Level Upper** too."
    )
    eq(names, ["Level Upper", "Librarian"], "contract name extraction")

    plus, minus = char_delta("abcdef", "abXdef")
    eq((plus, minus), (1, 1), "char delta replace")

    if fails:
        print("SELF-TEST FAILED:")
        for f in fails:
            print(f"  ✗ {f}")
        return 1
    print("SELF-TEST OK (all assertions passed)")
    return 0


# ---------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--self-test", action="store_true", help="run inline unit tests")
    sub = parser.add_subparsers(dest="command")

    p_export = sub.add_parser("export", help="fetch live personas -> SSOT")
    p_export.add_argument("--out", default=str(DEFAULT_SSOT))
    p_export.add_argument("--from-json", help="read personas from a JSON dump instead of live Zo")

    p_diff = sub.add_parser("diff", help="compare live vs SSOT")
    p_diff.add_argument("slugs", nargs="*")

    p_push = sub.add_parser("push", help="SSOT -> live")
    p_push.add_argument("slugs", nargs="*")
    p_push.add_argument("--force", action="store_true")

    sub.add_parser("check", help="offline consistency checks")

    args = parser.parse_args()
    if args.self_test:
        sys.exit(self_test())
    if args.command == "export":
        sys.exit(cmd_export(args))
    if args.command == "diff":
        sys.exit(cmd_diff(args))
    if args.command == "push":
        sys.exit(cmd_push(args))
    if args.command == "check":
        sys.exit(cmd_check(args))
    parser.print_help()
    sys.exit(2)


if __name__ == "__main__":
    main()
