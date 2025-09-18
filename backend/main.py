def show_tasks(db, user_id=None):
    cursor = db.cursor()
    if user_id:
        cursor.execute(
            "SELECT id, title, status, due_date FROM tasks WHERE user_id = %s ORDER BY id DESC LIMIT 20",
            (user_id,),
        )
    else:
        cursor.execute("SELECT id, title, status, due_date FROM tasks ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    print("\n--- Tasks ---")
    print(f"{'ID':<5} {'Title':<30} {'Status':<10} {'Due Date':<20}")
    print("-"*70)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<30} {row[2]:<10} {str(row[3]):<20}")
    if not rows:
        print("No tasks found.")


def show_reminders(db):
    cursor = db.cursor()
    cursor.execute("SELECT id, text, remind_time, notified FROM reminders ORDER BY remind_time DESC LIMIT 20")
    rows = cursor.fetchall()
    print("\n--- Reminders ---")
    print(f"{'ID':<5} {'Text':<30} {'Remind Time':<20} {'Notified':<10}")
    print("-"*80)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<30} {str(row[2]):<20} {row[3]:<10}")
    if not rows:
        print("No reminders found.")


def show_conversations(db):
    cursor = db.cursor()
    cursor.execute("SELECT id, user_input, assistant_response, timestamp FROM conversations ORDER BY timestamp DESC LIMIT 20")
    rows = cursor.fetchall()
    print("\n--- Conversations ---")
    print(f"{'ID':<5} {'User Input':<30} {'Assistant Response':<30} {'Timestamp':<20}")
    print("-"*110)
    for row in rows:
        print(f"{row[0]:<5} {row[1][:28]:<30} {row[2][:28]:<30} {str(row[3]):<20}")
    if not rows:
        print("No conversations found.")


import os
import time
import threading
import pyttsx3
import re
import datetime
import getpass
from dotenv import load_dotenv
from nlp.nlp_utils import parse_command
import dateparser

# Local imports
from speech.stt import listen_voice
from ai.brain import ask_ai
from system.control import run_system_command, list_running_apps, block_app_by_name, block_apps_by_names
from db.db_connection import (
    get_db_connection, save_conversation, save_task, log_action, get_system_logs,
    get_deleted_tasks,
    get_or_create_user, get_tasks_for_user_on_date,
    delete_user_by_name,
    create_user_with_password, verify_user_password, user_exists,
    set_user_password, user_has_password
)


def delete_task(db, identifier):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM tasks WHERE id = %s", (identifier,))
        if cursor.rowcount == 0:
            cursor.execute("DELETE FROM tasks WHERE title = %s", (identifier,))
        db.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting task: {e}")
        return False


def delete_reminder(db, identifier):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM reminders WHERE id = %s", (identifier,))
        if cursor.rowcount == 0:
            cursor.execute("DELETE FROM reminders WHERE text = %s", (identifier,))
        db.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting reminder: {e}")
        return False


def fetch_conversation_history(db, limit=10):
    cursor = db.cursor()
    cursor.execute("SELECT user_input, assistant_response, timestamp FROM conversations ORDER BY timestamp DESC LIMIT %s", (limit,))
    return cursor.fetchall()


# Load environment variables (resolve relative to project root)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(project_root, 'config', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Initialize text-to-speech
engine = pyttsx3.init()


def speak(text):
    # Personalize responses with the current user's name, if set
    global current_user_id, current_user_name
    prefix = f"{current_user_name}, " if current_user_id else ""
    say_text = prefix + text
    print(f"Assistant: {say_text}")
    engine.say(say_text)
    engine.runAndWait()


def speak_no_prefix(text):
    """Speak without adding any user-name prefix."""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()


def get_user_input(mode="cli"):
    if mode == "voice":
        return listen_voice()
    else:
        return input("You: ")


def save_reminder(db, text, remind_time):
    cursor = db.cursor()
    cursor.execute("INSERT INTO reminders (text, remind_time) VALUES (%s, %s)", (text, remind_time))
    db.commit()


def check_reminders(db):
    while True:
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        cursor = db.cursor()
        cursor.execute("SELECT id, text, remind_time FROM reminders WHERE remind_time <= %s AND notified = 0", (now,))
        for rid, text, remind_time in cursor.fetchall():
            speak(f"**Reminder:** {text} (scheduled for {remind_time})")
            cursor.execute("UPDATE reminders SET notified = 1 WHERE id = %s", (rid,))
            db.commit()
        time.sleep(60)


