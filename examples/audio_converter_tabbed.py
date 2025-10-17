#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import subprocess
from pathlib import Path
import json

# Import new design pattern modules
from app_constants import AppConstants
from media_processor import MediaProcessor, MediaProcessorBuilder
from media_handlers import MediaHandlerFactory

class TabbedMediaConverter:
    def __init__(self, root):
        self.root = root
        self.root.title(AppConstants.APP_NAME)
        self.root.geometry(f"{AppConstants.WINDOW_WIDTH}x{AppConstants.WINDOW_HEIGHT}")

        # Variables for Convert tab
        self.convert_files = []
        self.output_format = tk.StringVar(value="mp3")
        self.bitrate = tk.StringVar(value="192k")
        self.normalize = tk.BooleanVar(value=False)
        self.sample_rate = tk.StringVar(value="44100")

        # Variables for Split tab
        self.split_files = []
        self.split_mode = tk.StringVar(value="duration")
        self.split_size = tk.StringVar(value="100")  # MB
        self.split_duration = tk.StringVar(value="300")  # seconds
        self.keep_original = tk.BooleanVar(value=False)

        # Load saved settings first
        self.load_settings()

        self.create_widgets()

        # Setup close event to save settings
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(header, text="🎬 Media Tool Suite", font=('Helvetica', 16, 'bold')).pack()

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create tabs
        self.convert_tab = ttk.Frame(self.notebook)
        self.split_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.convert_tab, text="🔄 Convert")
        self.notebook.add(self.split_tab, text="✂️ Split")
        self.notebook.add(self.settings_tab, text="⚙️ Settings")
        self.notebook.add(self.history_tab, text="📊 History")

        # History tracking
        self.conversion_history = []
        self.split_history = []

        # Setup each tab
        self.setup_convert_tab()
        self.setup_split_tab()
        self.setup_settings_tab()
        self.setup_history_tab()

    def setup_convert_tab(self):
        """Setup the Convert tab"""
        main_frame = ttk.Frame(self.convert_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # File list
        list_frame = ttk.LabelFrame(main_frame, text="Media Files to Convert", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Listbox with scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.convert_listbox = tk.Listbox(list_frame, height=8, yscrollcommand=scrollbar.set)
        self.convert_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.convert_listbox.yview)

        # File buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(btn_frame, text="Add Files",
                  command=lambda: self.add_files('convert')).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Add Folder",
                  command=lambda: self.add_folder('convert')).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Remove",
                  command=lambda: self.remove_selected('convert')).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear",
                  command=lambda: self.clear_files('convert')).pack(side=tk.LEFT, padx=2)

        # Settings frame
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill=tk.X, pady=10)

        # Left side - Format settings
        format_frame = ttk.LabelFrame(settings_frame, text="Format Settings", padding="10")
        format_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(format_frame, text="Output Format:").grid(row=0, column=0, sticky=tk.W, pady=2)
        all_formats = AppConstants.AUDIO_FORMAT_OPTIONS + AppConstants.VIDEO_FORMAT_OPTIONS
        format_combo = ttk.Combobox(format_frame, textvariable=self.output_format,
                                    values=all_formats,
                                    state="readonly", width=10)
        format_combo.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(format_frame, text="Bitrate:").grid(row=1, column=0, sticky=tk.W, pady=2)
        bitrate_combo = ttk.Combobox(format_frame, textvariable=self.bitrate,
                                     values=["128k", "192k", "256k", "320k"],
                                     state="readonly", width=10)
        bitrate_combo.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(format_frame, text="Sample Rate:").grid(row=2, column=0, sticky=tk.W, pady=2)
        sample_combo = ttk.Combobox(format_frame, textvariable=self.sample_rate,
                                    values=["44100", "48000", "96000"],
                                    state="readonly", width=10)
        sample_combo.grid(row=2, column=1, padx=5, pady=2)

        # Right side - Options
        options_frame = ttk.LabelFrame(settings_frame, text="Options", padding="10")
        options_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Checkbutton(options_frame, text="Normalize Audio (-16 LUFS)",
                       variable=self.normalize).pack(anchor=tk.W, pady=5)

        ttk.Label(options_frame, text="Output: Same folder as source",
                 font=('Helvetica', 10, 'italic')).pack(anchor=tk.W, pady=5)

        # Progress bar
        self.convert_progress = ttk.Progressbar(main_frame, mode='determinate')
        self.convert_progress.pack(fill=tk.X, pady=5)

        # Convert button
        convert_btn = ttk.Button(main_frame, text="Convert All Files",
                                command=self.convert_files)
        convert_btn.pack(pady=10)

        # Status
        self.convert_status = ttk.Label(main_frame, text="Ready")
        self.convert_status.pack()

    def setup_split_tab(self):
        """Setup the Split tab"""
        main_frame = ttk.Frame(self.split_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # File list
        list_frame = ttk.LabelFrame(main_frame, text="Media Files to Split", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.split_listbox = tk.Listbox(list_frame, height=8, yscrollcommand=scrollbar.set)
        self.split_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.split_listbox.yview)

        # File buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(btn_frame, text="Add Files",
                  command=lambda: self.add_files('split')).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Add Large Files (>100MB)",
                  command=self.add_large_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Remove",
                  command=lambda: self.remove_selected('split')).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear",
                  command=lambda: self.clear_files('split')).pack(side=tk.LEFT, padx=2)

        # Split settings
        settings_frame = ttk.LabelFrame(main_frame, text="Split Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=10)

        # Split mode
        mode_frame = ttk.Frame(settings_frame)
        mode_frame.pack(anchor=tk.W, pady=5)

        ttk.Label(mode_frame, text="Split by:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(mode_frame, text="Duration", value="duration",
                       variable=self.split_mode,
                       command=self.update_split_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="File Size", value="size",
                       variable=self.split_mode,
                       command=self.update_split_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Parts", value="parts",
                       variable=self.split_mode,
                       command=self.update_split_mode).pack(side=tk.LEFT, padx=5)

        # Split value input
        self.split_input_frame = ttk.Frame(settings_frame)
        self.split_input_frame.pack(anchor=tk.W, pady=5)

        self.split_label = ttk.Label(self.split_input_frame, text="Duration (seconds):")
        self.split_label.pack(side=tk.LEFT, padx=(0, 10))

        self.split_entry = ttk.Entry(self.split_input_frame, textvariable=self.split_duration, width=10)
        self.split_entry.pack(side=tk.LEFT)

        self.split_unit = ttk.Label(self.split_input_frame, text="(5 minutes = 300)")
        self.split_unit.pack(side=tk.LEFT, padx=(10, 0))

        # Options
        ttk.Checkbutton(settings_frame, text="Keep original file after splitting",
                       variable=self.keep_original).pack(anchor=tk.W, pady=5)

        # Progress
        self.split_progress = ttk.Progressbar(main_frame, mode='determinate')
        self.split_progress.pack(fill=tk.X, pady=5)

        # Split button
        split_btn = ttk.Button(main_frame, text="Split Selected Files",
                              command=self.split_files_action)
        split_btn.pack(pady=10)

        # Status
        self.split_status = ttk.Label(main_frame, text="Ready")
        self.split_status.pack()

    def setup_settings_tab(self):
        """Setup the Settings tab"""
        main_frame = ttk.Frame(self.settings_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title and Description
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(title_frame, text="Default Settings", font=('Helvetica', 14, 'bold')).pack(anchor=tk.W)

        # Add description
        description_frame = ttk.Frame(title_frame)
        description_frame.pack(fill=tk.X, pady=(5, 0))

        description_text = ("這些預設值會自動套用到 Convert 和 Split 功能。\n"
                          "修改後點擊「Apply Settings」套用到目前工作區，或「Save Settings」永久儲存。")
        ttk.Label(description_frame, text=description_text,
                 font=('Helvetica', 9), foreground='#666666',
                 wraplength=650).pack(anchor=tk.W)

        # Create notebook for settings categories
        settings_notebook = ttk.Notebook(main_frame)
        settings_notebook.pack(fill=tk.BOTH, expand=True)

        # Convert defaults tab
        convert_defaults_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(convert_defaults_frame, text="Convert")

        # Convert section description
        convert_desc_frame = ttk.Frame(convert_defaults_frame)
        convert_desc_frame.pack(fill=tk.X, pady=(10, 15))
        ttk.Label(convert_desc_frame, text="轉檔預設設定",
                 font=('Helvetica', 11, 'bold')).pack(anchor=tk.W)
        ttk.Label(convert_desc_frame,
                 text="設定轉檔時的預設格式、品質和處理選項。支援音訊和視頻格式。",
                 font=('Helvetica', 9), foreground='#666666',
                 wraplength=500).pack(anchor=tk.W, pady=(2, 0))

        # Default format
        format_frame = ttk.Frame(convert_defaults_frame)
        format_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(format_frame, text="Output format:").pack(side=tk.LEFT, padx=(0, 10))
        self.default_format = tk.StringVar(value=AppConstants.DEFAULT_SETTINGS['convert']['format'])
        all_formats = AppConstants.AUDIO_FORMAT_OPTIONS + AppConstants.VIDEO_FORMAT_OPTIONS
        ttk.Combobox(format_frame, textvariable=self.default_format,
                    values=all_formats, state="readonly", width=8).pack(side=tk.LEFT)

        # Default bitrate
        bitrate_frame = ttk.Frame(convert_defaults_frame)
        bitrate_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(bitrate_frame, text="Bitrate:").pack(side=tk.LEFT, padx=(0, 10))
        self.default_bitrate = tk.StringVar(value=AppConstants.DEFAULT_SETTINGS['convert']['bitrate'])
        ttk.Combobox(bitrate_frame, textvariable=self.default_bitrate,
                    values=AppConstants.BITRATE_OPTIONS, state="readonly", width=8).pack(side=tk.LEFT)

        # Default sample rate
        sample_frame = ttk.Frame(convert_defaults_frame)
        sample_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(sample_frame, text="Sample rate:").pack(side=tk.LEFT, padx=(0, 10))
        self.default_sample_rate = tk.StringVar(value=AppConstants.DEFAULT_SETTINGS['convert']['sample_rate'])
        ttk.Combobox(sample_frame, textvariable=self.default_sample_rate,
                    values=AppConstants.SAMPLE_RATE_OPTIONS, state="readonly", width=8).pack(side=tk.LEFT)

        # Default normalize
        self.default_normalize = tk.BooleanVar(value=AppConstants.DEFAULT_SETTINGS['convert']['normalize'])
        ttk.Checkbutton(convert_defaults_frame, text="Enable audio normalization by default",
                       variable=self.default_normalize).pack(anchor=tk.W, pady=5)

        # Split defaults tab
        split_defaults_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(split_defaults_frame, text="Split")

        # Split section description
        split_desc_frame = ttk.Frame(split_defaults_frame)
        split_desc_frame.pack(fill=tk.X, pady=(10, 15))
        ttk.Label(split_desc_frame, text="分割預設設定",
                 font=('Helvetica', 11, 'bold')).pack(anchor=tk.W)
        ttk.Label(split_desc_frame,
                 text="設定檔案分割的預設模式和參數。可按時間長度、檔案大小或指定份數分割。",
                 font=('Helvetica', 9), foreground='#666666',
                 wraplength=500).pack(anchor=tk.W, pady=(2, 0))

        # Default split mode
        split_mode_frame = ttk.Frame(split_defaults_frame)
        split_mode_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(split_mode_frame, text="Default split mode:").pack(side=tk.LEFT, padx=(0, 10))
        self.default_split_mode = tk.StringVar(value=AppConstants.DEFAULT_SETTINGS['split']['mode'])
        ttk.Combobox(split_mode_frame, textvariable=self.default_split_mode,
                    values=AppConstants.SPLIT_MODE_OPTIONS, state="readonly", width=10).pack(side=tk.LEFT)

        # Default split duration
        duration_frame = ttk.Frame(split_defaults_frame)
        duration_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(duration_frame, text="Default duration (seconds):").pack(side=tk.LEFT, padx=(0, 10))
        self.default_split_duration = tk.StringVar(value=AppConstants.DEFAULT_SETTINGS['split']['duration'])
        ttk.Entry(duration_frame, textvariable=self.default_split_duration, width=10).pack(side=tk.LEFT)

        # Default keep original
        self.default_keep_original = tk.BooleanVar(value=AppConstants.DEFAULT_SETTINGS['split']['keep_original'])
        ttk.Checkbutton(split_defaults_frame, text="Keep original files after splitting by default",
                       variable=self.default_keep_original).pack(anchor=tk.W, pady=5)

        # General settings tab
        general_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(general_frame, text="General")

        # General section description
        general_desc_frame = ttk.Frame(general_frame)
        general_desc_frame.pack(fill=tk.X, pady=(10, 15))
        ttk.Label(general_desc_frame, text="一般預設設定",
                 font=('Helvetica', 11, 'bold')).pack(anchor=tk.W)
        ttk.Label(general_desc_frame,
                 text="設定檔案輸出位置、命名規則和自動化行為。這些設定會影響所有操作。",
                 font=('Helvetica', 9), foreground='#666666',
                 wraplength=500).pack(anchor=tk.W, pady=(2, 0))

        # Output directory preference
        output_frame = ttk.Frame(general_frame)
        output_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(output_frame, text="Default output location:").pack(anchor=tk.W, pady=2)
        ttk.Label(output_frame, text="（設定轉檔後的檔案儲存位置）",
                 font=('Helvetica', 8), foreground='#888888').pack(anchor=tk.W)
        self.output_location = tk.StringVar(value=AppConstants.DEFAULT_SETTINGS['general']['output_location'])
        ttk.Radiobutton(output_frame, text="Same as source file", value="same",
                       variable=self.output_location).pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(output_frame, text="Ask every time", value="ask",
                       variable=self.output_location).pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(output_frame, text="Fixed folder:", value="fixed",
                       variable=self.output_location).pack(anchor=tk.W, padx=20)

        # Fixed output directory
        fixed_dir_frame = ttk.Frame(general_frame)
        fixed_dir_frame.pack(anchor=tk.W, pady=5, padx=40)
        self.fixed_output_dir = tk.StringVar()
        ttk.Entry(fixed_dir_frame, textvariable=self.fixed_output_dir, width=30).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(fixed_dir_frame, text="Browse", command=self.browse_fixed_dir, width=8).pack(side=tk.LEFT)

        # File naming
        naming_frame = ttk.Frame(general_frame)
        naming_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(naming_frame, text="File naming:").pack(anchor=tk.W, pady=2)
        ttk.Label(naming_frame, text="（設定輸出檔案的命名規則）",
                 font=('Helvetica', 8), foreground='#888888').pack(anchor=tk.W)
        self.naming_style = tk.StringVar(value=AppConstants.DEFAULT_SETTINGS['general']['naming_style'])
        ttk.Radiobutton(naming_frame, text="Keep original name", value="original",
                       variable=self.naming_style).pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(naming_frame, text="Add suffix '_converted'", value="suffix",
                       variable=self.naming_style).pack(anchor=tk.W, padx=20)

        # Auto-clear completed files
        self.auto_clear = tk.BooleanVar(value=AppConstants.DEFAULT_SETTINGS['general']['auto_clear'])
        ttk.Checkbutton(general_frame, text="Auto-clear completed files from lists",
                       variable=self.auto_clear).pack(anchor=tk.W, pady=5)

        # Buttons section with instructions
        buttons_section = ttk.Frame(main_frame)
        buttons_section.pack(fill=tk.X, pady=(20, 0))

        # Button instructions
        instruction_frame = ttk.Frame(buttons_section)
        instruction_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(instruction_frame, text="操作說明:",
                 font=('Helvetica', 10, 'bold')).pack(anchor=tk.W)

        instructions_text = ("• Apply Settings: 立即套用設定到 Convert 和 Split 頁面\n"
                           "• Reset to Defaults: 重設所有設定為原廠預設值\n"
                           "• Save Settings: 永久儲存設定（程式重啟後保留）")
        ttk.Label(instruction_frame, text=instructions_text,
                 font=('Helvetica', 9), foreground='#666666',
                 justify=tk.LEFT).pack(anchor=tk.W, pady=(5, 0))

        # Buttons frame
        buttons_frame = ttk.Frame(buttons_section)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(buttons_frame, text="Apply Settings",
                  command=self.apply_all_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Reset to Defaults",
                  command=self.reset_to_defaults).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Save Settings",
                  command=self.save_settings).pack(side=tk.LEFT, padx=5)

        # Initialize default variables with loaded settings
        self.init_default_variables()

    def setup_history_tab(self):
        """Setup the History tab"""
        main_frame = ttk.Frame(self.history_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(title_frame, text="Processing History", font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT)

        # Clear button
        ttk.Button(title_frame, text="Clear History", command=self.clear_history).pack(side=tk.RIGHT)

        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        self.stats_frame_inner = ttk.Frame(stats_frame)
        self.stats_frame_inner.pack(fill=tk.X)

        # History notebook for different types
        history_notebook = ttk.Notebook(main_frame)
        history_notebook.pack(fill=tk.BOTH, expand=True)

        # Convert history tab
        convert_history_frame = ttk.Frame(history_notebook)
        history_notebook.add(convert_history_frame, text="Conversions")

        # Conversion history listbox
        convert_frame = ttk.Frame(convert_history_frame, padding="5")
        convert_frame.pack(fill=tk.BOTH, expand=True)

        convert_scrollbar = ttk.Scrollbar(convert_frame)
        convert_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.convert_history_listbox = tk.Listbox(convert_frame, yscrollcommand=convert_scrollbar.set,
                                                 font=('Courier', 10))
        self.convert_history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        convert_scrollbar.config(command=self.convert_history_listbox.yview)

        # Split history tab
        split_history_frame = ttk.Frame(history_notebook)
        history_notebook.add(split_history_frame, text="Splits")

        split_frame = ttk.Frame(split_history_frame, padding="5")
        split_frame.pack(fill=tk.BOTH, expand=True)

        split_scrollbar = ttk.Scrollbar(split_frame)
        split_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.split_history_listbox = tk.Listbox(split_frame, yscrollcommand=split_scrollbar.set,
                                               font=('Courier', 10))
        self.split_history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        split_scrollbar.config(command=self.split_history_listbox.yview)

        # Error log tab
        error_frame = ttk.Frame(history_notebook)
        history_notebook.add(error_frame, text="Errors")

        error_text_frame = ttk.Frame(error_frame, padding="5")
        error_text_frame.pack(fill=tk.BOTH, expand=True)

        error_scrollbar = ttk.Scrollbar(error_text_frame)
        error_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.error_log = tk.Text(error_text_frame, wrap=tk.WORD, yscrollcommand=error_scrollbar.set,
                                font=('Courier', 9), height=15)
        self.error_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        error_scrollbar.config(command=self.error_log.yview)


        # Initial stats update
        self.update_statistics()

    def update_statistics(self):
        """Update the statistics display"""
        # Clear existing stats
        for widget in self.stats_frame_inner.winfo_children():
            widget.destroy()

        total_conversions = len(self.conversion_history)
        total_splits = len(self.split_history)

        # Create stats labels
        ttk.Label(self.stats_frame_inner,
                 text=f"Total Conversions: {total_conversions}").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(self.stats_frame_inner,
                 text=f"Total Splits: {total_splits}").pack(side=tk.LEFT, padx=(0, 20))

        if total_conversions > 0:
            # Most common format
            formats = [entry['format'] for entry in self.conversion_history]
            most_common = max(set(formats), key=formats.count) if formats else "N/A"
            ttk.Label(self.stats_frame_inner,
                     text=f"Most Used Format: {most_common}").pack(side=tk.LEFT)

    def add_conversion_history(self, filename, input_format, output_format, success=True):
        """Add conversion to history"""
        from datetime import datetime
        entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'filename': filename,
            'input_format': input_format,
            'format': output_format,
            'success': success
        }
        self.conversion_history.append(entry)

        # Add to listbox
        status = "✓" if success else "✗"
        display_text = f"{entry['timestamp']} {status} {filename} → {output_format}"
        self.convert_history_listbox.insert(tk.END, display_text)

        # Auto-scroll to bottom
        self.convert_history_listbox.see(tk.END)

        self.update_statistics()

    def add_split_history(self, filename, mode, value, parts_created, success=True):
        """Add split operation to history"""
        from datetime import datetime
        entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'filename': filename,
            'mode': mode,
            'value': value,
            'parts': parts_created,
            'success': success
        }
        self.split_history.append(entry)

        # Add to listbox
        status = "✓" if success else "✗"
        display_text = f"{entry['timestamp']} {status} {filename} → {parts_created} parts ({mode}: {value})"
        self.split_history_listbox.insert(tk.END, display_text)

        # Auto-scroll to bottom
        self.split_history_listbox.see(tk.END)

        self.update_statistics()

    def log_error(self, operation, filename, error_msg):
        """Log an error to the error log"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {operation} - {filename}\nError: {error_msg}\n{'='*50}\n"

        self.error_log.insert(tk.END, log_entry)
        self.error_log.see(tk.END)

    def clear_history(self):
        """Clear all history"""
        self.conversion_history = []
        self.split_history = []
        self.convert_history_listbox.delete(0, tk.END)
        self.split_history_listbox.delete(0, tk.END)
        self.error_log.delete('1.0', tk.END)
        self.update_statistics()

    def browse_fixed_dir(self):
        """Browse for fixed output directory"""
        directory = filedialog.askdirectory(title="Select Default Output Directory")
        if directory:
            self.fixed_output_dir.set(directory)

    def apply_all_settings(self):
        """Apply all default settings to respective tabs"""
        # Apply Convert settings
        self.output_format.set(self.default_format.get())
        self.bitrate.set(self.default_bitrate.get())
        self.sample_rate.set(self.default_sample_rate.get())
        self.normalize.set(self.default_normalize.get())

        # Apply Split settings
        self.split_mode.set(self.default_split_mode.get())
        self.split_duration.set(self.default_split_duration.get())
        self.keep_original.set(self.default_keep_original.get())
        self.update_split_mode()  # Update the display

        messagebox.showinfo("Settings Applied", "All default settings have been applied to the Convert and Split tabs.")

    def reset_to_defaults(self):
        """Reset all settings to factory defaults"""
        # Convert defaults
        convert_settings = AppConstants.DEFAULT_SETTINGS['convert']
        self.default_format.set(convert_settings['format'])
        self.default_bitrate.set(convert_settings['bitrate'])
        self.default_sample_rate.set(convert_settings['sample_rate'])
        self.default_normalize.set(convert_settings['normalize'])

        # Split defaults
        split_settings = AppConstants.DEFAULT_SETTINGS['split']
        self.default_split_mode.set(split_settings['mode'])
        self.default_split_duration.set(split_settings['duration'])
        self.default_keep_original.set(split_settings['keep_original'])

        # General defaults
        general_settings = AppConstants.DEFAULT_SETTINGS['general']
        self.output_location.set(general_settings['output_location'])
        self.fixed_output_dir.set(general_settings['fixed_output_dir'])
        self.naming_style.set(general_settings['naming_style'])
        self.auto_clear.set(general_settings['auto_clear'])

        messagebox.showinfo("Reset Complete", "All settings have been reset to factory defaults.")

    def save_settings(self):
        """Save current settings to file"""
        settings = {
            'convert': {
                'format': self.default_format.get(),
                'bitrate': self.default_bitrate.get(),
                'sample_rate': self.default_sample_rate.get(),
                'normalize': self.default_normalize.get()
            },
            'split': {
                'mode': self.default_split_mode.get(),
                'duration': self.default_split_duration.get(),
                'keep_original': self.default_keep_original.get()
            },
            'general': {
                'output_location': self.output_location.get(),
                'fixed_output_dir': self.fixed_output_dir.get(),
                'naming_style': self.naming_style.get(),
                'auto_clear': self.auto_clear.get()
            }
        }

        try:
            settings_file = Path.home() / '.audio_converter_settings.json'
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            messagebox.showinfo("Settings Saved", f"Settings saved to {settings_file}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save settings: {e}")

    def load_settings(self):
        """Load settings from file"""
        try:
            settings_file = Path.home() / '.audio_converter_settings.json'
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)

                # Apply loaded settings to main variables
                convert_settings = settings.get('convert', {})
                self.output_format.set(convert_settings.get('format', 'mp3'))
                self.bitrate.set(convert_settings.get('bitrate', '192k'))
                self.sample_rate.set(convert_settings.get('sample_rate', '44100'))
                self.normalize.set(convert_settings.get('normalize', False))

                # Store settings for later use in history tab
                self.loaded_settings = settings
            else:
                self.loaded_settings = None
        except Exception as e:
            print(f"Failed to load settings: {e}")
            self.loaded_settings = None

    def init_default_variables(self):
        """Initialize default variables with loaded settings"""
        if hasattr(self, 'loaded_settings') and self.loaded_settings:
            convert_settings = self.loaded_settings.get('convert', {})
            split_settings = self.loaded_settings.get('split', {})
            general_settings = self.loaded_settings.get('general', {})

            # Set default variables
            self.default_format.set(convert_settings.get('format', 'mp3'))
            self.default_bitrate.set(convert_settings.get('bitrate', '192k'))
            self.default_sample_rate.set(convert_settings.get('sample_rate', '44100'))
            self.default_normalize.set(convert_settings.get('normalize', False))

            self.default_split_mode.set(split_settings.get('mode', 'duration'))
            self.default_split_duration.set(split_settings.get('duration', '300'))
            self.default_keep_original.set(split_settings.get('keep_original', False))

            self.output_location.set(general_settings.get('output_location', 'same'))
            self.fixed_output_dir.set(general_settings.get('fixed_output_dir', ''))
            self.naming_style.set(general_settings.get('naming_style', 'original'))
            self.auto_clear.set(general_settings.get('auto_clear', False))

    def on_closing(self):
        """Handle application closing"""
        # Auto-save settings
        try:
            self.save_settings()
        except:
            pass  # Don't let save errors prevent closing
        self.root.destroy()


    def update_split_mode(self):
        """Update split input based on selected mode"""
        mode = self.split_mode.get()
        if mode == "duration":
            self.split_label.config(text="Duration (seconds):")
            self.split_entry.config(textvariable=self.split_duration)
            self.split_unit.config(text="(5 minutes = 300)")
        elif mode == "size":
            self.split_label.config(text="Max size (MB):")
            self.split_entry.config(textvariable=self.split_size)
            self.split_unit.config(text="(e.g., 100 for 100MB)")
        else:  # parts
            self.split_label.config(text="Number of parts:")
            parts_var = tk.StringVar(value="2")
            self.split_entry.config(textvariable=parts_var)
            self.split_unit.config(text="(equal duration parts)")

    def add_files(self, tab):
        """Add files to specified tab"""
        files = filedialog.askopenfilenames(
            title="Select Media Files",
            filetypes=AppConstants.get_file_filter('all')
        )

        if tab == 'convert':
            listbox = self.convert_listbox
            file_list = self.convert_files
        else:  # split
            listbox = self.split_listbox
            file_list = self.split_files

        for file in files:
            if file not in file_list:
                file_list.append(file)
                # Show file name and size
                size_mb = os.path.getsize(file) / (1024 * 1024)
                listbox.insert(tk.END, f"{os.path.basename(file)} ({size_mb:.1f} MB)")

    def add_folder(self, tab):
        """Add all audio files from a folder"""
        folder = filedialog.askdirectory(title="Select Folder")
        if not folder:
            return

        media_extensions = AppConstants.MEDIA_EXTENSIONS

        if tab == 'convert':
            listbox = self.convert_listbox
            file_list = self.convert_files
        else:
            listbox = self.split_listbox
            file_list = self.split_files

        for file in Path(folder).glob('**/*'):
            if file.suffix.lower() in media_extensions:
                file_path = str(file)
                if file_path not in file_list:
                    file_list.append(file_path)
                    size_mb = file.stat().st_size / (1024 * 1024)
                    listbox.insert(tk.END, f"{file.name} ({size_mb:.1f} MB)")

    def add_large_files(self):
        """Add only files larger than 100MB"""
        folder = filedialog.askdirectory(title="Select Folder")
        if not folder:
            return

        media_extensions = AppConstants.MEDIA_EXTENSIONS
        added = 0

        for file in Path(folder).glob('**/*'):
            if file.suffix.lower() in media_extensions:
                size_mb = file.stat().st_size / (1024 * 1024)
                if size_mb > 100:  # Only files > 100MB
                    file_path = str(file)
                    if file_path not in self.split_files:
                        self.split_files.append(file_path)
                        self.split_listbox.insert(tk.END, f"{file.name} ({size_mb:.1f} MB)")
                        added += 1

        if added > 0:
            messagebox.showinfo("Files Added", f"Added {added} files larger than 100MB")
        else:
            messagebox.showinfo("No Large Files", "No audio files larger than 100MB found")

    def remove_selected(self, tab):
        """Remove selected files"""
        if tab == 'convert':
            listbox = self.convert_listbox
            file_list = self.convert_files
        else:
            listbox = self.split_listbox
            file_list = self.split_files

        selected = listbox.curselection()
        for index in reversed(selected):
            listbox.delete(index)
            del file_list[index]

    def clear_files(self, tab):
        """Clear all files"""
        if tab == 'convert':
            self.convert_listbox.delete(0, tk.END)
            self.convert_files = []
        else:
            self.split_listbox.delete(0, tk.END)
            self.split_files = []

    def convert_files(self):
        """Convert files in the Convert tab"""
        print("Convert button clicked!")  # Debug

        if not self.convert_files:
            messagebox.showwarning("No Files", "Please add files to convert")
            return

        print(f"Files to convert: {len(self.convert_files)}")  # Debug

        # Determine output location based on settings
        output_location = getattr(self, 'output_location', None)
        if output_location and output_location.get() == "ask":
            # Ask user for output directory
            output_dir = filedialog.askdirectory(title="Select Output Directory")
            if not output_dir:
                return
        elif output_location and output_location.get() == "fixed":
            # Use fixed directory
            fixed_dir = getattr(self, 'fixed_output_dir', None)
            if fixed_dir and fixed_dir.get():
                output_dir = fixed_dir.get()
                if not os.path.exists(output_dir):
                    messagebox.showerror("Error", f"Fixed output directory does not exist: {output_dir}")
                    return
            else:
                messagebox.showwarning("No Fixed Directory", "Please set a fixed output directory in Settings")
                return
        else:
            # Default: same as source (None means same directory)
            output_dir = None

        self.convert_status.config(text="Converting...")
        self.convert_progress['value'] = 0

        # Start conversion in thread
        thread = threading.Thread(target=self._convert_worker, args=(output_dir,))
        thread.daemon = True
        thread.start()

    def _convert_worker(self, custom_output_dir=None):
        """Worker thread for conversion"""
        print(f"Worker thread started with {len(self.convert_files)} files")  # Debug
        total = len(self.convert_files)

        for i, file_path in enumerate(self.convert_files):
            progress = ((i + 1) / total) * 100
            self.root.after(0, lambda p=progress: self.convert_progress.configure(value=p))

            filename = os.path.basename(file_path)
            self.root.after(0, lambda f=filename: self.convert_status.config(text=f"Converting: {f}"))

            try:
                # Determine output directory based on settings
                if custom_output_dir:
                    output_dir = custom_output_dir
                else:
                    output_dir = os.path.dirname(file_path)

                # Build output filename based on naming style setting
                base_name = Path(file_path).stem
                naming_style = getattr(self, 'naming_style', None)

                if naming_style and naming_style.get() == "suffix":
                    output_filename = f"{base_name}_converted.{self.output_format.get()}"
                else:
                    # Default: keep original name (but change extension)
                    output_filename = f"{base_name}.{self.output_format.get()}"

                output_file = os.path.join(output_dir, output_filename)

                # Use new design pattern for conversion
                processor = MediaProcessorBuilder.create_converter(
                    format=self.output_format.get(),
                    bitrate=self.bitrate.get(),
                    sample_rate=self.sample_rate.get(),
                    normalize=self.normalize.get()
                )

                output_params = {
                    'output_file': output_file,
                    'output_dir': output_dir,
                    'naming_style': naming_style
                }

                success = processor.process_file(file_path, output_params)
                if not success:
                    raise Exception("Conversion failed")

                # Add to history
                input_ext = Path(file_path).suffix.lower()
                self.add_conversion_history(filename, input_ext, self.output_format.get(), True)

            except Exception as e:
                error_msg = str(e)
                print(f"Error converting {file_path}: {error_msg}")
                import traceback
                traceback.print_exc()  # Print full error

                # Log error and add failed conversion to history
                self.log_error("Conversion", filename, error_msg)
                input_ext = Path(file_path).suffix.lower()
                self.add_conversion_history(filename, input_ext, self.output_format.get(), False)

        # Check if auto-clear is enabled
        auto_clear = getattr(self, 'auto_clear', None)
        if auto_clear and auto_clear.get():
            # Clear completed files from the list
            self.root.after(0, self._clear_completed_convert_files)

        self.root.after(0, lambda: self.convert_status.config(text=f"✓ Converted {total} files"))
        self.root.after(0, lambda: messagebox.showinfo("Success", f"Converted {total} files successfully!"))

    def split_files_action(self):
        """Split files in the Split tab"""
        if not self.split_files:
            messagebox.showwarning("No Files", "Please add files to split")
            return

        self.split_status.config(text="Splitting...")
        self.split_progress['value'] = 0

        # Start splitting in thread
        thread = threading.Thread(target=self._split_worker)
        thread.daemon = True
        thread.start()

    def _split_worker(self):
        """Worker thread for splitting"""
        total = len(self.split_files)

        for i, file_path in enumerate(self.split_files):
            progress = ((i + 1) / total) * 100
            self.root.after(0, lambda p=progress: self.split_progress.configure(value=p))

            filename = os.path.basename(file_path)
            self.root.after(0, lambda f=filename: self.split_status.config(text=f"Splitting: {f}"))

            try:
                # Use new design pattern for splitting
                if self.split_mode.get() == "duration":
                    processor = MediaProcessorBuilder.create_splitter('duration', duration=int(self.split_duration.get()))
                elif self.split_mode.get() == "size":
                    processor = MediaProcessorBuilder.create_splitter('size', size=int(self.split_size.get()))
                else:  # parts
                    processor = MediaProcessorBuilder.create_splitter('parts', parts=int(self.split_entry.get()))

                output_params = {'keep_original': self.keep_original.get()}
                success = processor.process_file(file_path, output_params)
                parts_created = 1 if success else 0  # Simplified for now
                # Add to history
                mode = self.split_mode.get()
                if mode == "duration":
                    value = self.split_duration.get() + "s"
                elif mode == "size":
                    value = self.split_size.get() + "MB"
                else:
                    value = self.split_entry.get() + " parts"

                self.add_split_history(filename, mode, value, parts_created, True)

            except Exception as e:
                error_msg = str(e)
                print(f"Error splitting {file_path}: {error_msg}")
                self.log_error("Split", filename, error_msg)
                self.add_split_history(filename, self.split_mode.get(), "failed", 0, False)

        # Check if auto-clear is enabled
        auto_clear = getattr(self, 'auto_clear', None)
        if auto_clear and auto_clear.get():
            # Clear completed files from the list
            self.root.after(0, self._clear_completed_split_files)

        self.root.after(0, lambda: self.split_status.config(text=f"✓ Split {total} files"))
        self.root.after(0, lambda: messagebox.showinfo("Success", f"Split {total} files successfully!"))

    def _split_single_file(self, file_path):
        """Split a single file based on settings"""
        # Get file duration
        probe_cmd = ['ffprobe', '-v', 'error', '-show_entries',
                    'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                    file_path]
        result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        total_duration = float(result.stdout.strip())

        # Calculate split parameters
        if self.split_mode.get() == "duration":
            part_duration = float(self.split_duration.get())
            num_parts = int(total_duration / part_duration) + (1 if total_duration % part_duration > 0 else 0)
        elif self.split_mode.get() == "size":
            # Estimate based on file size
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            max_size_mb = float(self.split_size.get())
            num_parts = int(file_size_mb / max_size_mb) + (1 if file_size_mb % max_size_mb > 0 else 0)
            part_duration = total_duration / num_parts
        else:  # parts mode
            num_parts = int(self.split_entry.get())
            part_duration = total_duration / num_parts

        if num_parts <= 1:
            return  # No need to split

        # Split the file
        base_path = Path(file_path)
        output_dir = base_path.parent
        base_name = base_path.stem
        extension = base_path.suffix

        for i in range(num_parts):
            start_time = i * part_duration
            duration = min(part_duration, total_duration - start_time)

            output_name = f"{base_name}_part{i+1:02d}{extension}"
            output_path = output_dir / output_name

            split_cmd = ['ffmpeg', '-i', file_path,
                        '-ss', str(start_time),
                        '-t', str(duration),
                        '-c', 'copy',
                        '-y', str(output_path)]

            subprocess.run(split_cmd, check=True, capture_output=True)

        # Remove original if requested
        if not self.keep_original.get():
            os.remove(file_path)

        return num_parts

    def _clear_completed_convert_files(self):
        """Clear all files from convert list after successful processing"""
        self.convert_files.clear()
        self.convert_listbox.delete(0, tk.END)

    def _clear_completed_split_files(self):
        """Clear all files from split list after successful processing"""
        self.split_files.clear()
        self.split_listbox.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = TabbedMediaConverter(root)
    root.mainloop()