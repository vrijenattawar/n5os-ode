#!/usr/bin/env python3
"""
Calendar triangulation module for meeting-ingestion skill.
Matches meetings to calendar events for participant identification.

This module queries Google Calendar via use_app_google_calendar to find events
that match a meeting by timestamp (±30 min), title similarity, and attendees.
Returns confidence score and matched event data for participant extraction.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional


def similarity(a: str, b: str) -> float:
    """Calculate similarity between two strings using SequenceMatcher."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def parse_meeting_datetime(date_str: str, time_str: str) -> datetime:
    """Parse meeting date and time into datetime object."""
    if not time_str or str(time_str) == "None":
        time_str = "12:00:00"
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")


def parse_calendar_datetime(cal_datetime_str: str) -> datetime:
    """Parse Google Calendar datetime string to datetime object."""
    # Handle RFC3339 format with timezone
    if 'T' in cal_datetime_str:
        # Parse with timezone info, then convert to UTC naive
        from datetime import timezone
        
        if cal_datetime_str.endswith('Z'):
            # UTC timezone
            dt = datetime.fromisoformat(cal_datetime_str.replace('Z', '+00:00'))
        elif '+' in cal_datetime_str or '-' in cal_datetime_str.split('T')[1]:
            # Has timezone offset
            dt = datetime.fromisoformat(cal_datetime_str)
        else:
            # No timezone, assume UTC
            dt = datetime.fromisoformat(cal_datetime_str).replace(tzinfo=timezone.utc)
        
        # Convert to UTC and remove timezone info for comparison
        dt_utc = dt.astimezone(timezone.utc)
        return dt_utc.replace(tzinfo=None)
    
    # Date only format
    return datetime.fromisoformat(cal_datetime_str)


def is_time_match(meeting_dt: datetime, event_dt: datetime, tolerance_minutes: int = 30) -> bool:
    """Check if meeting and event times match within tolerance."""
    time_diff = abs((meeting_dt - event_dt).total_seconds() / 60)
    return time_diff <= tolerance_minutes


def calculate_confidence(meeting: Dict, event: Dict, match_method: str) -> float:
    """Calculate confidence score for a calendar match."""
    confidence = 0.0
    
    # Parse meeting datetime
    meeting_dt = parse_meeting_datetime(meeting['date'], meeting.get('time_utc'))
    
    # Parse event datetime  
    if 'start' in event:
        start_time = event['start'].get('dateTime') or event['start'].get('date')
        if start_time:
            try:
                event_dt = parse_calendar_datetime(start_time)
            except:
                return 0.0
        else:
            return 0.0
    else:
        return 0.0
    
    # Time matching (0.4 weight)
    if is_time_match(meeting_dt, event_dt):
        confidence += 0.4
    
    # Title similarity (0.3 weight)
    meeting_title = meeting.get('title', '').strip()
    event_title = event.get('summary', '').strip()
    if meeting_title and event_title:
        title_sim = similarity(meeting_title, event_title)
        confidence += 0.3 * title_sim
    
    # Attendees presence (0.3 weight)
    if 'attendees' in event and event['attendees']:
        confidence += 0.15
    
    # Adjust confidence based on match method
    if match_method == 'timestamp+title' and confidence > 0.7:
        confidence = min(confidence + 0.1, 1.0)  # Boost high-confidence combined matches
    elif match_method == 'title_only':
        confidence *= 0.8  # Reduce confidence for title-only matches
    elif match_method == 'timestamp_only':
        confidence *= 0.7  # Reduce confidence for timestamp-only matches
    
    return round(confidence, 3)


def extract_attendee_emails(event: Dict) -> List[str]:
    """Extract attendee emails from calendar event."""
    emails = []
    attendees = event.get('attendees', [])
    
    for attendee in attendees:
        email = attendee.get('email', '')
        if email and email not in emails:
            emails.append(email)
    
    return emails


def find_best_match(meeting: Dict, events: List[Dict]) -> Optional[Dict]:
    """Find the best matching calendar event for a meeting."""
    if not events:
        return None
    
    best_match = None
    best_confidence = 0.0
    
    # Parse meeting details
    meeting_dt = parse_meeting_datetime(meeting['date'], meeting.get('time_utc'))
    meeting_title = meeting.get('title', '').strip()
    
    for event in events:
        # Skip events without proper time info
        if 'start' not in event:
            continue
            
        start_time = event['start'].get('dateTime') or event['start'].get('date')
        if not start_time:
            continue
        
        try:
            event_dt = parse_calendar_datetime(start_time)
        except:
            continue
        
        # Determine match method
        time_matches = is_time_match(meeting_dt, event_dt)
        title_matches = False
        
        event_title = event.get('summary', '').strip()
        if meeting_title and event_title:
            title_matches = similarity(meeting_title, event_title) > 0.6
        
        if time_matches and title_matches:
            method = 'timestamp+title'
        elif title_matches:
            method = 'title_only'
        elif time_matches:
            method = 'timestamp_only'
        else:
            continue  # Skip events with no reasonable match
        
        confidence = calculate_confidence(meeting, event, method)
        
        if confidence > best_confidence:
            best_confidence = confidence
            best_match = {
                'event_id': event.get('id', ''),
                'confidence': confidence,
                'method': method,
                'event_data': event,
                'attendee_emails': extract_attendee_emails(event)
            }
    
    return best_match


