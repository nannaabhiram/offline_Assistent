import os
import time
import threading
import pyttsx3
import re
import datetime
import requests
from dotenv import load_dotenv
from ai.brain import ask_ai
from dateparser.search import search_dates

# Vision and face analysis
from vision.face_analyzer import start_face_analysis, stop_face_analysis, get_current_analysis, detect_user_mood
from nlp.nlp_utils import parse_intent
from system.control import run_system_command, list_running_apps, block_app_by_name, block_apps_by_names
from system.optimized_control import (
    quick_process_kill, execute_fast_command, quick_volume_control,
    quick_brightness_control, quick_power_action, quick_app_launch,
    mute_toggle, lock_screen, wifi_toggle, performance_status, system_status
)
from db.db_connection import (
    get_db_connection, save_conversation, save_task, log_action, get_system_logs,
    get_deleted_tasks, get_tasks_on_date,
    # Memory helpers
    ensure_memories_table, save_memory, get_recent_memories, search_memories, delete_memory_by_id
)

def show_tasks(db):
    cursor = db.cursor()
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


def handle_enhanced_commands(user_input):
    """Handle enhanced system control commands with optimized performance and natural responses"""
    text = user_input.lower().strip()

    # System control commands - using fast optimized functions
    if any(keyword in text for keyword in ["volume", "sound", "audio"]):
        if "up" in text or "increase" in text:
            result = quick_volume_control("up", 10)
            return f"Volume increased to {result}! Let me know if you'd like to adjust it further or try something else."
        elif "down" in text or "decrease" in text:
            result = quick_volume_control("down", 10)
            return f"Volume decreased to {result}! Let me know if you'd like to adjust it further or try something else."
        elif "mute" in text:
            result = mute_toggle()
            return f"Sound toggled to {result}! Let me know if you'd like to adjust the volume or try something else."
        elif "max" in text or "full" in text:
            result = quick_volume_control("set", 100)
            return f"Volume set to maximum {result}! Let me know if you'd like to adjust it or try something else."
        elif "min" in text or "zero" in text:
            result = quick_volume_control("set", 0)
            return f"Volume muted to {result}! Let me know if you'd like to adjust it or try something else."
        else:
            # Extract volume level if specified
            import re
            numbers = re.findall(r'\d+', text)
            if numbers:
                level = min(100, max(0, int(numbers[0])))
                result = quick_volume_control("set", level)
            else:
                result = quick_volume_control("get")
            return f"Volume: {result}. Let me know if you'd like to adjust it further!"

    elif any(keyword in text for keyword in ["brightness", "screen", "display"]):
        if "up" in text or "increase" in text or "brighter" in text:
            result = quick_brightness_control("up", 10)
            return "Screen brightness increased! Let me know if you'd like to adjust it further or try something else."
        elif "down" in text or "decrease" in text or "dimmer" in text:
            result = quick_brightness_control("down", 10)
            return "Screen brightness decreased! Let me know if you'd like to adjust it further or try something else."
        elif "max" in text or "full" in text:
            result = quick_brightness_control("set", 100)
            return "Screen brightness set to maximum! Let me know if you'd like to adjust it or try something else."
        elif "min" in text or "lowest" in text:
            result = quick_brightness_control("set", 10)
            return "Screen brightness set to minimum! Let me know if you'd like to adjust it or try something else."
        else:
            result = quick_brightness_control("get")
            return f"Current brightness is at {result}%. Let me know if you'd like to adjust it!"

    elif any(keyword in text for keyword in ["shutdown", "restart", "sleep", "hibernate", "lock"]):
        if "shutdown" in text or "power off" in text:
            result = quick_power_action("shutdown")
            return "Shutting down your computer. Goodbye!"
        elif "restart" in text or "reboot" in text:
            result = quick_power_action("restart")
            return "Restarting your computer. I'll be here when you get back!"
        elif "sleep" in text:
            result = quick_power_action("sleep")
            return "Putting your computer to sleep. Sweet dreams!"
        elif "hibernate" in text:
            result = quick_power_action("hibernate")
            return "Hibernating your computer. See you later!"
        elif "lock" in text:
            result = lock_screen()
            return "Computer locked! Let me know when you're ready to continue."
        return "Power action completed!"

    elif any(keyword in text for keyword in ["wifi", "wireless", "network"]):
        if "off" in text or "disable" in text:
            result = wifi_toggle("off")
            return "WiFi turned off. Let me know if you'd like to turn it back on or try something else."
        elif "on" in text or "enable" in text:
            result = wifi_toggle("on")
            return "WiFi turned on! Let me know if you'd like to adjust network settings or try something else."
        else:
            result = wifi_toggle("status")
            return f"Network status: {result}. Let me know if you'd like to adjust the connection!"

    elif any(keyword in text for keyword in ["system info", "computer info", "pc info", "hardware", "system status"]):
        result = system_status()
        return f"Here's your system information: {result}. Let me know if you'd like more details about any specific component!"

    elif any(keyword in text for keyword in ["performance", "cpu usage", "memory usage", "disk usage"]):
        result = performance_status()
        return f"Here's your performance status: {result}. Let me know if you'd like to optimize any specific area!"

    elif any(keyword in text for keyword in ["open", "launch", "start"]) and "app" in text:
        # Extract app name from text
        import re
        patterns = [r'(?:open|launch|start)\s+(.+?)(?:\s+app)?(?:\s|$)', r'(?:open|launch|start)\s+app\s+(.+?)(?:\s|$)']
        app_name = None
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                app_name = match.group(1).strip()
                break

        if app_name:
            result = quick_app_launch(app_name)
            return f"Opening {app_name}! Let me know if you'd like to open any other applications."
        else:
            return "I'd be happy to open an application for you! Could you please specify which one?"

    elif any(keyword in text for keyword in ["kill", "close", "terminate"]):
        # Extract app/process name - more flexible patterns
        import re
        patterns = [
            r'(?:kill|close|terminate)\s+(.+?)(?:\s+(?:app|process))?(?:\s|$)',
            r'(?:kill|close|terminate)\s+(?:app|process)\s+(.+?)(?:\s|$)'
        ]
        process_name = None
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                process_name = match.group(1).strip()
                # Skip common words that aren't processes
                if process_name.lower() not in ["app", "application", "program", "process"]:
                    break

        if process_name and process_name.lower() not in ["app", "application", "program", "process"]:
            result = quick_process_kill(process_name)
            return f"Closed {process_name}! Let me know if you'd like to close any other applications."
        else:
            return "I'd be happy to close an application for you! Could you please specify which one?"

    # File operations - using optimized functions
    elif any(keyword in text for keyword in ["create file", "make file"]):
        import re
        match = re.search(r'(?:create|make)\s+file\s+(.+?)(?:\s|$)', text)
        if match:
            file_path = match.group(1).strip()
            result = execute_fast_command("file", action="create", path=file_path)
            return f"File created at {file_path}! Let me know if you'd like to create any other files."
        else:
            return "I'd be happy to create a file for you! Could you please specify the file path?"

    elif any(keyword in text for keyword in ["delete file", "remove file"]):
        import re
        match = re.search(r'(?:delete|remove)\s+file\s+(.+?)(?:\s|$)', text)
        if match:
            file_path = match.group(1).strip()
            result = execute_fast_command("file", action="delete", path=file_path)
            return f"File deleted from {file_path}! Let me know if you'd like to delete any other files."
        else:
            return "I'd be happy to delete a file for you! Could you please specify the file path?"

    # Return None if no enhanced command matched
    return None


