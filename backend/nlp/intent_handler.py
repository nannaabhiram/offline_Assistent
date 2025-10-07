import re
import spacy
from datetime import date

nlp = spacy.load("en_core_web_sm")

def handle_intent(user_input):
    doc = nlp(user_input.lower())

    # --- Detect Add Task ---
    if "add" in [token.lemma_ for token in doc] and "task" in user_input.lower():
        task_text = user_input.replace("add task", "").strip()
        if not task_text:
            return "What task would you like to add?"
        # Task will be added by main.py logic
        return f"Task '{task_text}' added."

    return "I'm not sure how to handle that yet."