# ---------------------------------------------------------------------------
# D3: Multi-calendar resolver
# ---------------------------------------------------------------------------

_CALENDAR_CONFIG_CACHE: Optional[Dict] = None


def _load_calendar_config() -> Dict:
    """Load calendars.yaml once and cache. Falls back to single-calendar default if missing."""
    global _CALENDAR_CONFIG_CACHE
    if _CALENDAR_CONFIG_CACHE is not None:
        return _CALENDAR_CONFIG_CACHE
    try:
        import yaml
        cfg_path = Path(__file__).resolve().parent.parent / "config" / "calendars.yaml"
        with open(cfg_path, "r") as f:
            cfg = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Warning: calendar config load failed ({e}); using single-calendar fallback", file=sys.stderr)
        cfg = {"calendars": [{"id": "me@example.com", "priority": 1}],
               "time_window_hours_exact": 2, "time_window_hours_approx": 12}
    _CALENDAR_CONFIG_CACHE = cfg
    return cfg


def _zo_ask_body(prompt: str) -> dict:
    """Build /zo/ask body; only pin a model when ZO_ASK_MODEL_NAME is set."""
    body = {"input": prompt}
    model = os.environ.get("ZO_ASK_MODEL_NAME", "").strip()
    if model:
        body["model_name"] = model
    return body


def _query_single_calendar(time_min: str, time_max: str, email: str) -> List[Dict]:
    """Query ONE Google Calendar by id for events in a time window via /zo/ask."""
    import re as _re, requests as _requests, json as _json
    zo_token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not zo_token:
        print("Warning: ZO_CLIENT_IDENTITY_TOKEN not set, skipping calendar lookup", file=sys.stderr)
        return []
    prompt = (
        f"Use google_calendar-list-events with calendarId=\"{email}\", "
        f"timeMin=\"{time_min}\", timeMax=\"{time_max}\", and singleEvents=true. "
        "Return ONLY the raw JSON array of events (no markdown, no explanation). "
        "Each event should include: id, iCalUID, summary, start, end, attendees, organizer. "
        "If no events found, return []."
    )
    try:
        resp = _requests.post(
            "https://api.zo.computer/zo/ask",
            headers={"authorization": zo_token, "content-type": "application/json"},
            json=_zo_ask_body(prompt),
            timeout=30,
        )
        if resp.status_code != 200:
            print(f"Warning: Zo API returned {resp.status_code} for {email}", file=sys.stderr)
            return []
        output = resp.json().get("output", "")
        if isinstance(output, list):
            return output
        if isinstance(output, dict):
            return output.get("events", output.get("items", [output] if ("id" in output) else []))
        if not isinstance(output, str):
            return []
        m = _re.search(r"```(?:json)?\s*(\[[\s\S]*?\]|\{[\s\S]*?\})\s*```", output)
        raw = m.group(1) if m else None
        if not raw:
            m = _re.search(r"(\[[\s\S]*\])", output)
            if m: raw = m.group(1)
        if not raw:
            m = _re.search(r"(\{[\s\S]*\})", output)
            if m: raw = m.group(1)
        if not raw:
            return []
        parsed = _json.loads(raw)
        if isinstance(parsed, list): return parsed
        if isinstance(parsed, dict):
            return parsed.get("items", parsed.get("events", [parsed] if "id" in parsed else []))
        return []
    except Exception as e:
        print(f"Warning: Calendar query failed for {email}: {e}", file=sys.stderr)
        return []


def _query_google_calendar(time_min: str, time_max: str, email: str = None) -> List[Dict]:
    """Multi-calendar query: iterate all configured calendars fail-soft.

    Returns a FLAT list of event dicts, each annotated with `_calendar_id` and
    `_priority`. The `email` arg, if provided, is biased to priority 0 (highest).
    Dedup by iCalUID + attendee union happens in _dedup_and_union().
    """
    cfg = _load_calendar_config()
    cals = list(cfg.get("calendars", []))
    if email:
        # Bias requested calendar to priority 0 for this invocation
        found = False
        for c in cals:
            if c.get("id") == email:
                c["_bias_priority"] = 0
                found = True
                break
        if not found:
            cals.insert(0, {"id": email, "priority": 0, "_bias_priority": 0})
    # Sort by effective priority (bias wins over configured)
    def _eff_pri(c):
        return c.get("_bias_priority", c.get("priority", 99))
    cals.sort(key=_eff_pri)

    all_events: List[Dict] = []
    for c in cals:
        cal_id = c.get("id")
        pri = _eff_pri(c)
        try:
            events = _query_single_calendar(time_min, time_max, cal_id)
        except Exception as e:
            print(f"Warning: calendar {cal_id} failed: {e}", file=sys.stderr)
            events = []
        for ev in events:
            ev["_calendar_id"] = cal_id
            ev["_priority"] = pri
        all_events.extend(events)
    print(f"Multi-calendar query returned {len(all_events)} raw event(s) across {len(cals)} calendars")
    return _dedup_and_union(all_events)


