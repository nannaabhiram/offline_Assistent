import spacy

# Load the small English model with a safe fallback if the model isn't installed
try:
    nlp = spacy.load("en_core_web_sm")
    _SPACY_AVAILABLE = True
except Exception:
    # Fallback: minimal tokenizer using SpaCy's blank model or a naive split
    try:
        nlp = spacy.blank("en")
    except Exception:
        nlp = None
    _SPACY_AVAILABLE = False

def parse_command(user_input: str):
    """
    Extract intent (verb) and target (noun) from a user's command.
    Returns: (action, target, extra)
    """
    # If SpaCy model isn't available, use a very simple heuristic parser
    if not _SPACY_AVAILABLE or nlp is None:
        text = user_input.lower().strip()
        action = None
        target = None
        extra = None

        # Heuristic: look for common verbs and nouns
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

    doc = nlp(user_input.lower())

    action = None
    target = None
    extra = None

    for token in doc:
        if token.pos_ == "VERB":  # show, list, delete, add
            action = token.lemma_  # normalize to base form
        if token.pos_ == "NOUN":  # task, reminder, log
            target = token.text
        if token.text in ["deleted", "recent", "completed"]:
            extra = token.text

    # Also check for keywords in the raw input for robustness
    if "deleted" in user_input.lower():
        extra = "deleted"
    elif "recent deleted" in user_input.lower():
        extra = "recent deleted"
    elif "completed" in user_input.lower():
        extra = "completed"

    return action, target, extra
