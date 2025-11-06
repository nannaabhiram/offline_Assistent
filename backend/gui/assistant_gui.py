"""
Modern GUI Panel for Offline Assistant
Shows visual feedback while CLI runs in background
"""
import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime

class AssistantGUI:
    def __init__(self):
        self.root = None
        self.status_label = None
        self.response_text = None
        self.command_label = None
        self.cpu_bar = None
        self.memory_bar = None
        self.battery_label = None
        self.running = False
        self.gui_thread = None
        
    def start(self):
        """Start GUI in separate thread"""
        if not self.running:
            self.running = True
            self.gui_thread = threading.Thread(target=self._run_gui, daemon=True)
            self.gui_thread.start()
            time.sleep(0.5)  # Wait for GUI to initialize
            
    def _run_gui(self):
        """Run the GUI window (called in separate thread)"""
        self.root = tk.Tk()
        self.root.title("🤖 Offline Assistant")
        self.root.geometry("500x600")
        self.root.configure(bg='#0a0a0a')
        
        # Make window stay on top (optional)
        self.root.attributes('-topmost', True)
        
        # Header Section
        header_frame = tk.Frame(self.root, bg='#1a1a1a', height=80)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        # Assistant Title
        title_label = tk.Label(
            header_frame, 
            text="🤖 OFFLINE ASSISTANT", 
            font=('Arial', 18, 'bold'),
            fg='#00ff88',
            bg='#1a1a1a'
        )
        title_label.pack(pady=10)
        
        # Status Indicator
        self.status_label = tk.Label(
            header_frame,
            text="● ONLINE",
            font=('Arial', 10),
            fg='#00ff88',
            bg='#1a1a1a'
        )
        self.status_label.pack()
        
        # Current Command Section
        cmd_frame = tk.Frame(self.root, bg='#0a0a0a')
        cmd_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            cmd_frame,
            text="Last Command:",
            font=('Arial', 10, 'bold'),
            fg='#888888',
            bg='#0a0a0a'
        ).pack(anchor='w')
        
        self.command_label = tk.Label(
            cmd_frame,
            text="Waiting for input...",
            font=('Arial', 12),
            fg='#ffffff',
            bg='#0a0a0a',
            wraplength=450,
            justify='left'
        )
        self.command_label.pack(anchor='w', pady=5)
        
        # Response Section
        response_frame = tk.Frame(self.root, bg='#1a1a1a')
        response_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(
            response_frame,
            text="Response:",
            font=('Arial', 10, 'bold'),
            fg='#888888',
            bg='#1a1a1a'
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Scrollable text area for responses
        text_container = tk.Frame(response_frame, bg='#1a1a1a')
        text_container.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(text_container)
        scrollbar.pack(side='right', fill='y')
        
        self.response_text = tk.Text(
            text_container,
            font=('Consolas', 11),
            bg='#0a0a0a',
            fg='#00ff88',
            wrap='word',
            height=10,
            yscrollcommand=scrollbar.set,
            relief='flat',
            padx=10,
            pady=10
        )
        self.response_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.response_text.yview)
        
        # System Stats Section
        stats_frame = tk.Frame(self.root, bg='#1a1a1a')
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            stats_frame,
            text="System Status:",
            font=('Arial', 10, 'bold'),
            fg='#888888',
            bg='#1a1a1a'
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        # CPU Progress Bar
        cpu_container = tk.Frame(stats_frame, bg='#1a1a1a')
        cpu_container.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            cpu_container,
            text="CPU:",
            font=('Arial', 9),
            fg='#ffffff',
            bg='#1a1a1a',
            width=10,
            anchor='w'
        ).pack(side='left')
        
        self.cpu_bar = ttk.Progressbar(
            cpu_container,
            length=300,
            mode='determinate',
            maximum=100
        )
        self.cpu_bar.pack(side='left', padx=5)
        
        self.cpu_label = tk.Label(
            cpu_container,
            text="0%",
            font=('Arial', 9),
            fg='#ffffff',
            bg='#1a1a1a',
            width=5
        )
        self.cpu_label.pack(side='left')
        
        # Memory Progress Bar
        mem_container = tk.Frame(stats_frame, bg='#1a1a1a')
        mem_container.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            mem_container,
            text="Memory:",
            font=('Arial', 9),
            fg='#ffffff',
            bg='#1a1a1a',
            width=10,
            anchor='w'
        ).pack(side='left')
        
        self.memory_bar = ttk.Progressbar(
            mem_container,
            length=300,
            mode='determinate',
            maximum=100
        )
        self.memory_bar.pack(side='left', padx=5)
        
        self.memory_label = tk.Label(
            mem_container,
            text="0%",
            font=('Arial', 9),
            fg='#ffffff',
            bg='#1a1a1a',
            width=5
        )
        self.memory_label.pack(side='left')
        
        # Battery Status
        battery_container = tk.Frame(stats_frame, bg='#1a1a1a')
        battery_container.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            battery_container,
            text="Battery:",
            font=('Arial', 9),
            fg='#ffffff',
            bg='#1a1a1a',
            width=10,
            anchor='w'
        ).pack(side='left')
        
        self.battery_label = tk.Label(
            battery_container,
            text="N/A",
            font=('Arial', 9),
            fg='#ffffff',
            bg='#1a1a1a'
        )
        self.battery_label.pack(side='left')
        
        # Footer
        footer_frame = tk.Frame(self.root, bg='#1a1a1a')
        footer_frame.pack(fill='x', side='bottom')
        
        self.time_label = tk.Label(
            footer_frame,
            text=self._get_time(),
            font=('Arial', 9),
            fg='#888888',
            bg='#1a1a1a'
        )
        self.time_label.pack(pady=10)
        
        # Update time periodically
        self._update_time()
        
        # Start GUI loop
        self.root.mainloop()
        self.running = False
        
    def _get_time(self):
        """Get current time string"""
        return datetime.now().strftime("%I:%M:%S %p")
        
    def _update_time(self):
        """Update time label every second"""
        if self.running and self.time_label:
            self.time_label.config(text=self._get_time())
            self.root.after(1000, self._update_time)
            
    def update_command(self, command):
        """Update the current command display"""
        if self.running and self.command_label:
            self.root.after(0, lambda: self.command_label.config(text=f"▶ {command}"))
            
    def update_response(self, response, success=True):
        """Update the response text area"""
        if self.running and self.response_text:
            def _update():
                self.response_text.config(state='normal')
                self.response_text.delete('1.0', 'end')
                
                # Add timestamp
                timestamp = datetime.now().strftime("%H:%M:%S")
                color = '#00ff88' if success else '#ff4444'
                
                self.response_text.insert('end', f"[{timestamp}] ", 'timestamp')
                self.response_text.insert('end', f"{'✓' if success else '✗'} ", 'status')
                self.response_text.insert('end', f"{response}\n", 'response')
                
                # Apply tags for colors
                self.response_text.tag_config('timestamp', foreground='#888888')
                self.response_text.tag_config('status', foreground=color, font=('Arial', 12, 'bold'))
                self.response_text.tag_config('response', foreground='#ffffff')
                
                self.response_text.config(state='disabled')
                self.response_text.see('end')
                
            self.root.after(0, _update)
            
    def update_status(self, status, color='#00ff88'):
        """Update the status indicator"""
        if self.running and self.status_label:
            self.root.after(0, lambda: self.status_label.config(text=f"● {status}", fg=color))
            
    def update_system_stats(self, cpu=None, memory=None, battery=None):
        """Update system statistics"""
        if self.running:
            def _update():
                if cpu is not None and self.cpu_bar:
                    self.cpu_bar['value'] = cpu
                    self.cpu_label.config(text=f"{cpu}%")
                    
                if memory is not None and self.memory_bar:
                    self.memory_bar['value'] = memory
                    self.memory_label.config(text=f"{memory}%")
                    
                if battery is not None and self.battery_label:
                    self.battery_label.config(text=battery)
                    
            self.root.after(0, _update)
            
    def show_processing(self):
        """Show processing animation"""
        if self.running and self.status_label:
            self.root.after(0, lambda: self.status_label.config(text="● PROCESSING...", fg='#ffaa00'))
            
    def show_listening(self):
        """Show listening status"""
        if self.running and self.status_label:
            self.root.after(0, lambda: self.status_label.config(text="● LISTENING...", fg='#00aaff'))
            
    def show_idle(self):
        """Show idle status"""
        if self.running and self.status_label:
            self.root.after(0, lambda: self.status_label.config(text="● READY", fg='#00ff88'))
            
    def stop(self):
        """Stop the GUI"""
        if self.running and self.root:
            self.root.after(0, self.root.quit)
            self.running = False

# Global GUI instance
_gui_instance = None

def get_gui():
    """Get or create GUI instance"""
    global _gui_instance
    if _gui_instance is None:
        _gui_instance = AssistantGUI()
    return _gui_instance

def start_gui():
    """Start the GUI"""
    gui = get_gui()
    gui.start()
    return gui

def update_command(command):
    """Update command display"""
    gui = get_gui()
    if gui.running:
        gui.update_command(command)

def update_response(response, success=True):
    """Update response display"""
    gui = get_gui()
    if gui.running:
        gui.update_response(response, success)

def update_status(status, color='#00ff88'):
    """Update status display"""
    gui = get_gui()
    if gui.running:
        gui.update_status(status, color)

def update_system_stats(cpu=None, memory=None, battery=None):
    """Update system stats"""
    gui = get_gui()
    if gui.running:
        gui.update_system_stats(cpu, memory, battery)

def show_processing():
    """Show processing status"""
    gui = get_gui()
    if gui.running:
        gui.show_processing()

def show_listening():
    """Show listening status"""
    gui = get_gui()
    if gui.running:
        gui.show_listening()

def show_idle():
    """Show idle status"""
    gui = get_gui()
    if gui.running:
        gui.show_idle()