def _dedup_and_union(raw_events: List[Dict]) -> List[Dict]:
    """Group by iCalUID; keep highest-priority copy; union attendee emails across copies.

    Events missing iCalUID are keyed by (calendar_id, event_id) and NOT deduped
    cross-calendar — they pass through as-is.
    """
    groups: Dict[str, Dict] = {}
    for ev in raw_events:
        ical_uid = ev.get("iCalUID")
        if ical_uid:
            key = f"uid::{ical_uid}"
        else:
            key = f"cal::{ev.get('_calendar_id')}::{ev.get('id')}"
        if key not in groups:
            groups[key] = {"canonical": ev, "attendees": set(extract_attendee_emails(ev)),
                           "copies": [ev]}
        else:
            g = groups[key]
            g["attendees"].update(extract_attendee_emails(ev))
            g["copies"].append(ev)
            # Lower priority number wins as canonical
            if ev.get("_priority", 99) < g["canonical"].get("_priority", 99):
                g["canonical"] = ev
    result = []
    for key, g in groups.items():
        c = dict(g["canonical"])
        c["_unioned_attendee_emails"] = sorted(g["attendees"])
        c["_dedup_copies"] = len(g["copies"])
        result.append(c)
    return result


def match_meeting_to_calendar(meeting_data: Dict, email: str = None) -> Optional[Dict]:
    """Match a meeting to calendar events across all configured calendars.

    Backwards-compatible signature. Returns a dict with the D3 expanded shape
    (never returns raw None when meeting_data is valid).
    """
    meeting = meeting_data.get('meeting', {})
    if not meeting:
        print("Error: No meeting data provided", file=sys.stderr)
        return None
    date_str = meeting.get('date') or meeting_data.get('date') or meeting_data.get('content', {}).get('date')
    if not date_str:
        print("Error: No date found in meeting data", file=sys.stderr)
        return None

    cfg = _load_calendar_config()
    time_utc = meeting.get('time_utc')
    has_exact_time = time_utc is not None and str(time_utc) != "None"
    meeting_dt = parse_meeting_datetime(date_str, time_utc)
    window_hours = cfg.get("time_window_hours_exact", 2) if has_exact_time else cfg.get("time_window_hours_approx", 12)
    start_time = meeting_dt - timedelta(hours=window_hours)
    end_time = meeting_dt + timedelta(hours=window_hours)
    time_min = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    time_max = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    print(f"Querying multi-cal for: {meeting.get('title', 'Untitled')} on {meeting.get('date')} at {meeting.get('time_utc')}")
    print(f"Time window: {time_min} to {time_max}")

    events = _query_google_calendar(time_min, time_max, email)
    empty_result = {"event_id": None, "event_ical_uid": None, "confidence": 0.0,
                    "method": "none", "attendee_emails": [], "organizer_email": None,
                    "source_calendar": None}
    if not events:
        print("No calendar events found in time window")
        return empty_result

    print(f"Multi-cal returned {len(events)} deduplicated event(s)")
    match = find_best_match(meeting, events)
    if not match:
        print("No suitable calendar matches found")
        return empty_result

    ev = match.get("event_data", {})
    organizer = ev.get("organizer", {}) if isinstance(ev.get("organizer"), dict) else {}
    return {
        "event_id": match["event_id"],
        "event_ical_uid": ev.get("iCalUID"),
        "confidence": match["confidence"],
        "method": match["method"],
        "attendee_emails": ev.get("_unioned_attendee_emails", match["attendee_emails"]),
        "organizer_email": (organizer.get("email") if organizer else None),
        "source_calendar": ev.get("_calendar_id"),
    }


def main():
    parser = argparse.ArgumentParser(description='Match meetings to calendar events')
    parser.add_argument('manifest_file', help='Path to meeting manifest JSON file')
    parser.add_argument('--email', help='Google Calendar account email to use')
    parser.add_argument('--output', help='Output file for calendar match results')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Read manifest file
    try:
        with open(args.manifest_file, 'r') as f:
            manifest_data = json.load(f)
    except Exception as e:
        print(f"Error reading manifest file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Perform calendar matching
    match_result = match_meeting_to_calendar(manifest_data, args.email)
    
    if match_result:
        print(f"\nCalendar Match Found:")
        print(f"  Event ID: {match_result['event_id']}")
        print(f"  Confidence: {match_result['confidence']}")
        print(f"  Method: {match_result['method']}")
        print(f"  Attendee Emails: {', '.join(match_result['attendee_emails'])}")
        
        # Save results if output specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(match_result, f, indent=2)
            print(f"\nResults saved to: {args.output}")
        
        # Exit code 0 for successful match
        sys.exit(0)
    else:
        print("No calendar match found")
        
        # Save empty result if output specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(None, f)
        
        # Exit code 1 for no match (not an error, just no result)
        sys.exit(1)


if __name__ == '__main__':
    main()