def parse_reminder(user_input):
    match = re.match(r"remind me to (.+) at (\d{1,2})(:(\d{2}))? ?(am|pm)?", user_input, re.I)
    if match:
        text = match.group(1)
        hour = int(match.group(2))
        minute = int(match.group(4) or 0)
        ampm = match.group(5)
        now = datetime.datetime.now()
        if ampm:
            if ampm.lower() == "pm" and hour < 12:
                hour += 12
            elif ampm.lower() == "am" and hour == 12:
                hour = 0
        remind_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if remind_time < now:
            remind_time += datetime.timedelta(days=1)
        return text, remind_time

    match_after = re.match(r"remind me to (.+) after (\d{1,2}) ?(am|pm)?", user_input, re.I)
    if match_after:
        text = match_after.group(1)
        hour = int(match_after.group(2))
        ampm = match_after.group(3)
        now = datetime.datetime.now()
        if ampm:
            if ampm.lower() == "pm" and hour < 12:
                hour += 12
            elif ampm.lower() == "am" and hour == 12:
                hour = 0
        remind_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if remind_time < now:
            remind_time += datetime.timedelta(days=1)
        remind_time += datetime.timedelta(minutes=30)
        return text, remind_time

    return None, None


def handle_delete_command(user_input: str):
    user_input = user_input.lower()

    if "task" in user_input:
        return "Delete task by ID or title is supported. Deleting the most recent task is not implemented."

    elif "reminder" in user_input or "note" in user_input:
        return "Delete reminder by ID or text is supported. Deleting the most recent reminder is not implemented."

    elif "log" in user_input or "system" in user_input:
        return "Delete log by ID is supported. Deleting the most recent log is not implemented."

    else:
        return "Sorry, I didn’t understand what to delete."


current_user_name = "Abhiram"   # default user
current_user_id = None  # defer DB-backed user creation until runtime

def switch_user(db, name):
    """Switch or create user context."""
    global current_user_id, current_user_name
    user_id = get_or_create_user(name)
    current_user_id = user_id
    current_user_name = name
    return user_id, name


