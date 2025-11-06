"""
Test Advanced Automation Module
"""
import sys
sys.path.append('d:/offline_assistant/backend')

from system import automation

print("=" * 70)
print("TESTING ADVANCED AUTOMATION MODULE")
print("=" * 70)

# Test 1: System Info
print("\n📊 1. SYSTEM INFO TESTS")
print("-" * 70)

print("\n✓ CPU Usage:")
result = automation.get_cpu_usage()
print(f"  {result['message']}")

print("\n✓ Memory Info:")
result = automation.get_memory_info()
print(f"  {result['message']}")

print("\n✓ Disk Info:")
result = automation.get_disk_info()
print(f"  {result['message']}")

print("\n✓ Battery Status:")
result = automation.get_battery_status()
print(f"  {result['message']}")

print("\n✓ OS Info:")
result = automation.get_os_info()
print(f"  {result['message']}")

print("\n✓ Network Info:")
result = automation.get_network_info()
print(f"  {result['message']}")

# Test 2: App Control
print("\n\n🎯 2. APP CONTROL TESTS")
print("-" * 70)

print("\n✓ Check Explorer:")
result = automation.get_app_info("explorer")
if result['found']:
    print(f"  Explorer is running - CPU: {result['cpu_percent']}%, Memory: {result['memory_percent']:.1f}%")
else:
    print(f"  Explorer not found")

print("\n✓ List Running Processes (Top 10):")
processes = automation.list_running_processes()
sorted_procs = sorted(processes, key=lambda x: x['cpu'] or 0, reverse=True)[:10]
for proc in sorted_procs:
    print(f"  - {proc['name']} (CPU: {proc['cpu']}%)")

# Test 3: PyAutoGUI availability
print("\n\n🖱️ 3. MOUSE & KEYBOARD CONTROL")
print("-" * 70)

if automation.is_pyautogui_available():
    print("✅ PyAutoGUI is available")
    
    result = automation.get_screen_size()
    if result['success']:
        print(f"  Screen: {result['resolution']}")
    
    result = automation.get_mouse_position()
    if result['success']:
        print(f"  Mouse: {result['position']}")
else:
    print("⚠️ PyAutoGUI not installed")
    print("  Install with: pip install pyautogui")

# Test 4: File System
print("\n\n📁 4. FILE SYSTEM TESTS")
print("-" * 70)

print("\n✓ Current Directory Files:")
result = automation.list_files(".")
if result['success']:
    print(f"  Found {result['count']} files")
    for f in result['files'][:5]:
        print(f"    - {f}")
    if result['count'] > 5:
        print(f"    ... and {result['count'] - 5} more")

# Test 5: Full System Status
print("\n\n🖥️ 5. FULL SYSTEM STATUS")
print("-" * 70)

status = automation.get_full_system_status()
if status['success']:
    print(f"\n  CPU: {status['cpu']['cpu_percent']}% ({status['cpu']['cpu_count']} cores)")
    print(f"  Memory: {status['memory']['percent']}% used ({status['memory']['used_gb']} GB / {status['memory']['total_gb']} GB)")
    print(f"  Disk: {status['disk']['percent']}% used ({status['disk']['free_gb']} GB free)")
    if status['battery']['has_battery']:
        print(f"  Battery: {status['battery']['percent']}% {'(charging)' if status['battery']['plugged_in'] else '(on battery)'}")
    else:
        print(f"  Battery: No battery (desktop)")
    print(f"  OS: {status['os']['platform']}")
    print(f"  Network: {status['network']['bytes_recv_mb']} MB received")

print("\n" + "=" * 70)
print("✅ ALL TESTS COMPLETE!")
print("=" * 70)

print("\n💡 The automation module is ready to use!")
print("   Start your assistant and try commands like:")
print("   - 'cpu usage'")
print("   - 'battery status'")
print("   - 'full system status'")
print("   - 'open app notepad'")
print("   - 'list files in C:\\\\Users'")
