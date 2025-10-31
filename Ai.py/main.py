import re
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os
import dateparser
import sys
import time
import itertools
from dataclasses import dataclass, asdict

# ---------- Constants ----------
CALENDAR_FILE = "calendar_events.json"
DEFAULT_PARTICIPANTS = ["Parth", "Nitish", "Atul"]
DEFAULT_DURATION = 30  # minutes

# Regex patterns
ADD_PATTERN = re.compile(r"add (.+?) on (.+?)(?: for (\d+)\s*minutes?)?(?: with (.+))?$", re.I)
VIEW_PATTERN = re.compile(r"what(?:'s| is) happening on (.+)", re.I)
DELETE_PATTERN = re.compile(r"delete event (.+)", re.I)

# ---------- Dataclass ----------
@dataclass
class Event:
    id: str
    title: str
    start: str
    end: str
    participants: List[str]

# ---------- Load & Save ----------
def load_events() -> List[Event]:
    if os.path.exists(CALENDAR_FILE):
        try:
            with open(CALENDAR_FILE, "r") as f:
                data = json.load(f)
                return [Event(**e) for e in data]
        except json.JSONDecodeError:
            return []
    return []

def save_events(events: List[Event]):
    with open(CALENDAR_FILE, "w") as f:
        json.dump([asdict(e) for e in events], f, indent=2)

events_store: List[Event] = load_events()

# ---------- Utility Functions ----------
def parse_to_datetime(date_text: str) -> datetime:
    dt = dateparser.parse(date_text, settings={"PREFER_DATES_FROM": "future"})
    if not dt:
        raise ValueError(f"❌ Could not parse date/time from '{date_text}'")
    return dt

def animated_print(text: str, delay: float = 0.05):
    """Simulate typing animation"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()  # newline

def spinner(seconds: float = 1.0):
    """Simple console spinner animation"""
    for c in itertools.cycle('|/-\\'):
        sys.stdout.write(f'\r⏳ Processing {c}')
        sys.stdout.flush()
        time.sleep(0.1)
        seconds -= 0.1
        if seconds <= 0:
            break
    sys.stdout.write('\r✔ Done!      \n')

# ---------- Core Functions ----------
def schedule_event(title: str, datetime_text: str, duration_minutes: int = DEFAULT_DURATION, participants: Optional[List[str]] = None) -> str:
    start_dt = parse_to_datetime(datetime_text)
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    participants = participants or DEFAULT_PARTICIPANTS
    event_id = str(uuid.uuid4())

    event = Event(
        id=event_id,
        title=title,
        start=start_dt.isoformat(),
        end=end_dt.isoformat(),
        participants=participants
    )

    # Conflict detection
    conflicts = [
        e for e in events_store
        if datetime.fromisoformat(e.start) < end_dt and datetime.fromisoformat(e.end) > start_dt
    ]
    if conflicts:
        conflict_titles = ", ".join([e.title for e in conflicts])
        return f"⚠ Conflict detected with event(s): {conflict_titles}"

    spinner(0.8)  # running animation
    events_store.append(event)
    save_events(events_store)
    return f"✅ Event '{title}' scheduled on {start_dt.strftime('%Y-%m-%d %H:%M')} for {duration_minutes} minutes with {', '.join(participants)}"

def list_events(date_text: Optional[str] = None) -> str:
    if date_text:
        target_date = parse_to_datetime(date_text).date()
        events = [e for e in events_store if datetime.fromisoformat(e.start).date() == target_date]
        if not events:
            return f"ℹ No events scheduled for {target_date}"
    else:
        events = events_store
        if not events:
            return "ℹ No events scheduled."
    
    events = sorted(events, key=lambda e: datetime.fromisoformat(e.start))
    lines = []
    for e in events:
        lines.append(
            f"🗓 {e.id}: {e.title} on {datetime.fromisoformat(e.start).strftime('%Y-%m-%d %H:%M')} "
            f"to {datetime.fromisoformat(e.end).strftime('%H:%M')} with {', '.join(e.participants)}"
        )
    return "\n".join(lines)

def remove_event(event_id: str) -> str:
    for e in events_store:
        if e.id == event_id:
            spinner(0.5)  # running animation
            events_store.remove(e)
            save_events(events_store)
            return f"🗑 Deleted event {event_id}: {e.title}"
    return f"ℹ No event found with id {event_id}"

# ---------- Command Processing ----------
def handle_command(command: str) -> str:
    command = command.strip()

    # Add event
    m = ADD_PATTERN.match(command)
    if m:
        title = m.group(1).strip()
        dt_text = m.group(2).strip()
        duration = int(m.group(3)) if m.group(3) else DEFAULT_DURATION
        participants = [p.strip() for p in m.group(4).split(",")] if m.group(4) else None
        try:
            return schedule_event(title, dt_text, duration, participants)
        except Exception as e:
            return str(e)

    # View specific day
    m = VIEW_PATTERN.match(command)
    if m:
        return list_events(m.group(1).strip())

    # View all
    if command.lower() == "view all events":
        return list_events()

    # Delete by id
    m = DELETE_PATTERN.match(command)
    if m:
        return remove_event(m.group(1).strip())

    return (
        "❌ Command not recognized. Examples:\n"
        "- add meeting on tomorrow at 10am for 60 minutes with Parth, Nitish, Atul\n"
        "- what's happening on 2025-10-16\n"
        "- view all events\n"
        "- delete event <uuid>"
    )

# ---------- Main ----------
def main():
    print("🤖 AI Calendar Agent (JSON + UUID) — Type a command (or 'exit' to quit)")
    while True:
        cmd = input(">>> ").strip()
        if cmd.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break
        animated_print(handle_command(cmd), delay=0.01)

if _name_ == "_main_":
    main()