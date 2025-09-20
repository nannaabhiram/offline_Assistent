import requests
import json
from typing import List, Tuple, Optional


def _format_history(history: List[Tuple[str, str, str]], max_chars: int = 3000) -> str:
    """Format last conversation rows [(user, assistant, ts), ...] into a compact transcript.
    Truncates to approximately max_chars from the end.
    """
    if not history:
        return ""
    parts = []
    # history is likely newest-first; reverse to oldest-first for coherence
    for user, assistant, _ts in reversed(history):
        if user:
            parts.append(f"User: {user}")
        if assistant:
            parts.append(f"Assistant: {assistant}")
    text = "\n".join(parts)
    # Truncate from the left if too long
    if len(text) > max_chars:
        text = text[-max_chars:]
        # Ensure we start at a line break boundary for neatness
        first_nl = text.find("\n")
        if first_nl != -1:
            text = text[first_nl+1:]
    return text


def ask_ai(prompt: str, *, history: Optional[List[Tuple[str, str, str]]] = None,
           system: Optional[str] = None, model: str = "phi3:latest", timeout: int = 20) -> str:
    """Call local LLM with optional short conversation history prepended.

    - history: list of (user, assistant, timestamp)
    - system: instruction string guiding behavior
    - model: ollama model name
    """
    try:
        context = _format_history(history or [])
        sys_text = system or (
            "You are an offline desktop assistant. Answer concisely, refer to prior context if relevant, "
            "and ask clarifying questions when the request is ambiguous."
        )
        composite_prompt = (
            f"[System]\n{sys_text}\n\n"
            + (f"[Recent Conversation]\n{context}\n\n" if context else "")
            + f"[User]\n{prompt}\n\n[Assistant]"
        )
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": composite_prompt},
            stream=True,
            timeout=timeout,
        )
        result = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                result += data.get("response", "")
        return result.strip()
    except requests.exceptions.RequestException as e:
        return f"AI Error: {e}"