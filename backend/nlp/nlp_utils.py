import spacy
import re
import datetime
from typing import Optional, Dict, Any
try:
    from dateparser.search import search_dates
except Exception:
    search_dates = None

try:
    nlp = spacy.load("en_core_web_sm")
    _SPACY_AVAILABLE = True
except Exception:
    try:
        nlp = spacy.blank("en")
    except Exception:
        nlp = None
    _SPACY_AVAILABLE = False

def parse_command(user_input: str):
    if not _SPACY_AVAILABLE or nlp is None:
        text = user_input.lower().strip()
        action = None
        target = None
        extra = None

        verbs = ["show", "list", "delete", "add", "create", "run"]
        nouns = ["task", "tasks", "reminder", "reminders", "log", "logs", "history", "conversation", "conversations", "note", "notes"]
        for v in verbs:
            if text.startswith(v + " ") or (" " + v + " ") in text:
                action = v
                break
        for n in nouns:
            if n in text:
                target = n.rstrip("s")
                break
        if "deleted" in text:
            extra = "deleted"
        elif "completed" in text:
            extra = "completed"
        return action, target, extra


def _parse_duration_seconds(text: str) -> Optional[int]:
    text = (text or '').lower()
    m = re.search(r"for\s+(?P<num>\d+)\s*(sec|second|seconds|s)\b", text)
    if m:
        return int(m.group('num'))
    m = re.search(r"for\s+(?P<num>\d+)\s*(min|mins|minute|minutes|m)\b", text)
    if m:
        return int(m.group('num')) * 60
    return None


def _extract_datetime(text: str) -> Optional[datetime.datetime]:
    if not search_dates:
        return None
    try:
        results = search_dates(text, settings={
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': datetime.datetime.now()
        })
    except Exception:
        results = None
    if not results:
        return None
    _, dt = results[0]
    if isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime):
        dt = datetime.datetime.combine(dt, datetime.datetime.now().time())
    return dt.replace(second=0, microsecond=0)


def parse_intent(user_input: str) -> Optional[Dict[str, Any]]:
    if not user_input:
        return None
    text = user_input.strip()
    lower = text.lower()

    # RUN command
    if lower.startswith("run "):
        return {"intent": "RUN_CMD", "params": {"command": text[4:].strip()}}

    # Reminder detection
    if ("remind" in lower) or ("rmind" in lower):
        when = _extract_datetime(text)
        cleaned = lower
        for p in ["remind me to ", "remind me ", "remind ", "rmind me ", "rmind "]:
            if cleaned.startswith(p):
                cleaned = cleaned[len(p):]
                break
        for tok in [" at ", " on ", " by ", " today ", " tomorrow "]:
            cleaned = cleaned.replace(tok, " ")
        cleaned = cleaned.strip()
        if cleaned.startswith('to '):
            cleaned = cleaned[3:]
        if not cleaned:
            cleaned = text
        return {"intent": "REMINDER", "params": {"text": cleaned, "when": when}}

    # Show apps
    if lower in ["show apps", "list apps", "show applications"]:
        return {"intent": "SHOW_APPS", "params": {}}

    # Block app(s)
    if lower.startswith("block "):
        seconds = _parse_duration_seconds(lower)
        m = re.search(r"block\s+(?P<name>.+?)(?:\s+for\s+\d+\s*\w+)?$", text, re.IGNORECASE)
        names = []
        if m:
            name = m.group('name').strip()
            if name:
                names = [name]
        return {"intent": "BLOCK_APP", "params": {"names": names, "seconds": seconds or 30}}

    # Tasks
    if lower.startswith("add task "):
        return {"intent": "TASK_ADD", "params": {"title": text[9:].strip()}}
    if lower in ["show tasks", "list tasks", "show task", "list task"]:
        return {"intent": "TASK_SHOW", "params": {}}
    if lower.startswith("delete task "):
        return {"intent": "TASK_DELETE", "params": {"identifier": text[12:].strip()}}

    # Reminders and history views
    if lower == "show reminders":
        return {"intent": "SHOW_REMINDERS", "params": {}}
    if lower == "show conversations":
        return {"intent": "SHOW_CONVERSATIONS", "params": {}}
    if lower == "show history":
        return {"intent": "SHOW_HISTORY", "params": {}}

    return None

    doc = nlp(user_input.lower())

    action = None
    target = None
    extra = None

    for token in doc:
        if token.pos_ == "VERB":
            action = token.lemma_
        if token.pos_ == "NOUN":
            target = token.text
        if token.text in ["deleted", "recent", "completed"]:
            extra = token.text

    if "deleted" in user_input.lower():
        extra = "deleted"
    elif "recent deleted" in user_input.lower():
        extra = "recent deleted"
    elif "completed" in user_input.lower():
        extra = "completed"

    return action, target, extra