def main():
    db = get_db_connection()
    if not db:
        print("❌ Database connection failed. Exiting.")
        return
    
    # Initialize default user context if not set
    global current_user_id, current_user_name
    if current_user_id is None:
        # Ask to choose existing user or create new
        from db.db_connection import get_all_users
        users = get_all_users()
        if users:
            print("\nAvailable users:")
            for idx, u in enumerate(users, start=1):
                print(f"  {idx}. {u['name']}")
            choice = input("Choose user number or 'n' to create new [1]: ").strip()
            if choice.lower() == 'n':
                name = input("Enter new user name: ").strip().capitalize() or current_user_name
                # Set password with confirmation
                while True:
                    pwd1 = getpass.getpass("Set password: ")
                    pwd2 = getpass.getpass("Confirm password: ")
                    if pwd1 != pwd2:
                        print("Passwords do not match. Try again.")
                        continue
                    break
                ok, msg, uid_new = create_user_with_password(name, pwd1)
                if not ok:
                    print(f"Assistant: {msg}")
                    uid, uname = switch_user(db, current_user_name)
                else:
                    uid, uname = switch_user(db, name)
            else:
                try:
                    n = int(choice) if choice else 1
                    n = max(1, min(n, len(users)))
                    name = users[n-1]['name']
                    uid, uname = switch_user(db, name)
                except ValueError:
                    uid, uname = switch_user(db, current_user_name)
        else:
            name = input(f"Enter your name [{current_user_name}]: ").strip().capitalize() or current_user_name
            # No users exist yet, force password creation path
            while True:
                pwd1 = getpass.getpass("Set password: ")
                pwd2 = getpass.getpass("Confirm password: ")
                if pwd1 != pwd2:
                    print("Passwords do not match. Try again.")
                    continue
                break
            ok, msg, uid_new = create_user_with_password(name, pwd1)
            if not ok:
                print(f"Assistant: {msg}")
                uid, uname = switch_user(db, current_user_name)
            else:
                uid, uname = switch_user(db, name)
    
    speak("Hello! Your offline AI assistant is ready.")
    
    mode = input("Choose mode (cli/voice): ").strip().lower()
    if mode not in ["cli", "voice"]:
        mode = "cli"
    
    # Tick callback for audible countdowns in voice mode
    def tick_cb(remaining: int, total: int, label: str):
        try:
            if mode == "voice":
                # Keep it short to avoid overlapping speech
                if remaining == total or remaining % 5 == 0 or remaining <= 3:
                    speak_no_prefix(f"{label}: {remaining} seconds remaining")
        except Exception:
            pass

    # Auto-block watcher using ALWAYS_BLOCK_APPS and ALWAYS_BLOCK_DURATION from env
    always_block = os.getenv("ALWAYS_BLOCK_APPS", "").strip()
    always_block_duration = int(os.getenv("ALWAYS_BLOCK_DURATION", "30") or 30)
    if always_block:
        targets = [p.strip() for p in always_block.split(',') if p.strip()]
        if targets:
            def _auto_block_watcher():
                backoff_until = 0
                while True:
                    try:
                        apps = list_running_apps()
                        # Determine which target names are currently present (substring or exact case-insensitive)
                        present = []
                        low_apps = [a.lower() for a in apps]
                        for t in targets:
                            tlow = t.lower()
                            # match by exact name or substring present in any running app
                            matched = None
                            for idx, la in enumerate(low_apps):
                                if la == tlow or tlow in la:
                                    matched = apps[idx]
                                    break
                            if matched:
                                present.append(matched)
                        if present and time.time() >= backoff_until:
                            result = block_apps_by_names(present, always_block_duration)
                            log_action(f"Auto-blocked apps: {present} for {always_block_duration}s - {result}")
                            backoff_until = time.time() + always_block_duration + 2
                    except Exception as e:
                        print("Auto-block watcher error:", e)
                    time.sleep(5)
            watcher = threading.Thread(target=_auto_block_watcher, daemon=True)
            watcher.start()
        
    while True:
        try:
            user_input = get_user_input(mode)
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "bye"]:
                speak("Goodbye!")
                break

            # --- NEW: User switching ---
            if user_input.lower().startswith("i am "):
                name = user_input[5:].strip().capitalize()
                if not user_exists(name):
                    # Create user with password
                    while True:
                        pwd1 = getpass.getpass("Set password for new user: ")
                        pwd2 = getpass.getpass("Confirm password: ")
                        if pwd1 != pwd2:
                            print("Passwords do not match. Try again.")
                            continue
                        break
                    ok, msg, _uid = create_user_with_password(name, pwd1)
                    if not ok:
                        speak(msg)
                        continue
                uid, uname = switch_user(db, name)
                speak(f"Hello {uname}, I’ll remember you.")
                continue

            # Add/switch user commands
            if user_input.lower().startswith("add user "):
                name = user_input[9:].strip().capitalize()
                if not name:
                    speak("Please specify a name.")
                    continue
                if user_exists(name):
                    uid, uname = switch_user(db, name)
                    speak(f"User '{uname}' already exists. Switched to this user.")
                    continue
                # Create new user with password
                while True:
                    pwd1 = getpass.getpass("Set password for new user: ")
                    pwd2 = getpass.getpass("Confirm password: ")
                    if pwd1 != pwd2:
                        print("Passwords do not match. Try again.")
                        continue
                    break
                ok, msg, _uid = create_user_with_password(name, pwd1)
                if ok:
                    uid, uname = switch_user(db, name)
                    speak(f"User '{uname}' created and set as current user.")
                else:
                    speak(msg)
                continue

            if user_input.lower().startswith("switch user "):
                name = user_input[12:].strip().capitalize()
                if not user_exists(name):
                    while True:
                        pwd1 = getpass.getpass("Set password for new user: ")
                        pwd2 = getpass.getpass("Confirm password: ")
                        if pwd1 != pwd2:
                            print("Passwords do not match. Try again.")
                            continue
                        break
                    ok, msg, _uid = create_user_with_password(name, pwd1)
                    if not ok:
                        speak(msg)
                        continue
                uid, uname = switch_user(db, name)
                speak(f"Switched to user '{uname}'.")
                continue

            # Support variants: "switch to <name>", "switch <name>", "use <name>", common typo "swich"
            lower = user_input.lower()
            if lower.startswith("switch to "):
                name = user_input[10:].strip().capitalize()
                if not user_exists(name):
                    while True:
                        pwd1 = getpass.getpass("Set password for new user: ")
                        pwd2 = getpass.getpass("Confirm password: ")
                        if pwd1 != pwd2:
                            print("Passwords do not match. Try again.")
                            continue
                        break
                    ok, msg, _uid = create_user_with_password(name, pwd1)
                    if not ok:
                        speak(msg)
                        continue
                uid, uname = switch_user(db, name)
                speak(f"Switched to user '{uname}'.")
                continue
            if lower.startswith("switch "):
                name = user_input[7:].strip().capitalize()
                if not user_exists(name):
                    while True:
                        pwd1 = getpass.getpass("Set password for new user: ")
                        pwd2 = getpass.getpass("Confirm password: ")
                        if pwd1 != pwd2:
                            print("Passwords do not match. Try again.")
                            continue
                        break
                    ok, msg, _uid = create_user_with_password(name, pwd1)
                    if not ok:
                        speak(msg)
                        continue
                uid, uname = switch_user(db, name)
                speak(f"Switched to user '{uname}'.")
                continue
            if lower.startswith("use "):
                name = user_input[4:].strip().capitalize()
                if not user_exists(name):
                    while True:
                        pwd1 = getpass.getpass("Set password for new user: ")
                        pwd2 = getpass.getpass("Confirm password: ")
                        if pwd1 != pwd2:
                            print("Passwords do not match. Try again.")
                            continue
                        break
                    ok, msg, _uid = create_user_with_password(name, pwd1)
                    if not ok:
                        speak(msg)
                        continue
                uid, uname = switch_user(db, name)
                speak(f"Using user '{uname}'.")
                continue
            if lower.startswith("swich ") or lower.startswith("swich to "):
                # common typo handling
                name = user_input.split(None, 1)[1].replace('to', '', 1).strip().capitalize() if len(user_input.split()) > 1 else current_user_name
                if not user_exists(name):
                    while True:
                        pwd1 = getpass.getpass("Set password for new user: ")
                        pwd2 = getpass.getpass("Confirm password: ")
                        if pwd1 != pwd2:
                            print("Passwords do not match. Try again.")
                            continue
                        break
                    ok, msg, _uid = create_user_with_password(name, pwd1)
                    if not ok:
                        speak(msg)
                        continue
                uid, uname = switch_user(db, name)
                speak(f"Switched to user '{uname}'.")
                continue

            # Hardcoded creator response regardless of selected user
            lower = user_input.lower().strip()
            if any(phrase in lower for phrase in [
                "how made you",
                "how were you made",
                "who made you",
                "who created you",
                "how created you",
                "who build you",
                "who built you",
                "who developed you",
                "how were u made",
                "who created u"
            ]):
                response = (
                    "I was created by Abhiram. I'm an offline AI assistant built with Python "
                    "and local libraries to run without the internet."
                )
                # Respond without any user-name prefix
                speak_no_prefix(response)
                save_conversation(db, user_input, response)
                continue

            # --- Ensure user is set ---
            if not current_user_id:
                speak("Please tell me your name first. Say: I am Abhiram")
                continue

            # Fast-path handlers for common commands
            if user_input.lower().strip() in [
                "show tasks", "show task", "list tasks", "list task"
            ]:
                show_tasks(db, current_user_id)
                continue

            # List running apps
            if user_input.lower().strip() in ["show apps", "list apps", "show applications"]:
                apps = list_running_apps()
                if apps:
                    print("\n--- Running Apps ---")
                    for i, a in enumerate(apps, 1):
                        print(f"{i:>2}. {a}")
                else:
                    print("No user applications detected.")
                continue

            # Block multiple apps interactively: shows list, lets you pick multiple, asks duration
            lower_cmd = user_input.lower().strip()
            if lower_cmd in ["block apps", "block applications", "block multiple apps"] or lower_cmd.startswith("block apps"):
                apps = list_running_apps()
                if not apps:
                    speak("I couldn't find any running apps to block.")
                    continue
                print("\nSelect one or more apps to block (comma-separated):")
                for i, a in enumerate(apps, 1):
                    print(f"  {i}. {a}")
                sel = input("Enter numbers or names (comma-separated): ").strip()
                raw_parts = [p.strip() for p in sel.split(',') if p.strip()]
                chosen = []
                for p in raw_parts:
                    if p.isdigit():
                        idx = max(1, min(int(p), len(apps)))
                        chosen.append(apps[idx-1])
                    else:
                        chosen.append(p)
                # Remove duplicates while preserving order
                seen = set()
                chosen_unique = []
                for name in chosen:
                    key = name.lower()
                    if key not in seen:
                        seen.add(key)
                        chosen_unique.append(name)
                if not chosen_unique:
                    speak("No valid app selection provided.")
                    continue
                dur_text = input("Enter block duration in seconds [30]: ").strip()
                try:
                    sec = int(dur_text) if dur_text else 30
                except ValueError:
                    sec = 30
                result = block_apps_by_names(chosen_unique, sec, tick_callback=tick_cb, label=", ".join(chosen_unique[:2]) + (" ..." if len(chosen_unique) > 2 else ""))
                speak(result)
                try:
                    log_action(f"Blocked apps: {chosen_unique} for {sec}s")
                except Exception:
                    pass
                continue

            # Block app for N seconds: e.g., "block chrome for 30 seconds"
            if user_input.lower().startswith("block "):
                import re
                text = user_input.strip()
                m = re.search(r"block\s+(?P<app>.+?)\s+for\s+(?P<sec>\d+)\s*(second|seconds|sec)?", text, re.IGNORECASE)
                if m:
                    app = m.group('app').strip()
                    sec = int(m.group('sec'))
                    result = block_app_by_name(app, sec, tick_callback=tick_cb, label=app)
                    speak(result)
                    try:
                        log_action(f"Blocked app: {app} for {sec}s")
                    except Exception:
                        pass
                    continue
                # If no app parsed but has seconds
                m2 = re.search(r"for\s+(?P<sec>\d+)\s*(second|seconds|sec)", text, re.IGNORECASE)
                if m2:
                    sec = int(m2.group('sec'))
                else:
                    # default 30 seconds if not provided
                    sec = 30
                # Ask user to pick an app
                apps = list_running_apps()
                if not apps:
                    speak("I couldn't find any running apps to block.")
                    continue
                print("\nSelect an app to block:")
                for i, a in enumerate(apps, 1):
                    print(f"  {i}. {a}")
                choice = input(f"Enter number or name to block for {sec} seconds: ").strip()
                if choice.isdigit():
                    idx = max(1, min(int(choice), len(apps)))
                    app = apps[idx-1]
                else:
                    app = choice
                result = block_app_by_name(app, sec, tick_callback=tick_cb, label=app)
                speak(result)
                try:
                    log_action(f"Blocked app: {app} for {sec}s")
                except Exception:
                    pass
                continue

            # Parse command
            action, target, extra = parse_command(user_input)

            # Show tasks done today (for active user)
            if ("what task i have done today" in user_input.lower() or
                "show my todays tasks" in user_input.lower() or
                ("today" in user_input.lower() and "task" in user_input.lower())):
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                tasks = get_tasks_for_user_on_date(current_user_id, today)
                if tasks:
                    print(f"\nTasks done by {current_user_name} on {today}:")
                    for t in tasks:
                        print(f"- {t['title']} ({t['status']})")
                else:
                    print(f"No tasks found for {current_user_name} on {today}.")
                continue

            # Add task for active user
            if user_input.startswith("add task "):
                task = user_input[9:]
                save_task(db, task, user_id=current_user_id)
                log_action(f"{current_user_name} added task: '{task}'")
                speak(f"Task '{task}' added for {current_user_name}.")
                continue

            # Deleted tasks
            if action == "show" and target == "task" and (extra == "deleted" or "deleted" in user_input.lower()):
                deleted_tasks = get_deleted_tasks()
                if deleted_tasks:
                    print("\n--- Recent Deleted Tasks ---")
                    print(f"{'ID':<5} {'Title':<30} {'Status':<10} {'Due Date':<20} {'Deleted At':<20}")
                    print("-"*100)
                    for row in deleted_tasks:
                        print(f"{row['id']:<5} {row['title']:<30} {row['status']:<10} {str(row.get('due_date', '')):<20} {str(row.get('deleted_at', '')):<20}")
                else:
                    print("No deleted tasks found.")

            elif action == "show" and target == "task":
                show_tasks(db, current_user_id)

            elif user_input.lower() == "show reminders":
                show_reminders(db)

            elif user_input.lower() == "show conversations":
                show_conversations(db)

            elif user_input.lower() == "show history":
                history = fetch_conversation_history(db)
                if history:
                    print("\n--- Conversation History ---")
                    for user, assistant, ts in reversed(history):
                        print(f"[{ts}] You: {user}")
                        print(f"[{ts}] Assistant: {assistant}\n")
                else:
                    print("No previous conversations found.")

            elif user_input.startswith("run "):
                result = run_system_command(user_input[4:])
                speak(result)


            # Set/change password for a user
            elif user_input.lower().startswith("set password "):
                raw = user_input[13:].strip()
                if not raw:
                    speak("Please provide a username, e.g., 'set password John'.")
                    continue
                name = raw.capitalize()
                if not user_exists(name):
                    speak(f"User '{name}' not found.")
                    continue
                # If user already has a password, ask for current password
                if user_has_password(name):
                    current = getpass.getpass("Enter current password: ")
                    if not verify_user_password(name, current):
                        speak("Current password incorrect.")
                        continue
                # Set new password
                while True:
                    pwd1 = getpass.getpass("New password: ")
                    pwd2 = getpass.getpass("Confirm new password: ")
                    if pwd1 != pwd2:
                        print("Passwords do not match. Try again.")
                        continue
                    break
                ok, msg = set_user_password(name, pwd1)
                speak(msg if ok else msg)
                continue

            elif user_input.lower() in ["set my password", "change my password", "change password"]:
                if not current_user_id:
                    speak("No active user. Please introduce yourself first, e.g., 'I am Abhiram'.")
                    continue
                name = current_user_name
                if user_has_password(name):
                    current = getpass.getpass("Enter current password: ")
                    if not verify_user_password(name, current):
                        speak("Current password incorrect.")
                        continue
                while True:
                    pwd1 = getpass.getpass("New password: ")
                    pwd2 = getpass.getpass("Confirm new password: ")
                    if pwd1 != pwd2:
                        print("Passwords do not match. Try again.")
                        continue
                    break
                ok, msg = set_user_password(name, pwd1)
                speak(msg if ok else msg)
                continue

            elif user_input.lower().startswith("delete user "):
                # Example: "delete user John"
                name = user_input[12:].strip().capitalize()
                if not name:
                    speak("Please specify the user name to delete.")
                    continue
                # Ask for that user's password without echo
                pwd = getpass.getpass("Enter this user's password to confirm deletion: ")
                if not verify_user_password(name, pwd):
                    speak("Authentication failed. User deletion cancelled.")
                    continue
                # Second safety check: require typing the username exactly
                confirm_text = input(f"Type the username '{name}' to confirm deletion: ").strip()
                if confirm_text.lower() != name.lower():
                    speak("Confirmation did not match. User deletion cancelled.")
                    continue
                ok, msg = delete_user_by_name(name)
                if ok:
                    # If we deleted the active user, clear context
                    if current_user_name.lower() == name.lower():
                        current_user_id = None
                        speak(f"{msg} Please select a user again.")
                    else:
                        speak(msg)
                    try:
                        log_action(f"Deleted user: {name}")
                    except Exception:
                        pass
                else:
                    speak(msg)

            elif user_input.lower().startswith("delete task "):
                identifier = user_input[12:].strip()
                success = delete_task(db, identifier)
                if success:
                    log_action(f"Deleted task id {identifier}")
                    speak(f"Task '{identifier}' deleted.")
                else:
                    speak(f"Task '{identifier}' not found.")

            elif user_input.lower().startswith("delete reminder "):
                speak("Delete reminder by ID or text is not implemented.")

            elif user_input.lower().startswith("remind me to"):
                text, remind_time = parse_reminder(user_input)
                if text and remind_time:
                    save_reminder(db, text, remind_time)
                    speak(f"Reminder saved for {remind_time.strftime('%I:%M %p')}: {text}")
                else:
                    speak("Sorry, I couldn't understand the reminder time.")

            elif user_input.lower() == "show system logs":
                logs = get_system_logs()
                if logs:
                    print("Assistant: Here are the latest system logs:")
                    for log in logs:
                        print(f"[{log['timestamp']}] {log['action']} - {log['status']}")
                else:
                    print("Assistant: No logs found.")

            elif action == "add" and target in ["reminder", "note"]:
                text = user_input.replace("add reminder", "").replace("create reminder", "").strip()
                if text:
                    parsed_date = dateparser.parse(text)
                    if parsed_date:
                        title = text
                        due_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        title = text
                        due_date = None
                    print(f"Assistant: Reminder '{title}' feature is not implemented.")
                else:
                    print("Assistant: Please specify the reminder.")

            else:
                response = ask_ai(user_input)
                speak(response)
                save_conversation(db, user_input, response)
        
        except KeyboardInterrupt:
            speak("Goodbye!")
            break
        except Exception as e:
            print("⚠️ Error:", e)
            speak("Something went wrong.")
            time.sleep(1)


if __name__ == "__main__":
    main()