def fetch_conversation_history(db, limit=10):
    cursor = db.cursor()
    cursor.execute("SELECT user_input, assistant_response, timestamp FROM conversations ORDER BY timestamp DESC LIMIT %s", (limit,))
    return cursor.fetchall()


def check_ollama_server(timeout=3):
    """Check if Ollama server is running and responsive"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=timeout)
        return response.status_code == 200
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False
    except Exception:
        return False


def wait_for_ollama_server(timeout=10):
    """Wait for Ollama server to become available"""
    start_time = time.time()
    print("🔄 Checking Ollama server availability...")

    while time.time() - start_time < timeout:
        if check_ollama_server():
            print("✅ Ollama server is ready!")
            return True
        print("⏳ Waiting for Ollama server...")
        time.sleep(1)

    print("❌ Ollama server is not available. Please start Ollama server and try again.")
    return False


# Initialize text-to-speech (lazy initialization)
engine = None
tts_lock = threading.Lock()


def get_tts_engine():
    """Get TTS engine with lazy initialization"""
    global engine
    if engine is None:
        try:
            engine = pyttsx3.init()
        except Exception as e:
            print(f"Warning: TTS initialization failed: {e}")
            return None
    return engine


def speak(text):
    print(f"Assistant: {text}")
    try:
        tts_engine = get_tts_engine()
        if tts_engine:
            with tts_lock:
                tts_engine.say(text)
                tts_engine.runAndWait()
    except Exception:
        pass


def speak_no_prefix(text):
    print(f"Assistant: {text}")
    try:
        tts_engine = get_tts_engine()
        if tts_engine:
            with tts_lock:
                tts_engine.say(text)
                tts_engine.runAndWait()
    except Exception:
        pass


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


def parse_reminder_natural(user_input: str):
    if not user_input:
        return None, None
    try:
        results = search_dates(user_input, settings={
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': datetime.datetime.now()
        })
    except Exception:
        results = None
    if not results:
        return None, None
    matched_str, dt = results[0]
    if not isinstance(dt, datetime.datetime):
        dt = datetime.datetime.combine(dt, datetime.datetime.now().time())
    dt = dt.replace(second=0, microsecond=0)

    text = user_input
    text = text.replace(matched_str, " ")
    low = text.lower()
    for prefix in ["remind me to ", "remind me ", "remind "]:
        if low.startswith(prefix):
            text = text[len(prefix):]
            break
    for tok in [" at ", " on ", " by ", " today ", " tomorrow "]:
        text = text.replace(tok, " ")
    text = text.strip().lstrip('to ').strip()
    if not text:
        text = user_input
    return text.strip(), dt


# Memory table check cache
_memory_table_checked = False
_memory_table_lock = threading.Lock()


def main():
    print("🚀 Starting Offline AI Assistant...")

    # Check if Ollama server is available before proceeding
    if not wait_for_ollama_server():
        return

    db = get_db_connection()
    if not db:
        print("❌ Database connection failed. Exiting.")
        return

    # Initialize face analysis (optional)
    face_analysis_active = False
    last_face_id = None
    last_mood = None
    last_mood_confidence = 0.0
    try:
        from vision.face_analyzer import start_face_analysis, stop_face_analysis, get_current_analysis, detect_user_mood
        if start_face_analysis():
            face_analysis_active = True
            print("✅ Face analysis system activated!")
        else:
            print("⚠️ Face analysis system not available (camera not found)")
    except ImportError as e:
        print(f"⚠️ Face analysis not available: {e}")
        face_analysis_active = False
    except Exception as e:
        print(f"⚠️ Face analysis initialization failed: {e}")
        face_analysis_active = False

    mode = input("Choose mode (cli/voice): ").strip().lower()
    if mode not in ["cli", "voice"]:
        mode = "cli"

    # Start reminder watcher in the background
    try:
        reminder_thread = threading.Thread(target=check_reminders, args=(db,), daemon=True)
        reminder_thread.start()
    except Exception as e:
        print("Warning: failed to start reminder watcher:", e)

    # Tick callback for audible countdowns
    def tick_cb(remaining: int, total: int, label: str):
        try:
            if mode == "voice":
                if remaining == total or remaining % 5 == 0 or remaining <= 3:
                    speak_no_prefix(f"{label}: {remaining} seconds remaining")
        except Exception:
            pass

    # Auto-block watcher
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
                        present = []
                        low_apps = [a.lower() for a in apps]
                        for t in targets:
                            tlow = t.lower()
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

            # Get face analysis if available
            current_mood = "neutral"
            if face_analysis_active:
                try:
                    current_mood = detect_user_mood()
                except Exception:
                    current_mood = "neutral"
            lower = user_input.lower().strip()
            if any(phrase in lower for phrase in [
                "how made you", "how were you made", "who made you", "who created you",
                "how created you", "who build you", "who built you", "who developed you",
                "how were u made", "who created u"
            ]):
                response = (
                    "I was created by Abhiram. I'm an offline AI assistant built with Python "
                    "and local libraries to run without the internet."
                )
                speak_no_prefix(response)
                save_conversation(db, user_input, response)
                continue

            # Structured intent routing
            intent_obj = parse_intent(user_input)
            if intent_obj:
                it = intent_obj.get("intent")
                params = intent_obj.get("params", {})

                if it == "RUN_CMD":
                    result = run_system_command(params.get("command", ""))
                    speak(result)
                    continue

                if it == "REMINDER":
                    text = params.get("text")
                    when = params.get("when")
                    if text and when:
                        save_reminder(db, text, when)
                        speak(f"Reminder saved for {when.strftime('%I:%M %p on %b %d')}: {text}")
                    else:
                        speak("I couldn't parse the reminder time.")
                    continue

                if it == "SHOW_APPS":
                    apps = list_running_apps()
                    if apps:
                        print("\n--- Running Apps ---")
                        for i, a in enumerate(apps, 1):
                            print(f"{i:>2}. {a}")
                    else:
                        print("No user applications detected.")
                    continue

                if it == "BLOCK_APP":
                    names = params.get("names") or []
                    sec = int(params.get("seconds") or 30)
                    if not names:
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
                        seen = set(); chosen_unique = []
                        for name in chosen:
                            k = name.lower()
                            if k not in seen:
                                seen.add(k); chosen_unique.append(name)
                        if not chosen_unique:
                            speak("No valid app selection provided.")
                            continue
                        names = chosen_unique
                    if len(names) == 1:
                        result = block_app_by_name(names[0], sec, tick_callback=tick_cb, label=names[0])
                    else:
                        result = block_apps_by_names(names, sec, tick_callback=tick_cb)
                    speak(result)
                    try:
                        log_action(f"Blocked apps: {names} for {sec}s")
                    except Exception:
                        pass
                    continue

                if it == "TASK_ADD":
                    task = params.get("title")
                    if task:
                        save_task(db, task)
                        log_action(f"Added task: '{task}'")
                        speak(f"Task '{task}' added.")
                    else:
                        speak("Please provide a task title.")
                    continue

                if it == "TASK_SHOW":
                    show_tasks(db)
                    continue

                if it == "TASK_DELETE":
                    ident = params.get("identifier")
                    success = delete_task(db, ident)
                    if success:
                        log_action(f"Deleted task: {ident}")
                        speak(f"Task '{ident}' deleted.")
                    else:
                        speak(f"Task '{ident}' not found.")
                    continue

                if it == "SHOW_REMINDERS":
                    show_reminders(db)
                    continue

                if it == "SHOW_CONVERSATIONS":
                    show_conversations(db)
                    continue

                if it == "SHOW_HISTORY":
                    history = fetch_conversation_history(db)
                    if history:
                        print("\n--- Conversation History ---")
                        for user, assistant, ts in reversed(history):
                            print(f"[{ts}] You: {user}")
                            print(f"[{ts}] Assistant: {assistant}\n")
                    else:
                        print("No previous conversations found.")
                    continue

            # Try enhanced system control commands first
            enhanced_result = handle_enhanced_commands(user_input)
            if enhanced_result:
                speak(enhanced_result)
                save_conversation(db, user_input, enhanced_result)
                log_action(f"Enhanced command executed: {user_input[:50]}...")
                continue

            # Show tasks done today
            if ("what task i have done today" in user_input.lower() or
                "show my todays tasks" in user_input.lower() or
                ("today" in user_input.lower() and "task" in user_input.lower())):
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                tasks = get_tasks_on_date(today)
                if tasks:
                    print(f"\nTasks on {today}:")
                    for t in tasks:
                        print(f"- {t['title']} ({t['status']})")
                else:
                    print(f"No tasks found on {today}.")
                continue

            # Add task
            if user_input.startswith("add task "):
                task = user_input[9:]
                save_task(db, task)
                log_action(f"Added task: '{task}'")
                speak(f"Task '{task}' added.")
                continue

            # Long-term memory commands
            if user_input.lower().startswith("remember "):
                content = user_input[9:].strip()
                for p in ["that ", "this ", ": ", "- "]:
                    if content.lower().startswith(p.strip()):
                        content = content[len(p):].strip()
                        break
                if not content:
                    speak("What should I remember?")
                    continue
                mem_id = save_memory(content, tags=None)
                if mem_id > 0:
                    speak(f"Okay, I will remember that. (id {mem_id})")
                else:
                    speak("I couldn't save that memory.")
                continue

            if user_input.lower() in ["show memories", "list memories"]:
                rows = get_recent_memories(limit=20)
                if rows:
                    print("\n--- Memories ---")
                    print(f"{'ID':<5} {'When':<20} {'Content'}")
                    print("-"*80)
                    for r in rows:
                        when = str(r.get('created_at', ''))
                        print(f"{r['id']:<5} {when:<20} {r['content']}")
                else:
                    print("No memories saved yet.")
                continue

            if user_input.lower().startswith("find memory "):
                q = user_input[12:].strip()
                rows = search_memories(q, limit=10)
                if rows:
                    print("\n--- Memory Search ---")
                    print(f"{'ID':<5} {'When':<20} {'Content'}")
                    print("-"*80)
                    for r in rows:
                        when = str(r.get('created_at', ''))
                        print(f"{r['id']:<5} {when:<20} {r['content']}")
                else:
                    print("No matching memories found.")
                continue

            if user_input.lower().startswith("forget "):
                ident = user_input[7:].strip()
                if ident.isdigit():
                    ok = delete_memory_by_id(int(ident))
                    speak("Forgotten." if ok else "I couldn't find that memory.")
                else:
                    rows = search_memories(ident, limit=1)
                    if rows:
                        ok = delete_memory_by_id(rows[0]['id'])
                        speak("Forgotten." if ok else "I couldn't delete that memory.")
                    else:
                        speak("I couldn't find a matching memory.")
                continue

            # Show tasks/reminders/conversations
            if user_input.lower().strip() in ["show tasks", "show task", "list tasks", "list task"]:
                show_tasks(db)
                continue

            if user_input.lower() == "show reminders":
                show_reminders(db)
                continue

            if user_input.lower() == "show conversations":
                show_conversations(db)
                continue

            # Reminders
            if ("remind" in user_input.lower()) or ("rmind" in user_input.lower()):
                text, remind_time = parse_reminder_natural(user_input)
                if text and remind_time:
                    save_reminder(db, text, remind_time)
                    speak(f"Reminder saved for {remind_time.strftime('%I:%M %p on %b %d')}: {text}")
                else:
                    speak("I couldn't parse the reminder time.")
                continue

            # Run command
            if user_input.startswith("run "):
                result = run_system_command(user_input[4:])
                speak(result)
                continue

            # Delete task
            if user_input.lower().startswith("delete task "):
                identifier = user_input[12:].strip()
                success = delete_task(db, identifier)
                if success:
                    log_action(f"Deleted task: {identifier}")
                    speak(f"Task '{identifier}' deleted.")
                else:
                    speak(f"Task '{identifier}' not found.")
                continue

            # System logs
            if user_input.lower() == "show system logs":
                logs = get_system_logs()
                if logs:
                    print("Assistant: Here are the latest system logs:")
                    for log in logs:
                        print(f"[{log['timestamp']}] {log['action']} - {log['status']}")
                else:
                    print("Assistant: No logs found.")
                continue

            # AI response fallback with mood awareness
            try:
                history = fetch_conversation_history(db, limit=20)
            except Exception:
                history = []
            try:
                mem_rows = search_memories(user_input, limit=5)
            except Exception:
                mem_rows = []
            mem_context = "\n".join([f"- {m['content']}" for m in mem_rows]) if mem_rows else ""

            # Add mood context to system message - only for tone, not activity assumptions
            mood_context = ""
            if face_analysis_active:
                # Get current face analysis
                analysis = get_current_analysis()
                faces_detected = analysis.get('faces_detected', 0)

                if faces_detected > 0:
                    face = analysis['analysis'][0] if analysis['analysis'] else {}
                    emotion = face.get('emotion', {}).get('emotion', 'neutral')
                    confidence = face.get('emotion', {}).get('confidence', 0)

                    # State tracking - only print if mood changed significantly
                    mood_changed = False
                    if last_mood is None:
                        mood_changed = True  # First detection
                    elif emotion != last_mood:
                        mood_changed = True  # Different emotion
                    elif abs(confidence - last_mood_confidence) > 0.2:  # Confidence changed significantly
                        mood_changed = True

                    if mood_changed:
                        print(f"🎭 Face detected - Mood: {emotion} ({confidence:.2f})")
                        last_mood = emotion
                        last_mood_confidence = confidence

                    # Use mood for tone only, not activity assumptions
                    if confidence > 0.5:  # Higher threshold for tone adjustment only
                        if emotion == "happy":
                            mood_context = "\nThe user appears happy. Respond in a cheerful, friendly manner."
                        elif emotion == "sad":
                            mood_context = "\nThe user appears sad. Respond in a gentle, empathetic manner."
                        else:
                            mood_context = "\nThe user appears neutral. Respond in a natural, conversational manner."
                    else:
                        mood_context = "\nRespond in a natural, conversational manner."

            system_msg = (
                "You are a helpful AI assistant like Google Assistant. Be natural, concise, and direct. "
                "Keep responses brief and conversational. "
                "CRITICAL INSTRUCTION: NEVER assume or mention what the user is doing unless they explicitly tell you. "
                "If the user asks about their mood or face, respond based on detected emotion, but do not invent activities. "
                "For example, if mood is neutral, respond naturally without assuming they're doing anything specific."
                + mood_context
                + ("User memories:\n" + mem_context if mem_context else "")
            )
            response = ask_ai(user_input, history=history, system=system_msg)
            speak(response)
            save_conversation(db, user_input, response)

        except KeyboardInterrupt:
            speak("Goodbye!")
            break
        except Exception as e:
            print("⚠️ Error:", e)
            speak("Something went wrong.")
            time.sleep(1)

    # Cleanup
    try:
        if face_analysis_active and 'stop_face_analysis' in globals():
            stop_face_analysis()
            print("Face analysis system stopped.")
    except Exception as e:
        print(f"Error stopping face analysis: {e}")

    if db:
        try:
            db.close()
            print("Database connection closed.")
        except Exception:
            pass


if __name__ == "__main__":
    main()
