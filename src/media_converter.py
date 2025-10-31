#!/usr/bin/env python3
"""
Media Converter Application - Main Entry Point
Fully refactored with separated UI and business logic
"""

import tkinter as tk
from tkinter import ttk

# Import core business logic
from core import (
    ConvertHandler, SplitHandler, SettingsManager, HistoryManager,
    FileManager, YouTubeHandler, RecorderHandler
)

# Import UI components
from ui import (
    ConvertTab, SplitTab, YouTubeTab, RecordingTab,
    SettingsTab, HistoryTab
)


class MediaConverterApp:
    """Main application class - coordinates UI and business logic"""

    def __init__(self, root):
        self.root = root
        self.root.title("檔案豪幫手 v2.0")

        # Set window size
        window_width = 900
        window_height = 700
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(window_width, window_height)
        self.root.resizable(True, True)

        # Initialize variables
        self._init_variables()

        # Initialize handlers
        self.converter = ConvertHandler(self)
        self.splitter = SplitHandler(self)
        self.settings_mgr = SettingsManager(self)
        self.history_mgr = HistoryManager(self)
        self.file_mgr = FileManager(self)
        self.youtube_handler = YouTubeHandler(self)
        self.recorder_handler = RecorderHandler(self)

        # Load saved settings
        self.settings_mgr.load_settings()
        self.settings_mgr.init_default_variables()

        # Create UI
        self.create_ui()

        # Setup close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _init_variables(self):
        """Initialize all application variables"""
        # Convert tab variables
        self.convert_file_list = []
        self.audio_format = tk.StringVar(value="mp3")
        self.audio_bitrate = tk.StringVar(value="192k")
        self.sample_rate = tk.StringVar(value="44100")
        self.normalize = tk.BooleanVar(value=False)
        self.video_format = tk.StringVar(value="mp4")
        self.video_bitrate = tk.StringVar(value="2M")
        self.media_type = tk.StringVar(value="auto")

        # Split tab variables
        self.split_files = []
        self.split_mode = tk.StringVar(value="duration")
        self.split_size = tk.StringVar(value="100")
        self.split_duration = tk.StringVar(value="300")
        self.split_parts = tk.StringVar(value="3")
        self.keep_original = tk.BooleanVar(value=True)

        # YouTube variables
        self.youtube_url = tk.StringVar()
        self.youtube_quality = tk.StringVar(value="720p")
        self.youtube_format = tk.StringVar(value="mp4")
        self.youtube_mode = tk.StringVar(value="download")
        self.max_downloads = tk.IntVar(value=3)
        self.youtube_downloader = None

        # Recording variables
        self.recording_framerate = tk.StringVar(value="30")
        self.recording_quality = tk.StringVar(value="medium")
        self.recording_video_device = tk.StringVar(value="1")
        self.recording_audio_device = tk.StringVar(value="0")
        self.screen_recorder = None
        self.is_recording = False

    def create_ui(self):
        """Create the main UI"""
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=(5, 0))
        ttk.Label(header, text="🎬 Media Tool Suite", font=('Helvetica', 16, 'bold')).pack()

        # Custom tab selector
        self._create_tab_selector()

        # Configure styles
        self._configure_styles()

        # Create notebook
        self.notebook = ttk.Notebook(self.root, style='MainNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 5))

        # Create tab frames
        self.convert_frame = ttk.Frame(self.notebook)
        self.split_frame = ttk.Frame(self.notebook)
        self.youtube_frame = ttk.Frame(self.notebook)
        self.recording_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        self.history_frame = ttk.Frame(self.notebook)

        # Add tabs
        self.notebook.add(self.convert_frame, text="")
        self.notebook.add(self.split_frame, text="")
        self.notebook.add(self.youtube_frame, text="")
        self.notebook.add(self.recording_frame, text="")
        self.notebook.add(self.settings_frame, text="")
        self.notebook.add(self.history_frame, text="")

        # Create tab UI components
        self.convert_tab = ConvertTab(self.convert_frame, self)
        self.split_tab = SplitTab(self.split_frame, self)
        self.youtube_tab = YouTubeTab(self.youtube_frame, self)
        self.recording_tab = RecordingTab(self.recording_frame, self)
        self.settings_tab = SettingsTab(self.settings_frame, self)
        self.history_tab = HistoryTab(self.history_frame, self)

        # Initialize recording devices
        self.recorder_handler.refresh_recording_devices(show_message=False)

        # Set initial tab
        self.current_tab = None
        self.notebook.select(0)
        self._update_tab_button_styles(0)
        self.current_tab = 0

    def _create_tab_selector(self):
        """Create custom tab selector buttons"""
        tab_selector_frame = ttk.Frame(self.root)
        tab_selector_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        self.tab_buttons = {}
        tab_names = [
            ("Convert", 0), ("Split", 1), ("YouTube", 2),
            ("Screen Record", 3), ("Settings", 4), ("History", 5)
        ]

        for name, index in tab_names:
            btn = tk.Button(
                tab_selector_frame, text=name,
                command=lambda i=index: self.switch_tab(i),
                font=('Helvetica', 13), width=15, height=2,
                relief=tk.RAISED, bd=2, bg='#f0f0f0',
                activebackground='#e0e0e0', cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=3, pady=3)
            self.tab_buttons[index] = btn

    def _configure_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        try:
            style.configure('Accent.TButton', font=('Helvetica', 11, 'bold'))
        except:
            pass
        style.layout('MainNotebook', [('Notebook.client', {'sticky': 'nswe'})])

    def switch_tab(self, index):
        """Switch to specified tab"""
        if hasattr(self, 'current_tab') and self.current_tab == index:
            return
        self.notebook.select(index)
        self.current_tab = index
        self.root.after_idle(self._update_tab_button_styles, index)

    def _update_tab_button_styles(self, active_index):
        """Update button styles to show active tab"""
        for idx, btn in self.tab_buttons.items():
            if idx == active_index:
                btn.configure(font=('Helvetica', 13, 'bold'), relief=tk.SUNKEN, bg='#d0d0d0')
            else:
                btn.configure(font=('Helvetica', 13), relief=tk.RAISED, bg='#f0f0f0')

    # ========== Delegate methods to handlers ==========
    
    def update_format_ui(self):
        """Update format UI"""
        if hasattr(self, 'convert_tab'):
            self.convert_tab.update_format_ui()
    
    def update_split_mode(self):
        """Update split mode UI"""
        mode = self.split_mode.get()
        if hasattr(self, 'split_tab'):
            if mode == "duration":
                self.split_tab.split_label.config(text="Duration (seconds):")
                self.split_tab.split_entry.config(textvariable=self.split_duration)
                self.split_tab.split_unit.config(text="(5 minutes = 300)")
            elif mode == "size":
                self.split_tab.split_label.config(text="File size (MB):")
                self.split_tab.split_entry.config(textvariable=self.split_size)
                self.split_tab.split_unit.config(text="(1 GB = 1024 MB)")
            elif mode == "parts":
                self.split_tab.split_label.config(text="Number of parts:")
                self.split_tab.split_entry.config(textvariable=self.split_parts)
                self.split_tab.split_unit.config(text="(2-10 parts)")
    
    # File management
    def add_files(self, tab):
        self.file_mgr.add_files(tab)
    
    def add_folder(self, tab):
        self.file_mgr.add_folder(tab)
    
    def add_large_files(self):
        self.file_mgr.add_large_files()
    
    def remove_selected(self, tab):
        self.file_mgr.remove_selected(tab)
    
    def clear_files(self, tab):
        self.file_mgr.clear_files(tab)
    
    # Convert
    def convert_files(self):
        self.converter.convert_files()
    
    # Split
    def split_files_action(self):
        self.splitter.split_files_action()
    
    # Settings
    def apply_all_settings(self):
        self.settings_mgr.apply_all_settings()
    
    def reset_to_defaults(self):
        self.settings_mgr.reset_to_defaults()
    
    def save_settings(self):
        self.settings_mgr.save_settings()
    
    def browse_fixed_dir(self):
        self.settings_mgr.browse_fixed_dir()
    
    # History
    def add_conversion_history(self, *args, **kwargs):
        self.history_mgr.add_conversion_history(*args, **kwargs)
    
    def add_split_history(self, *args, **kwargs):
        self.history_mgr.add_split_history(*args, **kwargs)
    
    def update_statistics(self):
        self.history_mgr.update_statistics()
    
    def clear_history(self):
        self.history_mgr.clear_history()
    
    def log_error(self, *args):
        self.history_mgr.log_error(*args)
    
    # YouTube
    def download_youtube_unified(self):
        self.youtube_handler.download_youtube_unified()

    # Recording
    def refresh_recording_devices(self, show_message=True):
        self.recorder_handler.refresh_recording_devices(show_message)

    def start_recording(self):
        self.recorder_handler.start_recording()

    def stop_recording(self):
        self.recorder_handler.stop_recording()
    
    def on_closing(self):
        """Handle window closing"""
        try:
            self.settings_mgr.save_settings()
        except:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MediaConverterApp(root)
    root.update_idletasks()
    root.mainloop()
