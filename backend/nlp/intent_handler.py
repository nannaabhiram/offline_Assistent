import re
import spacy
from datetime import date
from backend.db import get_or_create_user, add_task, count_tasks_for_user_on_date

nlp = spacy.load("en_core_web_sm")

# Keep track of current active user in memory
current_user_id = None
current_user_name = None

def handle_intent(user_input):
    global current_user_id, current_user_name

    doc = nlp(user_input.lower())

    # --- Detect "I am <name>" ---
    match = re.match(r"i am ([a-z]+)", user_input.lower())
    if match:
        name = match.group(1).capitalize()
        user_id = get_or_create_user(name)
        current_user_id = user_id
        current_user_name = name
        return f"Hello {name}, I’ll remember you."

    # --- Check if user is set ---
    if not current_user_id:
        return "Please tell me who you are first by saying 'I am <your name>'."

    # --- Detect Add Task ---
    if "add" in [token.lemma_ for token in doc] and "task" in user_input.lower():
        task_text = user_input.replace("add task", "").strip()
        if not task_text:
            return "What task would you like to add?"
        add_task(current_user_id, task_text)
        return f"Task '{task_text}' added for {current_user_name}."

    # --- Detect Count Tasks Today ---
    if "how many" in user_input.lower() and "task" in user_input.lower() and "today" in user_input.lower():
        today = date.today()
        count = count_tasks_for_user_on_date(current_user_id, today)
        return f"{current_user_name}, you have added {count} tasks today."

    return "I’m not sure how to handle that yet."
