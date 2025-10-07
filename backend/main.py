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


import os
import time
import threading
import pyttsx3
import re
import datetime
from dotenv import load_dotenv
from nlp.nlp_utils import parse_command, parse_intent
import dateparser
from dateparser.search import search_dates

# Local imports
from speech.stt import listen_voice
from ai.brain import ask_ai
from system.control import run_system_command, list_running_apps, block_app_by_name, block_apps_by_names
from system.optimized_control import (
    execute_fast_command, quick_volume_control, quick_brightness_control, 
    quick_power_action, quick_network_toggle, quick_app_launch, quick_process_kill,
    get_quick_performance, get_quick_system_info, mute_toggle, lock_screen, 
    wifi_toggle, performance_status, system_status
)
from db.db_connection import (
    get_db_connection, save_conversation, save_task, log_action, get_system_logs,
    get_deleted_tasks, get_tasks_on_date,
    # Memory helpers
    ensure_memories_table, save_memory, get_recent_memories, search_memories, delete_memory_by_id
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


def handle_enhanced_commands(user_input):
    """Handle enhanced system control commands with optimized performance"""
    text = user_input.lower().strip()
    
    # System control commands - using fast optimized functions
    if any(keyword in text for keyword in ["volume", "sound", "audio"]):
        if "up" in text or "increase" in text:
            result = quick_volume_control("up", 10)
        elif "down" in text or "decrease" in text:
            result = quick_volume_control("down", 10)
        elif "mute" in text:
            result = mute_toggle()
        elif "max" in text or "full" in text:
            result = quick_volume_control("set", 100)
        elif "min" in text or "zero" in text:
            result = quick_volume_control("set", 0)
        else:
            # Extract volume level if specified
            import re
            numbers = re.findall(r'\d+', text)
            if numbers:
                level = min(100, max(0, int(numbers[0])))
                result = quick_volume_control("set", level)
            else:
                result = quick_volume_control("get")
        return f"Volume: {result}"
    
    elif any(keyword in text for keyword in ["brightness", "screen", "display"]):
        if "up" in text or "increase" in text or "brighter" in text:
            result = quick_brightness_control("up", 10)
        elif "down" in text or "decrease" in text or "dimmer" in text:
            result = quick_brightness_control("down", 10)
        elif "max" in text or "full" in text:
            result = quick_brightness_control("set", 100)
        elif "min" in text or "lowest" in text:
            result = quick_brightness_control("set", 10)
        else:
            result = quick_brightness_control("get")
        return f"Brightness: {result}"
    
    elif any(keyword in text for keyword in ["shutdown", "restart", "sleep", "hibernate", "lock"]):
        if "shutdown" in text or "power off" in text:
            result = quick_power_action("shutdown")
        elif "restart" in text or "reboot" in text:
            result = quick_power_action("restart")
        elif "sleep" in text:
            result = quick_power_action("sleep")
        elif "hibernate" in text:
            result = quick_power_action("hibernate")
        elif "lock" in text:
            result = lock_screen()
        return f"Power: {result}"
    
    elif any(keyword in text for keyword in ["wifi", "wireless", "network"]):
        if "off" in text or "disable" in text:
            result = wifi_toggle("off")
        elif "on" in text or "enable" in text:
            result = wifi_toggle("on")
        else:
            result = wifi_toggle("status")
        return f"Network: {result}"
    
    elif any(keyword in text for keyword in ["system info", "computer info", "pc info", "hardware", "system status"]):
        result = system_status()
        return f"System: {result}"
    
    elif any(keyword in text for keyword in ["performance", "cpu usage", "memory usage", "disk usage"]):
        result = performance_status()
        return f"Performance: {result}"
    
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
            return f"App: {result}"
        else:
            return "Please specify which application to open."
    
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
            return f"Process: {result}"
        else:
            return "Please specify which process to terminate."
    
    # File operations - using optimized functions
    elif any(keyword in text for keyword in ["create file", "make file"]):
        import re
        match = re.search(r'(?:create|make)\s+file\s+(.+?)(?:\s|$)', text)
        if match:
            file_path = match.group(1).strip()
            result = execute_fast_command("file", action="create", path=file_path)
            return f"File: {result}"
        else:
            return "Please specify the file path to create."
    
    elif any(keyword in text for keyword in ["delete file", "remove file"]):
        import re
        match = re.search(r'(?:delete|remove)\s+file\s+(.+?)(?:\s|$)', text)
        if match:
            file_path = match.group(1).strip()
            result = execute_fast_command("file", action="delete", path=file_path)
            return f"File: {result}"
        else:
            return "Please specify the file path to delete."
    
    # Return None if no enhanced command matched
    return None


def fetch_conversation_history(db, limit=10):
    cursor = db.cursor()
    cursor.execute("SELECT user_input, assistant_response, timestamp FROM conversations ORDER BY timestamp DESC LIMIT %s", (limit,))
    return cursor.fetchall()


# Load environment variables
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(project_root, 'config', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Initialize text-to-speech
engine = pyttsx3.init()
tts_lock = threading.Lock()


def speak(text):
    print(f"Assistant: {text}")
    try:
        with tts_lock:
            engine.say(text)
            engine.runAndWait()
    except Exception:
        pass


def speak_no_prefix(text):
    print(f"Assistant: {text}")
    try:
        with tts_lock:
            engine.say(text)
            engine.runAndWait()
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


def main():
    db = get_db_connection()
    if not db:
        print("❌ Database connection failed. Exiting.")
        return
    
    # Ensure long-term memory table exists
    try:
        ensure_memories_table()
    except Exception:
        pass
    
    speak("Hello! Your offline AI assistant is ready.")
    
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

            # Hardcoded creator response
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

            # AI response fallback
            try:
                history = fetch_conversation_history(db, limit=20)
            except Exception:
                history = []
            try:
                mem_rows = search_memories(user_input, limit=5)
            except Exception:
                mem_rows = []
            mem_context = "\n".join([f"- {m['content']}" for m in mem_rows]) if mem_rows else ""
            system_msg = (
                "You are an offline assistant. Use recent context and the following memories when helpful, "
                "be concise, and ask a clarifying question if needed.\n"
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


if __name__ == "__main__":
    main()
