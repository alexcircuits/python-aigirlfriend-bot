import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from datetime import datetime

class UserDataViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram User Data Viewer")
        self.root.geometry("1200x800")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - File list
        self.left_panel = ttk.Frame(self.main_frame, width=250)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        # Search box
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.left_panel, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X, padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.filter_list)
        
        # File list
        self.file_listbox = tk.Listbox(self.left_panel)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.file_listbox.bind("<<ListboxSelect>>", self.load_user_data)
        
        # Right panel - Data display
        self.right_panel = ttk.Frame(self.main_frame)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Notebook for different sections
        self.notebook = ttk.Notebook(self.right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_profile_tab()
        self.create_activity_tab()
        self.create_messages_tab()
        self.create_entities_tab()
        
        # Load initial data
        self.data_dir = "user_data"
        self.load_file_list()
        
    def create_profile_tab(self):
        self.profile_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.profile_frame, text="Profile")
        
        # Profile info
        ttk.Label(self.profile_frame, text="Username:").grid(row=0, column=0, sticky=tk.W)
        self.username_label = ttk.Label(self.profile_frame, text="")
        self.username_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(self.profile_frame, text="Name:").grid(row=1, column=0, sticky=tk.W)
        self.name_label = ttk.Label(self.profile_frame, text="")
        self.name_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(self.profile_frame, text="User ID:").grid(row=2, column=0, sticky=tk.W)
        self.user_id_label = ttk.Label(self.profile_frame, text="")
        self.user_id_label.grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(self.profile_frame, text="Language:").grid(row=3, column=0, sticky=tk.W)
        self.language_label = ttk.Label(self.profile_frame, text="")
        self.language_label.grid(row=3, column=1, sticky=tk.W)
        
        ttk.Label(self.profile_frame, text="First Seen:").grid(row=4, column=0, sticky=tk.W)
        self.first_seen_label = ttk.Label(self.profile_frame, text="")
        self.first_seen_label.grid(row=4, column=1, sticky=tk.W)
        
        ttk.Label(self.profile_frame, text="Last Seen:").grid(row=5, column=0, sticky=tk.W)
        self.last_seen_label = ttk.Label(self.profile_frame, text="")
        self.last_seen_label.grid(row=5, column=1, sticky=tk.W)
        
    def create_activity_tab(self):
        self.activity_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.activity_frame, text="Activity")
        
        # Activity stats
        ttk.Label(self.activity_frame, text="Total Messages:").grid(row=0, column=0, sticky=tk.W)
        self.total_messages_label = ttk.Label(self.activity_frame, text="")
        self.total_messages_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(self.activity_frame, text="Entities Parsed:").grid(row=1, column=0, sticky=tk.W)
        self.entities_label = ttk.Label(self.activity_frame, text="")
        self.entities_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(self.activity_frame, text="Chat Type:").grid(row=2, column=0, sticky=tk.W)
        self.chat_type_label = ttk.Label(self.activity_frame, text="")
        self.chat_type_label.grid(row=2, column=1, sticky=tk.W)
        
    def create_messages_tab(self):
        self.messages_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.messages_frame, text="Messages")
        
        self.messages_text = scrolledtext.ScrolledText(self.messages_frame, wrap=tk.WORD)
        self.messages_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_entities_tab(self):
        self.entities_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.entities_frame, text="Entities")
        
        # Links
        ttk.Label(self.entities_frame, text="Links:").pack(anchor=tk.W)
        self.links_listbox = tk.Listbox(self.entities_frame, height=5)
        self.links_listbox.pack(fill=tk.X, padx=5, pady=2)
        
        # Phone Numbers
        ttk.Label(self.entities_frame, text="Phone Numbers:").pack(anchor=tk.W)
        self.phones_listbox = tk.Listbox(self.entities_frame, height=3)
        self.phones_listbox.pack(fill=tk.X, padx=5, pady=2)
        
        # Hashtags
        ttk.Label(self.entities_frame, text="Hashtags:").pack(anchor=tk.W)
        self.hashtags_listbox = tk.Listbox(self.entities_frame, height=3)
        self.hashtags_listbox.pack(fill=tk.X, padx=5, pady=2)
        
        # Mentions
        ttk.Label(self.entities_frame, text="Mentions:").pack(anchor=tk.W)
        self.mentions_listbox = tk.Listbox(self.entities_frame, height=3)
        self.mentions_listbox.pack(fill=tk.X, padx=5, pady=2)
        
    def load_file_list(self):
        self.file_listbox.delete(0, tk.END)
        try:
            files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
            for f in files:
                self.file_listbox.insert(tk.END, f)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Directory '{self.data_dir}' not found!")
            
    def filter_list(self, event=None):
        search_term = self.search_var.get().lower()
        self.file_listbox.delete(0, tk.END)
        try:
            files = [f for f in os.listdir(self.data_dir) 
                    if f.endswith('.json') and search_term in f.lower()]
            for f in files:
                self.file_listbox.insert(tk.END, f)
        except FileNotFoundError:
            pass
            
    def load_user_data(self, event):
        selection = self.file_listbox.curselection()
        if not selection:
            return
            
        filename = self.file_listbox.get(selection[0])
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Update profile tab
            self.username_label.config(text=data.get('username', 'N/A'))
            self.name_label.config(text=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or 'N/A')
            self.user_id_label.config(text=data.get('user_id', 'N/A'))
            self.language_label.config(text=data.get('language_code', 'N/A'))
            self.first_seen_label.config(text=self.format_timestamp(data.get('first_seen')))
            self.last_seen_label.config(text=self.format_timestamp(data.get('last_seen')))
            
            # Update activity tab
            self.total_messages_label.config(text=data.get('message_count', 0))
            self.entities_label.config(text=data.get('entities_parsed', 0))
            self.chat_type_label.config(text=data.get('chat_type', 'N/A'))
            
            # Update messages tab
            self.messages_text.delete(1.0, tk.END)
            for msg in data.get('messages', []):
                timestamp = self.format_timestamp(msg.get('timestamp'))
                self.messages_text.insert(tk.END, 
                    f"[{timestamp}] {msg.get('from', '?')}: {msg.get('text', '')}\n")
                
            # Update entities tab
            self.update_listbox(self.links_listbox, data.get('links', []))
            self.update_listbox(self.phones_listbox, data.get('phone_numbers', []))
            self.update_listbox(self.hashtags_listbox, [f"#{h}" for h in data.get('hashtags', [])])
            self.update_listbox(self.mentions_listbox, [f"@{m}" for m in data.get('mentions', [])])
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading file: {str(e)}")
            
    def format_timestamp(self, ts):
        try:
            if isinstance(ts, str):
                dt = datetime.fromisoformat(ts)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            return "N/A"
        except ValueError:
            return "Invalid timestamp"
            
    def update_listbox(self, listbox, items):
        listbox.delete(0, tk.END)
        for item in items:
            listbox.insert(tk.END, item)

if __name__ == "__main__":
    root = tk.Tk()
    app = UserDataViewer(root)
    root.mainloop()