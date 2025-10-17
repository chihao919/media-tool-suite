#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import subprocess
import webbrowser
import tkinter.messagebox as messagebox
from pathlib import Path
import json

# Import new design pattern modules
from app_constants import AppConstants
from media_processor import MediaProcessor, MediaProcessorBuilder
from media_handlers import MediaHandlerFactory
from youtube_downloader import YouTubeDownloader
from screen_recorder import ScreenRecorder, ScreenRecorderBuilder

class TabbedMediaConverter:
    def __init__(self, root):
        self.root = root
        self.root.title(AppConstants.APP_NAME)
        self.root.geometry(f"{AppConstants.WINDOW_WIDTH}x{AppConstants.WINDOW_HEIGHT}")

        # Variables for Convert tab
        self.convert_file_list = []
        # Audio settings
        self.audio_format = tk.StringVar(value="mp3")
        self.audio_bitrate = tk.StringVar(value="192k")
        self.sample_rate = tk.StringVar(value="44100")
        self.normalize = tk.BooleanVar(value=False)
        # Video settings
        self.video_format = tk.StringVar(value="mp4")
        self.video_bitrate = tk.StringVar(value="2M")
        # Current mode
        self.media_type = tk.StringVar(value="auto")  # auto, audio, video

        # Variables for Split tab
        self.split_files = []
        self.split_mode = tk.StringVar(value="duration")
        self.split_size = tk.StringVar(value="100")  # MB
        self.split_duration = tk.StringVar(value="300")  # seconds
        self.split_parts = tk.StringVar(value="3")  # number of parts
        self.keep_original = tk.BooleanVar(value=False)

        # YouTube downloader variables
        self.youtube_url = tk.StringVar()
        self.youtube_quality = tk.StringVar(value="720p")
        self.youtube_format = tk.StringVar(value="mp4")
        self.youtube_mode = tk.StringVar(value="download")  # download, split, audio, playlist
        self.max_downloads = tk.IntVar(value=3)
        self.youtube_downloader = None

        # Screen recording variables
        self.recording_framerate = tk.StringVar(value="30")
        self.recording_quality = tk.StringVar(value="medium")
        self.recording_video_device = tk.StringVar(value="1")
        self.recording_audio_device = tk.StringVar(value="0")
        self.screen_recorder = None
        self.is_recording = False

        # Load saved settings first
        self.load_settings()

        self.create_widgets()

        # Setup close event to save settings
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_format_ui(self):
        """Update format UI based on selected media type"""
        # Clean up previous dynamic labels
        for label in self.dynamic_labels:
            label.destroy()
        self.dynamic_labels.clear()

        # Hide all widgets first
        for widget_dict in [self.audio_widgets, self.video_widgets]:
            for widget in widget_dict.values():
                widget.grid_remove()

        media_type = self.media_type.get()

        if media_type == "audio":
            # Show audio widgets
            row = 0
            self.audio_widgets['format_label'].grid(row=row, column=0, sticky=tk.W, pady=2)
            self.audio_widgets['format_combo'].grid(row=row, column=1, padx=5, pady=2)
            row += 1
            self.audio_widgets['bitrate_label'].grid(row=row, column=0, sticky=tk.W, pady=2)
            self.audio_widgets['bitrate_combo'].grid(row=row, column=1, padx=5, pady=2)
            row += 1
            self.audio_widgets['sample_label'].grid(row=row, column=0, sticky=tk.W, pady=2)
            self.audio_widgets['sample_combo'].grid(row=row, column=1, padx=5, pady=2)

        elif media_type == "video":
            # Show video widgets
            row = 0
            self.video_widgets['format_label'].grid(row=row, column=0, sticky=tk.W, pady=2)
            self.video_widgets['format_combo'].grid(row=row, column=1, padx=5, pady=2)
            row += 1
            self.video_widgets['bitrate_label'].grid(row=row, column=0, sticky=tk.W, pady=2)
            self.video_widgets['bitrate_combo'].grid(row=row, column=1, padx=5, pady=2)
            row += 1
            self.video_widgets['audio_bitrate_label'].grid(row=row, column=0, sticky=tk.W, pady=2)
            self.video_widgets['audio_bitrate_combo'].grid(row=row, column=1, padx=5, pady=2)

        else:  # auto
            # Create and track dynamic labels with larger font
            row = 0
            audio_format_label = ttk.Label(self.format_frame, text="Audio Format:", font=('Helvetica', 10, 'bold'))
            audio_format_label.grid(row=row, column=0, sticky=tk.W, pady=2)
            self.dynamic_labels.append(audio_format_label)
            self.audio_widgets['format_combo'].grid(row=row, column=1, padx=5, pady=2)

            row += 1
            video_format_label = ttk.Label(self.format_frame, text="Video Format:", font=('Helvetica', 10, 'bold'))
            video_format_label.grid(row=row, column=0, sticky=tk.W, pady=2)
            self.dynamic_labels.append(video_format_label)
            self.video_widgets['format_combo'].grid(row=row, column=1, padx=5, pady=2)

            row += 1
            quality_label = ttk.Label(self.format_frame, text="Quality:", font=('Helvetica', 10, 'italic'))
            quality_label.grid(row=row, column=0, sticky=tk.W, pady=(10,2))
            self.dynamic_labels.append(quality_label)

            row += 1
            self.audio_widgets['bitrate_label'].grid(row=row, column=0, sticky=tk.W, pady=2)
            self.audio_widgets['bitrate_combo'].grid(row=row, column=1, padx=5, pady=2)

            row += 1
            self.video_widgets['bitrate_label'].grid(row=row, column=0, sticky=tk.W, pady=2)
            self.video_widgets['bitrate_combo'].grid(row=row, column=1, padx=5, pady=2)

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
        self.recording_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.convert_tab, text="🔄 Convert")
        self.notebook.add(self.split_tab, text="✂️ Split")
        self.notebook.add(self.recording_tab, text="🎥 Screen Record")
        self.notebook.add(self.settings_tab, text="⚙️ Settings")
        self.notebook.add(self.history_tab, text="📊 History")

        # History tracking
        self.conversion_history = []
        self.split_history = []

        # Setup each tab
        self.setup_convert_tab()
        self.setup_split_tab()
        self.setup_recording_tab()
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

        def test_add_files():
            print("ADD FILES BUTTON CLICKED!")
            self.add_files('convert')

        ttk.Button(btn_frame, text="Add Files",
                  command=test_add_files).pack(side=tk.LEFT, padx=5, ipadx=12, ipady=6)
        ttk.Button(btn_frame, text="Add Folder",
                  command=lambda: self.add_folder('convert')).pack(side=tk.LEFT, padx=5, ipadx=12, ipady=6)
        ttk.Button(btn_frame, text="Remove",
                  command=lambda: self.remove_selected('convert')).pack(side=tk.LEFT, padx=5, ipadx=12, ipady=6)
        ttk.Button(btn_frame, text="Clear",
                  command=lambda: self.clear_files('convert')).pack(side=tk.LEFT, padx=5, ipadx=12, ipady=6)

        # Settings frame
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill=tk.X, pady=10)

        # Left side - Media Type Selection
        type_frame = ttk.LabelFrame(settings_frame, text="Media Type", padding="10")
        type_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        ttk.Radiobutton(type_frame, text="Auto Detect", variable=self.media_type,
                        value="auto", command=self.update_format_ui).pack(anchor=tk.W)
        ttk.Radiobutton(type_frame, text="Audio", variable=self.media_type,
                        value="audio", command=self.update_format_ui).pack(anchor=tk.W)
        ttk.Radiobutton(type_frame, text="Video", variable=self.media_type,
                        value="video", command=self.update_format_ui).pack(anchor=tk.W)

        # Middle - Format settings
        self.format_frame = ttk.LabelFrame(settings_frame, text="Format Settings", padding="10")
        self.format_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Configure column weights for better spacing
        self.format_frame.columnconfigure(0, weight=0, minsize=120)  # Label column
        self.format_frame.columnconfigure(1, weight=1, minsize=120)  # Combo column

        # Audio format widgets
        self.audio_widgets = {}
        self.audio_widgets['format_label'] = ttk.Label(self.format_frame, text="Audio Format:")
        self.audio_widgets['format_combo'] = ttk.Combobox(self.format_frame, textvariable=self.audio_format,
                                                          values=AppConstants.AUDIO_FORMAT_OPTIONS,
                                                          state="readonly", width=15)
        self.audio_widgets['bitrate_label'] = ttk.Label(self.format_frame, text="Audio Bitrate:")
        self.audio_widgets['bitrate_combo'] = ttk.Combobox(self.format_frame, textvariable=self.audio_bitrate,
                                                           values=["128k", "192k", "256k", "320k"],
                                                           state="readonly", width=15)
        self.audio_widgets['sample_label'] = ttk.Label(self.format_frame, text="Sample Rate:")
        self.audio_widgets['sample_combo'] = ttk.Combobox(self.format_frame, textvariable=self.sample_rate,
                                                          values=["44100", "48000", "96000"],
                                                          state="readonly", width=15)

        # Video format widgets
        self.video_widgets = {}
        self.video_widgets['format_label'] = ttk.Label(self.format_frame, text="Video Format:")
        self.video_widgets['format_combo'] = ttk.Combobox(self.format_frame, textvariable=self.video_format,
                                                          values=AppConstants.VIDEO_FORMAT_OPTIONS,
                                                          state="readonly", width=15)
        self.video_widgets['bitrate_label'] = ttk.Label(self.format_frame, text="Video Bitrate:")
        self.video_widgets['bitrate_combo'] = ttk.Combobox(self.format_frame, textvariable=self.video_bitrate,
                                                           values=["1M", "2M", "5M", "10M", "20M"],
                                                           state="readonly", width=15)
        self.video_widgets['audio_bitrate_label'] = ttk.Label(self.format_frame, text="Audio Bitrate:")
        self.video_widgets['audio_bitrate_combo'] = ttk.Combobox(self.format_frame, textvariable=self.audio_bitrate,
                                                                 values=["128k", "192k", "256k", "320k"],
                                                                 state="readonly", width=15)

        # Track dynamic labels for cleanup
        self.dynamic_labels = []

        # Initialize UI
        self.update_format_ui()


        # Right side - Options
        options_frame = ttk.LabelFrame(settings_frame, text="Options", padding="10")
        options_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Checkbutton(options_frame, text="Normalize Audio (-16 LUFS)",
                       variable=self.normalize).pack(anchor=tk.W, pady=5)

        ttk.Label(options_frame, text="Output: Same folder as source",
                 font=('Helvetica', 10, 'italic')).pack(anchor=tk.W, pady=5)


        # Convert button (moved up)
        def test_convert():
            print("=== CONVERT BUTTON CLICKED ===")
            try:
                self.convert_files()
            except Exception as e:
                print(f"Exception in test_convert: {e}")
                import traceback
                traceback.print_exc()

        self.convert_btn = ttk.Button(main_frame, text="🚀 Convert All Files 🚀",
                                     command=test_convert)
        self.convert_btn.pack(pady=15, ipadx=30, ipady=15)

        # Progress bar
        self.convert_progress = ttk.Progressbar(main_frame, mode='determinate')
        self.convert_progress.pack(fill=tk.X, pady=5)

        # Status
        self.convert_status = ttk.Label(main_frame, text="Ready")
        self.convert_status.pack()

    def setup_split_tab(self):
        """Setup the Split tab"""
        # Create main container with left progress and right content
        container = ttk.Frame(self.split_tab, padding="10")
        container.pack(fill=tk.BOTH, expand=True)

        # Left side for shared vertical progress bar
        progress_frame = ttk.Frame(container)
        progress_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Shared vertical progress bar
        ttk.Label(progress_frame, text="Progress", font=('Helvetica', 10, 'bold'), foreground='#2E8B57').pack(pady=(0, 5))

        # Create custom progress bar using Canvas (0.5cm ≈ 38 pixels wide)
        self.shared_progress = tk.Canvas(progress_frame, width=38, height=400, bg='#E0E0E0',
                                       relief='sunken', bd=1, highlightthickness=0)
        self.shared_progress.pack(pady=5)

        # Initialize progress bar background
        self._progress_bg = self.shared_progress.create_rectangle(0, 0, 38, 400,
                                                                fill='#E0E0E0', outline='')
        self._progress_fill = self.shared_progress.create_rectangle(0, 400, 38, 400,
                                                                  fill='#2E8B57', outline='')
        self._progress_value = 0

        # Progress percentage label with better contrast
        self.progress_percent = ttk.Label(progress_frame, text="0%", font=('Helvetica', 14, 'bold'),
                                        foreground='#2E8B57', background='white')
        self.progress_percent.pack(pady=(8, 0))

        # Combined status with better visibility
        self.combined_status = ttk.Label(progress_frame, text="Ready", font=('Helvetica', 10, 'bold'),
                                       wraplength=80, foreground='#2E8B57', background='white')
        self.combined_status.pack(pady=(10, 0))

        # Right side for content (YouTube + Media Files)
        main_frame = ttk.Frame(container)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # YouTube download section
        youtube_frame = ttk.LabelFrame(main_frame, text="YouTube Download & Split", padding="10")
        youtube_frame.pack(fill=tk.X, pady=(0, 10))

        # URL input
        url_frame = ttk.Frame(youtube_frame)
        url_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(url_frame, text="YouTube URL:").pack(side=tk.LEFT, padx=(0, 10))
        self.youtube_url = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.youtube_url, width=50)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # YouTube options and single download button
        yt_control_frame = ttk.Frame(youtube_frame)
        yt_control_frame.pack(fill=tk.X, pady=5)

        # Mode selection on the left
        mode_frame = ttk.Frame(yt_control_frame)
        mode_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT, padx=(0, 5))
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.youtube_mode,
                                  values=["📥 Download", "⚡ Download & Split", "🎵 Audio Only", "📋 Playlist"],
                                  state="readonly", width=18)
        mode_combo.set("📥 Download")
        mode_combo.pack(side=tk.LEFT, padx=(0, 20))

        # Single large download button on the right
        self.youtube_download_btn = ttk.Button(yt_control_frame, text="🔽 DOWNLOAD",
                                             command=self.download_youtube_unified,
                                             style="Accent.TButton")
        self.youtube_download_btn.pack(side=tk.RIGHT, ipadx=20, ipady=10)

        # YouTube options
        yt_options = ttk.Frame(youtube_frame)
        yt_options.pack(fill=tk.X, pady=5)

        ttk.Label(yt_options, text="Format:").pack(side=tk.LEFT, padx=(0, 5))
        format_combo = ttk.Combobox(yt_options, textvariable=self.youtube_format,
                                    values=["mp4", "webm", "mkv", "flv", "avi"],
                                    state="readonly", width=8)
        format_combo.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(yt_options, text="Quality:").pack(side=tk.LEFT, padx=(0, 5))
        quality_combo = ttk.Combobox(yt_options, textvariable=self.youtube_quality,
                                     values=["best", "1080p", "720p", "480p", "360p", "audio"],
                                     state="readonly", width=10)
        quality_combo.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(yt_options, text="Max Downloads:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Spinbox(yt_options, from_=1, to=10, textvariable=self.max_downloads,
                   width=5).pack(side=tk.LEFT, padx=(0, 15))


        # Note about workflow
        workflow_note = ttk.Label(yt_options, text="💡 下載後可在下方進行分割 →",
                                 font=('Helvetica', 9, 'italic'), foreground='#666666')
        workflow_note.pack(side=tk.LEFT)

        # YouTube progress (now uses shared progress bar)
        # Progress status will be shown in the shared vertical progress bar

        # YouTube status now handled by shared progress bar on left

        # File list (bottom half of right side)
        list_frame = ttk.LabelFrame(main_frame, text="Media Files to Split", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Move Split Selected Files button here
        split_btn_frame = ttk.Frame(list_frame)
        split_btn_frame.pack(fill=tk.X, pady=(0, 10))

        self.split_btn = ttk.Button(split_btn_frame, text="✂️ Split Selected Files",
                                   command=self.split_files_action)
        self.split_btn.pack(side=tk.LEFT, padx=5, ipadx=20, ipady=8)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.split_listbox = tk.Listbox(list_frame, height=8, yscrollcommand=scrollbar.set)
        self.split_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.split_listbox.yview)

        # File buttons - Two rows for better layout
        # First row of buttons
        btn_frame_row1 = ttk.Frame(list_frame)
        btn_frame_row1.pack(fill=tk.X, pady=(5, 2))

        ttk.Button(btn_frame_row1, text="Add Files",
                  command=lambda: self.add_files('split')).pack(side=tk.LEFT, padx=5, ipadx=12, ipady=6)
        ttk.Button(btn_frame_row1, text="Add Folder",
                  command=self.add_large_files).pack(side=tk.LEFT, padx=5, ipadx=12, ipady=6)

        # Second row of buttons
        btn_frame_row2 = ttk.Frame(list_frame)
        btn_frame_row2.pack(fill=tk.X, pady=(2, 5))

        ttk.Button(btn_frame_row2, text="Remove",
                  command=lambda: self.remove_selected('split')).pack(side=tk.LEFT, padx=5, ipadx=12, ipady=6)
        ttk.Button(btn_frame_row2, text="Clear",
                  command=lambda: self.clear_files('split')).pack(side=tk.LEFT, padx=5, ipadx=12, ipady=6)

        # Split settings (inside Media Files section)
        settings_frame = ttk.LabelFrame(list_frame, text="Split Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(10, 0))

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

        # Progress and status now handled by shared vertical progress bar on the left

    def setup_recording_tab(self):
        """Setup the Screen Recording tab"""
        main_frame = ttk.Frame(self.recording_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Recording status frame
        status_frame = ttk.LabelFrame(main_frame, text="Recording Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.recording_status_label = ttk.Label(
            status_frame,
            text="Ready to record",
            font=('Helvetica', 12, 'bold')
        )
        self.recording_status_label.pack()

        self.recording_time_label = ttk.Label(status_frame, text="00:00:00")
        self.recording_time_label.pack()

        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Recording Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Framerate setting
        framerate_frame = ttk.Frame(settings_frame)
        framerate_frame.pack(fill=tk.X, pady=5)
        ttk.Label(framerate_frame, text="Framerate:", width=15).pack(side=tk.LEFT)
        framerate_combo = ttk.Combobox(
            framerate_frame,
            textvariable=self.recording_framerate,
            values=AppConstants.RECORDING_FRAMERATE_OPTIONS,
            state="readonly",
            width=15
        )
        framerate_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(framerate_frame, text="fps").pack(side=tk.LEFT)

        # Quality setting
        quality_frame = ttk.Frame(settings_frame)
        quality_frame.pack(fill=tk.X, pady=5)
        ttk.Label(quality_frame, text="Quality:", width=15).pack(side=tk.LEFT)
        quality_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.recording_quality,
            values=AppConstants.RECORDING_QUALITY_OPTIONS,
            state="readonly",
            width=15
        )
        quality_combo.pack(side=tk.LEFT, padx=5)

        # Device selection frame
        device_frame = ttk.LabelFrame(main_frame, text="Device Selection", padding="10")
        device_frame.pack(fill=tk.X, pady=(0, 10))

        # Video device
        video_device_frame = ttk.Frame(device_frame)
        video_device_frame.pack(fill=tk.X, pady=5)
        ttk.Label(video_device_frame, text="Video Source:", width=15).pack(side=tk.LEFT)
        self.video_device_combo = ttk.Combobox(
            video_device_frame,
            textvariable=self.recording_video_device,
            state="readonly",
            width=30
        )
        self.video_device_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(
            video_device_frame,
            text="Refresh Devices",
            command=self.refresh_recording_devices
        ).pack(side=tk.LEFT, padx=5)

        # Audio device
        audio_device_frame = ttk.Frame(device_frame)
        audio_device_frame.pack(fill=tk.X, pady=5)
        ttk.Label(audio_device_frame, text="Audio Source:", width=15).pack(side=tk.LEFT)
        self.audio_device_combo = ttk.Combobox(
            audio_device_frame,
            textvariable=self.recording_audio_device,
            state="readonly",
            width=30
        )
        self.audio_device_combo.pack(side=tk.LEFT, padx=5)

        # Info label for audio setup
        info_frame = ttk.Frame(device_frame)
        info_frame.pack(fill=tk.X, pady=10)
        info_label = ttk.Label(
            info_frame,
            text="⚠️ To record system audio, you need to install BlackHole or similar virtual audio device.\n"
                 "Visit: https://github.com/ExistentialAudio/BlackHole",
            wraplength=600,
            justify=tk.LEFT,
            foreground="blue"
        )
        info_label.pack()
        info_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/ExistentialAudio/BlackHole"))

        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.start_recording_button = ttk.Button(
            button_frame,
            text="🔴 Start Recording",
            command=self.start_recording,
            style="Accent.TButton"
        )
        self.start_recording_button.pack(side=tk.LEFT, padx=5)

        self.stop_recording_button = ttk.Button(
            button_frame,
            text="⏹ Stop Recording",
            command=self.stop_recording,
            state="disabled"
        )
        self.stop_recording_button.pack(side=tk.LEFT, padx=5)

        # Output info
        self.recording_output_label = ttk.Label(
            main_frame,
            text="Output will be saved to Desktop",
            foreground="gray"
        )
        self.recording_output_label.pack(pady=10)

        # Initialize recorder and refresh devices
        self.screen_recorder = ScreenRecorder()
        self.refresh_recording_devices()

    def refresh_recording_devices(self):
        """Refresh available recording devices"""
        try:
            if not self.screen_recorder:
                self.screen_recorder = ScreenRecorder()

            devices = self.screen_recorder.get_available_devices()

            # Update video device combo
            video_devices = ["1: Capture screen 1"]  # Default option
            if devices['video']:
                video_devices = [f"{d['id']}: {d['name']}" for d in devices['video']]
            self.video_device_combo['values'] = video_devices
            if video_devices:
                self.video_device_combo.current(0)

            # Update audio device combo
            audio_devices = ["0: Default Audio"]  # Default option
            if devices['audio']:
                audio_devices = [f"{d['id']}: {d['name']}" for d in devices['audio']]
            self.audio_device_combo['values'] = audio_devices
            if audio_devices:
                self.audio_device_combo.current(0)

            messagebox.showinfo("Success", f"Found {len(video_devices)} video and {len(audio_devices)} audio devices")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh devices: {str(e)}")

    def start_recording(self):
        """Start screen recording"""
        try:
            # Check if ffmpeg is available
            if not ScreenRecorder.check_ffmpeg_available():
                messagebox.showerror(
                    "Error",
                    "ffmpeg is not installed or not found in PATH.\n"
                    "Please install ffmpeg to use screen recording."
                )
                return

            # Get device IDs from combo box selections
            video_device_text = self.recording_video_device.get()
            audio_device_text = self.recording_audio_device.get()

            # Extract device ID (format: "ID: Name")
            video_device = video_device_text.split(":")[0] if video_device_text else "1"
            audio_device = audio_device_text.split(":")[0] if audio_device_text else "0"

            # Get output path
            output_path = ScreenRecorder.get_default_output_path()

            # Create recorder with builder pattern
            success = (ScreenRecorderBuilder()
                      .set_output_path(output_path)
                      .set_video_device(video_device)
                      .set_audio_device(audio_device)
                      .set_framerate(int(self.recording_framerate.get()))
                      .set_quality(self.recording_quality.get())
                      .set_progress_callback(self.update_recording_progress)
                      .start())

            if success:
                self.is_recording = True
                self.recording_status_label.config(text="🔴 Recording...", foreground="red")
                self.start_recording_button.config(state="disabled")
                self.stop_recording_button.config(state="normal")
                self.recording_output_label.config(text=f"Saving to: {output_path}")

                # Start timer
                self.recording_start_time = 0
                self.update_recording_timer()
            else:
                messagebox.showerror("Error", "Failed to start recording")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start recording: {str(e)}")

    def stop_recording(self):
        """Stop screen recording"""
        try:
            if self.screen_recorder:
                success = self.screen_recorder.stop_recording()

                if success:
                    self.is_recording = False
                    self.recording_status_label.config(text="✅ Recording saved", foreground="green")
                    self.start_recording_button.config(state="normal")
                    self.stop_recording_button.config(state="disabled")

                    # Reset timer after a delay
                    self.root.after(2000, lambda: self.recording_status_label.config(
                        text="Ready to record",
                        foreground="black"
                    ))

                    messagebox.showinfo("Success", "Recording saved successfully!")
                else:
                    messagebox.showerror("Error", "Failed to stop recording")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop recording: {str(e)}")

    def update_recording_progress(self, progress_info):
        """Update recording progress display"""
        # This is called from the recording thread
        # Parse ffmpeg progress output if needed
        pass

    def update_recording_timer(self):
        """Update recording timer display"""
        if self.is_recording:
            self.recording_start_time += 1
            hours = self.recording_start_time // 3600
            minutes = (self.recording_start_time % 3600) // 60
            seconds = self.recording_start_time % 60
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.recording_time_label.config(text=time_str)
            # Update every second
            self.root.after(1000, self.update_recording_timer)

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
        ttk.Button(fixed_dir_frame, text="Browse", command=self.browse_fixed_dir, width=10).pack(side=tk.LEFT, ipadx=8, ipady=4)

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

        ttk.Label(instruction_frame, text="Instructions:",
                 font=('Helvetica', 12, 'bold')).pack(anchor=tk.W)

        instructions_text = ("• Apply Settings: Immediately apply settings to Convert and Split tabs\n"
                           "• Reset to Defaults: Reset all settings to factory defaults\n"
                           "• Save Settings: Permanently save settings (persist after restart)")
        ttk.Label(instruction_frame, text=instructions_text,
                 font=('Helvetica', 10), foreground='#555555',
                 justify=tk.LEFT).pack(anchor=tk.W, pady=(5, 0))

        # Buttons frame
        buttons_frame = ttk.Frame(buttons_section)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(buttons_frame, text="Apply Settings",
                  command=self.apply_all_settings).pack(side=tk.LEFT, padx=8, ipadx=15, ipady=8)
        ttk.Button(buttons_frame, text="Reset to Defaults",
                  command=self.reset_to_defaults).pack(side=tk.LEFT, padx=8, ipadx=15, ipady=8)
        ttk.Button(buttons_frame, text="Save Settings",
                  command=self.save_settings).pack(side=tk.LEFT, padx=8, ipadx=15, ipady=8)

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
        ttk.Button(title_frame, text="Clear History", command=self.clear_history).pack(side=tk.RIGHT, ipadx=12, ipady=6)

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

    def add_conversion_history(self, filename, input_format, output_format, success=True, failure_reason=None):
        """Add conversion to history"""
        from datetime import datetime
        entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'filename': filename,
            'input_format': input_format,
            'format': output_format,
            'success': success,
            'failure_reason': failure_reason
        }
        self.conversion_history.append(entry)

        # Add to listbox
        status = "✓" if success else "✗"
        if success:
            display_text = f"{entry['timestamp']} {status} {filename} → {output_format}"
        else:
            # Show failure reason in history
            reason = failure_reason or "Unknown error"
            display_text = f"{entry['timestamp']} {status} {filename} → {output_format} ({reason})"
        self.convert_history_listbox.insert(tk.END, display_text)

        # Auto-scroll to bottom
        self.convert_history_listbox.see(tk.END)

        self.update_statistics()

    def add_split_history(self, filename, mode, value, parts_created, success=True, failure_reason=None):
        """Add split operation to history"""
        from datetime import datetime
        entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'filename': filename,
            'mode': mode,
            'value': value,
            'parts': parts_created,
            'success': success,
            'failure_reason': failure_reason
        }
        self.split_history.append(entry)

        # Add to listbox
        status = "✓" if success else "✗"
        if success:
            display_text = f"{entry['timestamp']} {status} {filename} → {parts_created} parts ({mode}: {value})"
        else:
            reason = failure_reason or "Unknown error"
            display_text = f"{entry['timestamp']} {status} {filename} → FAILED ({reason})"
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
        self.audio_format.set(self.default_format.get())
        self.video_format.set('mp4')  # Default video format
        self.audio_bitrate.set(self.default_bitrate.get())
        self.video_bitrate.set('2M')  # Default video bitrate
        self.sample_rate.set(self.default_sample_rate.get())
        self.normalize.set(self.default_normalize.get())

        # Apply Split settings
        self.split_mode.set(self.default_split_mode.get())
        self.split_duration.set(self.default_split_duration.get())
        self.keep_original.set(self.default_keep_original.get())
        self.update_split_mode()  # Update the display

        # Show confirmation in status instead of popup
        self.convert_status.config(text="✅ Default settings applied")
        self.root.after(2000, lambda: self.convert_status.config(text="Ready"))

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

        # Show confirmation in status instead of popup
        self.convert_status.config(text="✅ Settings reset to defaults")
        self.root.after(2000, lambda: self.convert_status.config(text="Ready"))

    def save_settings(self):
        """Save current settings to file"""
        settings = {
            'convert': {
                'format': self.default_format.get(),
                'video_format': 'mp4',  # Default video format
                'bitrate': self.default_bitrate.get(),
                'video_bitrate': '2M',  # Default video bitrate
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

    def update_progress_bar(self, value):
        """Update the custom progress bar (value: 0-100)"""
        self._progress_value = max(0, min(100, value))

        # Calculate fill height
        fill_height = (self._progress_value / 100) * 400
        fill_top = 400 - fill_height

        # Update the progress fill rectangle
        self.shared_progress.coords(self._progress_fill, 0, fill_top, 38, 400)

    def load_settings(self):
        """Load settings from file"""
        try:
            settings_file = Path.home() / '.audio_converter_settings.json'
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)

                # Apply loaded settings to main variables
                convert_settings = settings.get('convert', {})
                self.audio_format.set(convert_settings.get('format', 'mp3'))
                self.video_format.set(convert_settings.get('video_format', 'mp4'))
                self.audio_bitrate.set(convert_settings.get('bitrate', '192k'))
                self.video_bitrate.set(convert_settings.get('video_bitrate', '2M'))
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
            file_list = self.convert_file_list
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
            file_list = self.convert_file_list
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
            file_list = self.convert_file_list
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
            self.convert_file_list = []
        else:
            self.split_listbox.delete(0, tk.END)
            self.split_files = []

    def convert_files(self):
        """Convert files in the Convert tab"""
        print("=== CONVERT FUNCTION STARTED ===")

        try:
            print(f"Checking self.convert_file_list: {hasattr(self, 'convert_files')}")
            print(f"self.convert_file_list value: {getattr(self, 'convert_files', 'NOT FOUND')}")

            if not self.convert_file_list:
                print("No files in list - showing warning")
                messagebox.showwarning("No Files", "Please add files to convert")
                return


        except Exception as e:
            print(f"ERROR in convert_files start: {e}")
            import traceback
            traceback.print_exc()
            return

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
        total = len(self.convert_file_list)

        for i, file_path in enumerate(self.convert_file_list):
            # Calculate base progress for current file
            base_progress = (i / total) * 100
            file_progress_range = 100 / total

            filename = os.path.basename(file_path)
            self.root.after(0, lambda f=filename: self.convert_status.config(text=f"Converting: {f}"))

            # Create progress callback for current file (fix closure issue)
            def create_progress_callback(base_prog, range_prog):
                def file_progress_callback(file_percent):
                    total_progress = base_prog + (file_percent / 100) * range_prog
                    self.root.after(0, lambda p=total_progress: self.convert_progress.configure(value=p))
                return file_progress_callback

            file_progress_callback = create_progress_callback(base_progress, file_progress_range)

            try:
                # Determine output directory based on settings
                if custom_output_dir:
                    output_dir = custom_output_dir
                else:
                    output_dir = os.path.dirname(file_path)

                # Build output filename based on naming style setting
                base_name = Path(file_path).stem
                naming_style = getattr(self, 'naming_style', None)

                # Determine format and options based on file type and settings
                if self.media_type.get() == "audio" or Path(file_path).suffix.lower() in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma']:
                    # Audio file conversion
                    target_format = self.audio_format.get()
                    options = {
                        'bitrate': self.audio_bitrate.get(),
                        'sample_rate': self.sample_rate.get(),
                        'normalize': self.normalize.get()
                    }
                else:
                    # Video file conversion
                    target_format = self.video_format.get()
                    options = {
                        'video_bitrate': self.video_bitrate.get(),
                        'audio_bitrate': self.audio_bitrate.get(),
                        'normalize': self.normalize.get()
                    }

                # Generate output filename
                if naming_style and naming_style.get() == "suffix":
                    output_filename = f"{base_name}_converted.{target_format}"
                else:
                    # Default: keep original name (but change extension)
                    output_filename = f"{base_name}.{target_format}"

                output_file = os.path.join(output_dir, output_filename)


                processor = MediaProcessorBuilder.create_converter(
                    format=target_format,
                    **options
                )

                output_params = {
                    'output_file': output_file,
                    'output_dir': output_dir,
                    'naming_style': naming_style,
                    'progress_callback': file_progress_callback
                }

                success = processor.process_file(file_path, output_params)
                if not success:
                    raise Exception("Conversion failed")

                # Add to history
                input_ext = Path(file_path).suffix.lower()
                self.add_conversion_history(filename, input_ext, target_format, True)

            except Exception as e:
                error_msg = str(e)
                print(f"Error converting {file_path}: {error_msg}")
                import traceback
                traceback.print_exc()  # Print full error

                # Add failed conversion to history with error details
                input_ext = Path(file_path).suffix.lower()
                failure_reason = f"FAILED: {error_msg[:100]}..."  # Truncate long errors
                # Use target format if available, otherwise use audio format as fallback
                format_for_history = target_format if 'target_format' in locals() else self.audio_format.get()
                self.add_conversion_history(filename, input_ext, format_for_history, False, failure_reason)

        # Check if auto-clear is enabled
        auto_clear = getattr(self, 'auto_clear', None)
        if auto_clear and auto_clear.get():
            # Clear completed files from the list
            self.root.after(0, self._clear_completed_convert_files)

        # Update status and button text instead of popup
        self.root.after(0, lambda: self.convert_status.config(text=f"✅ Converted {total} files successfully!"))
        self.root.after(0, lambda: self.convert_btn.config(text="✅ Conversion Complete!"))

        # Reset button text after 3 seconds
        self.root.after(3000, lambda: self.convert_btn.config(text="🚀 Convert All Files 🚀"))

    def split_files_action(self):
        """Split files in the Split tab"""
        if not self.split_files:
            messagebox.showwarning("No Files", "Please add files to split")
            return

        self.combined_status.config(text="Splitting...")
        self.update_progress_bar(0)
        self.progress_percent.config(text="0%")

        # Start splitting in thread
        thread = threading.Thread(target=self._split_worker)
        thread.daemon = True
        thread.start()

    def _split_worker(self):
        """Worker thread for splitting"""
        total = len(self.split_files)

        for i, file_path in enumerate(self.split_files):
            base_progress = (i / total) * 100
            file_progress_range = 100 / total

            def update_progress(p=base_progress):
                self.update_progress_bar(p)
                self.progress_percent.config(text=f"{int(p)}%")
            self.root.after(0, update_progress)

            filename = os.path.basename(file_path)
            self.root.after(0, lambda f=filename: self.combined_status.config(text=f"Splitting: {f}"))

            try:
                # Create progress callback for individual file processing
                def create_progress_callback(base_prog, range_prog):
                    def file_progress_callback(file_percent):
                        total_progress = base_prog + (file_percent / 100) * range_prog
                        print(f"📊 DEBUG: Split progress callback - file_percent: {file_percent:.1f}%, total_progress: {total_progress:.1f}%")
                        self.root.after(0, lambda p=total_progress: self.update_progress_bar(p))
                        self.root.after(0, lambda p=total_progress: self.progress_percent.config(text=f"{int(p)}%"))
                    return file_progress_callback

                file_progress_callback = create_progress_callback(base_progress, file_progress_range)

                # Use new design pattern for splitting
                if self.split_mode.get() == "duration":
                    processor = MediaProcessorBuilder.create_splitter('duration', duration=int(self.split_duration.get()))
                elif self.split_mode.get() == "size":
                    processor = MediaProcessorBuilder.create_splitter('size', size=int(self.split_size.get()))
                else:  # parts
                    processor = MediaProcessorBuilder.create_splitter('parts', parts=int(self.split_entry.get()))

                output_params = {
                    'keep_original': self.keep_original.get(),
                    'progress_callback': file_progress_callback
                }
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

        # Update status and button text instead of popup
        self.root.after(0, lambda: self.combined_status.config(text=f"✅ Split {total} files successfully!"))
        self.root.after(0, lambda: self.split_btn.config(text="✅ Split Complete!"))

        # Reset button text after 3 seconds
        self.root.after(3000, lambda: self.split_btn.config(text="✂️ Split Selected Files"))

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
        self.convert_file_list.clear()
        self.convert_listbox.delete(0, tk.END)

    def _clear_completed_split_files(self):
        """Clear all files from split list after successful processing"""
        self.split_files.clear()
        self.split_listbox.delete(0, tk.END)

    # YouTube download methods
    def _handle_age_verification(self, url):
        """Handle age verification by opening browser and retrying"""
        result = messagebox.askyesno(
            "需要年齡驗證",
            "這個影片需要年齡驗證。\n\n要打開瀏覽器讓您登入 YouTube 嗎？\n登入後點擊「是」重新下載。",
            icon='question'
        )

        if result:
            # Open YouTube in browser
            webbrowser.open(url)

            # Ask user to confirm after login
            retry = messagebox.askyesno(
                "重新嘗試下載",
                "請在瀏覽器中登入 YouTube 並確認年齡。\n\n登入完成後，點擊「是」重新下載影片。",
                icon='question'
            )

            return retry
        return False

    def _init_youtube_downloader(self):
        """Initialize YouTube downloader with current settings"""
        if self.youtube_downloader:
            self.youtube_downloader.cleanup()
        self.youtube_downloader = YouTubeDownloader(max_workers=self.max_downloads.get())

    def show_format_selection_dialog(self, url):
        """Show format selection dialog for YouTube video"""
        try:
            self.combined_status.config(text="正在獲取格式資訊...", foreground="#2E8B57")
            self.root.update()

            # Get available formats
            self._init_youtube_downloader()
            formats = self.youtube_downloader.get_available_formats(url)

            if not formats:
                self.combined_status.config(text="無法獲取影片格式", foreground="#DC143C")
                return None

            # Create format selection dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("選擇下載格式")
            dialog.geometry("500x400")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()

            # Center the dialog
            dialog.geometry("+%d+%d" % (
                self.root.winfo_rootx() + 50,
                self.root.winfo_rooty() + 50
            ))

            selected_format = None

            # Header frame
            header_frame = tk.Frame(dialog)
            header_frame.pack(fill=tk.X, padx=10, pady=10)

            title_label = tk.Label(header_frame, text="選擇畫質和格式", font=("Arial", 14, "bold"))
            title_label.pack()

            info_label = tk.Label(header_frame, text="請選擇您要下載的格式", font=("Arial", 10))
            info_label.pack()

            # Format list frame
            list_frame = tk.Frame(dialog)
            list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            # Create listbox with scrollbar
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            format_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 10))
            format_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=format_listbox.yview)

            # Populate format list
            format_data = []
            for i, fmt in enumerate(formats):
                size_str = f"{fmt['size_mb']:.1f}MB" if fmt['size_mb'] else "Unknown"
                display_text = f"{fmt['label']:<25} | {size_str:>10}"

                # Add type indicator
                if fmt['type'] == 'audio':
                    display_text += " | 🎵 Audio"
                elif fmt['type'] == 'separate':
                    display_text += " | 🎬 Best Quality"
                else:
                    display_text += " | 📺 Video"

                format_listbox.insert(tk.END, display_text)
                format_data.append(fmt)

            # Select first format by default
            if format_data:
                format_listbox.selection_set(0)

            # Button frame
            button_frame = tk.Frame(dialog)
            button_frame.pack(fill=tk.X, padx=10, pady=10)

            def on_download():
                selection = format_listbox.curselection()
                if selection:
                    nonlocal selected_format
                    selected_format = format_data[selection[0]]
                    dialog.destroy()

            def on_cancel():
                dialog.destroy()

            # Buttons
            download_btn = tk.Button(button_frame, text="下載", command=on_download,
                                   bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                                   relief=tk.RAISED, bd=2, padx=20)
            download_btn.pack(side=tk.RIGHT, padx=5)

            cancel_btn = tk.Button(button_frame, text="取消", command=on_cancel,
                                 bg="#f44336", fg="white", font=("Arial", 12),
                                 relief=tk.RAISED, bd=2, padx=20)
            cancel_btn.pack(side=tk.RIGHT, padx=5)

            # Handle double-click on listbox
            def on_double_click(event):
                on_download()

            format_listbox.bind("<Double-Button-1>", on_double_click)

            # Wait for dialog to close
            self.root.wait_window(dialog)

            return selected_format

        except Exception as e:
            self.combined_status.config(text=f"格式獲取失敗: {str(e)}", foreground="#DC143C")
            return None

    def download_youtube_unified(self):
        """Unified YouTube download based on selected mode"""
        url = self.youtube_url.get().strip()
        if not url:
            self.combined_status.config(text="Please enter a YouTube URL", foreground="#DC143C")
            return

        # Show format selection dialog
        selected_format = self.show_format_selection_dialog(url)
        if not selected_format:
            self.combined_status.config(text="下載已取消", foreground="#FF8C00")
            return

        mode = self.youtube_mode.get()

        if "Download & Split" in mode:
            self.download_and_split_youtube_with_format(selected_format)
        elif "Audio Only" in mode:
            self.download_youtube_audio_with_format(selected_format)
        elif "Playlist" in mode:
            self.download_youtube_playlist()
        else:  # Default to "Download"
            self.download_youtube_only_with_format(selected_format)

    def download_youtube_only(self):
        """Download YouTube video without splitting"""
        url = self.youtube_url.get().strip()
        if not url:
            self.combined_status.config(text="Please enter a YouTube URL", foreground="#DC143C")
            return

        # Select directory first (in main thread to avoid UI blocking)
        output_path = filedialog.askdirectory(title="Select Download Directory")
        if not output_path:
            self.combined_status.config(text="Download cancelled", foreground="#FF8C00")
            return

        self._init_youtube_downloader()
        self.combined_status.config(text="Downloading...", foreground="#2E8B57")
        self.update_progress_bar(0)
        self.progress_percent.config(text="0%")

        def download_thread():
            try:

                def progress_callback(progress):
                    def update_progress_yt(p=progress):
                        self.update_progress_bar(p)
                        self.progress_percent.config(text=f"{int(p)}%")
                        self.combined_status.config(
                            text=f"Downloading... {p:.1f}%", foreground="#2E8B57")
                    self.root.after(0, update_progress_yt)

                success, result = self.youtube_downloader.download_video(
                    url, output_path, self.youtube_format.get(), self.youtube_quality.get(), progress_callback)

                if success:
                    self.root.after(0, lambda: self.combined_status.config(
                        text=f"✅ Downloaded: {os.path.basename(result)}", foreground="#228B22"))
                    # Add to split list
                    self.split_files.append(result)
                    self.update_split_listbox()
                else:
                    self.root.after(0, lambda: self.combined_status.config(
                        text=f"❌ Error: {result}", foreground="#DC143C"))

            except Exception as e:
                self.root.after(0, lambda: self.combined_status.config(
                    text=f"❌ Error: {str(e)}", foreground="#DC143C"))

        threading.Thread(target=download_thread, daemon=True).start()

    def download_youtube_only_with_format(self, selected_format):
        """Download YouTube video with specific format without splitting"""
        url = self.youtube_url.get().strip()

        # Select directory first (in main thread to avoid UI blocking)
        output_path = filedialog.askdirectory(title="Select Download Directory")
        if not output_path:
            self.combined_status.config(text="下載已取消", foreground="#FF8C00")
            return

        self._init_youtube_downloader()
        self.combined_status.config(text="下載中...", foreground="#2E8B57")
        self.update_progress_bar(0)
        self.progress_percent.config(text="0%")

        def download_thread():
            try:
                def progress_callback(progress):
                    def update_progress_yt(p=progress):
                        self.update_progress_bar(p)
                        self.progress_percent.config(text=f"{int(p)}%")
                        self.combined_status.config(
                            text=f"下載中... {p:.1f}%", foreground="#2E8B57")
                    self.root.after(0, update_progress_yt)

                success, result = self.youtube_downloader.download_video_with_format(
                    url, output_path, selected_format['format_id'], selected_format['ext'], progress_callback)

                if success:
                    self.root.after(0, lambda: self.combined_status.config(
                        text=f"✅ 下載完成: {os.path.basename(result)}", foreground="#228B22"))
                    # Add to split list
                    self.split_files.append(result)
                    self.update_split_listbox()
                else:
                    self.root.after(0, lambda: self.combined_status.config(
                        text=f"❌ 下載失敗: {result}", foreground="#DC143C"))

            except Exception as e:
                self.root.after(0, lambda: self.combined_status.config(
                    text=f"❌ 錯誤: {str(e)}", foreground="#DC143C"))

        threading.Thread(target=download_thread, daemon=True).start()

    def download_youtube_audio_with_format(self, selected_format):
        """Download YouTube audio with specific format"""
        url = self.youtube_url.get().strip()

        # Select directory first (in main thread to avoid UI blocking)
        output_path = filedialog.askdirectory(title="Select Download Directory")
        if not output_path:
            self.combined_status.config(text="下載已取消", foreground="#FF8C00")
            return

        self._init_youtube_downloader()
        self.combined_status.config(text="下載音頻中...", foreground="#2E8B57")
        self.update_progress_bar(0)
        self.progress_percent.config(text="0%")

        def download_thread():
            try:
                def progress_callback(progress):
                    def update_progress_yt(p=progress):
                        self.update_progress_bar(p)
                        self.progress_percent.config(text=f"{int(p)}%")
                        self.combined_status.config(
                            text=f"下載音頻中... {p:.1f}%", foreground="#2E8B57")
                    self.root.after(0, update_progress_yt)

                success, result = self.youtube_downloader.download_video_with_format(
                    url, output_path, selected_format['format_id'], selected_format['ext'], progress_callback)

                if success:
                    self.root.after(0, lambda: self.combined_status.config(
                        text=f"✅ 音頻下載完成: {os.path.basename(result)}", foreground="#228B22"))
                    # Add to split list
                    self.split_files.append(result)
                    self.update_split_listbox()
                else:
                    self.root.after(0, lambda: self.combined_status.config(
                        text=f"❌ 音頻下載失敗: {result}", foreground="#DC143C"))

            except Exception as e:
                self.root.after(0, lambda: self.combined_status.config(
                    text=f"❌ 錯誤: {str(e)}", foreground="#DC143C"))

        threading.Thread(target=download_thread, daemon=True).start()

    def download_and_split_youtube_with_format(self, selected_format):
        """Download YouTube video with specific format and split it"""
        url = self.youtube_url.get().strip()

        # Select directory first (in main thread to avoid UI blocking)
        output_path = filedialog.askdirectory(title="Select Download Directory")
        if not output_path:
            self.combined_status.config(text="下載已取消", foreground="#FF8C00")
            return

        self._init_youtube_downloader()
        self.combined_status.config(text="下載並分割中...", foreground="#2E8B57")

        def download_split_thread():
            try:
                # Get split settings from UI
                split_mode = self.split_mode.get()
                split_value = None

                if split_mode == "duration":
                    try:
                        split_value = int(self.split_duration.get())
                    except ValueError:
                        split_value = 300  # Default 5 minutes
                elif split_mode == "size":
                    try:
                        split_value = int(self.split_size.get())
                    except ValueError:
                        split_value = 100  # Default 100MB
                elif split_mode == "parts":
                    try:
                        split_value = int(self.split_parts.get())
                    except ValueError:
                        split_value = 3  # Default 3 parts

                def progress_callback(progress):
                    def update_progress_yt(p=progress):
                        self.update_progress_bar(p)
                        self.progress_percent.config(text=f"{int(p)}%")
                        self.combined_status.config(
                            text=f"下載並分割中... {p:.1f}%", foreground="#2E8B57")
                    self.root.after(0, update_progress_yt)

                # First download with specific format
                success, result = self.youtube_downloader.download_video_with_format(
                    url, output_path, selected_format['format_id'], selected_format['ext'], progress_callback)

                if success:
                    # Then split the downloaded file
                    self.root.after(0, lambda: self.combined_status.config(
                        text="分割檔案中...", foreground="#2E8B57"))

                    # Use existing split functionality
                    success_split, split_results = self.youtube_downloader.download_and_split_extended(
                        url, output_path, split_mode, split_value,
                        selected_format['ext'], selected_format['format_id'], None)

                    if success_split:
                        self.root.after(0, lambda: self.combined_status.config(
                            text=f"✅ 下載並分割完成: {len(split_results)} 個檔案", foreground="#228B22"))
                        # Add all split files to list
                        for split_file in split_results:
                            if split_file not in self.split_files:
                                self.split_files.append(split_file)
                        self.update_split_listbox()
                    else:
                        self.root.after(0, lambda: self.combined_status.config(
                            text=f"❌ 分割失敗: {split_results[0] if split_results else 'Unknown error'}", foreground="#DC143C"))
                else:
                    self.root.after(0, lambda: self.combined_status.config(
                        text=f"❌ 下載失敗: {result}", foreground="#DC143C"))

            except Exception as e:
                self.root.after(0, lambda: self.combined_status.config(
                    text=f"❌ 錯誤: {str(e)}", foreground="#DC143C"))

        threading.Thread(target=download_split_thread, daemon=True).start()

    def download_and_split_youtube(self):
        """Download YouTube video and split it"""
        url = self.youtube_url.get().strip()
        if not url:
            self.combined_status.config(text="Please enter a YouTube URL", foreground="#DC143C")
            return

        # Select directory first (in main thread to avoid UI blocking)
        output_path = filedialog.askdirectory(title="Select Download Directory")
        if not output_path:
            self.combined_status.config(text="Download cancelled", foreground="#FF8C00")
            return

        self._init_youtube_downloader()
        self.combined_status.config(text="Downloading and splitting...", foreground="#2E8B57")

        def download_split_thread():
            try:

                # Get split settings from UI
                split_mode = self.split_mode.get()
                split_value = None

                if split_mode == "duration":
                    try:
                        split_value = int(self.split_duration.get())
                    except ValueError:
                        split_value = 300  # Default 5 minutes
                elif split_mode == "size":
                    try:
                        split_value = int(self.split_size.get())  # MB
                    except ValueError:
                        split_value = 100  # Default 100MB
                else:  # parts
                    try:
                        split_value = int(self.split_parts.get())
                    except (ValueError, AttributeError):
                        split_value = 3  # Default 3 parts

                def progress_callback(progress):
                    def update_progress_split(p=progress):
                        self.update_progress_bar(p)
                        self.progress_percent.config(text=f"{int(p)}%")
                        self.combined_status.config(
                            text=f"Processing... {p:.1f}%", foreground="#2E8B57")
                    self.root.after(0, update_progress_split)

                success, result = self.youtube_downloader.download_and_split_extended(
                    url, output_path, split_mode, split_value, self.youtube_format.get(),
                    self.youtube_quality.get(), progress_callback)

                if success:
                    self.root.after(0, lambda: self.combined_status.config(
                        text=f"✅ Created {len(result)} segments", foreground="#228B22"))
                    # Add all segments to split list
                    self.split_files.extend(result)
                    self.update_split_listbox()
                else:
                    self.root.after(0, lambda: self.combined_status.config(
                        text=f"❌ Error: {result[0] if result else 'Unknown error'}", foreground="#DC143C"))

            except Exception as e:
                self.root.after(0, lambda: self.combined_status.config(
                    text=f"❌ Error: {str(e)}", foreground="#DC143C"))

        threading.Thread(target=download_split_thread, daemon=True).start()

    def download_youtube_audio(self):
        """Download YouTube video as audio only"""
        url = self.youtube_url.get().strip()
        if not url:
            self.combined_status.config(text="Please enter a YouTube URL", foreground="#DC143C")
            return

        # Select directory first (in main thread to avoid UI blocking)
        output_path = filedialog.askdirectory(title="Select Download Directory")
        if not output_path:
            self.combined_status.config(text="Download cancelled", foreground="#FF8C00")
            return

        self._init_youtube_downloader()
        self.combined_status.config(text="Downloading audio...", foreground="#2E8B57")
        self.update_progress_bar(0)
        self.progress_percent.config(text="0%")

        def download_audio_thread():
            try:
                def progress_callback(progress):
                    def update_progress_audio(p=progress):
                        self.update_progress_bar(p)
                        self.progress_percent.config(text=f"{int(p)}%")
                        self.combined_status.config(
                            text=f"Downloading audio... {p:.1f}%", foreground="#2E8B57")
                    self.root.after(0, update_progress_audio)

                success, result = self.youtube_downloader.download_video(
                    url, output_path, 'm4a', 'audio', progress_callback)

                if success:
                    self.root.after(0, lambda: self.combined_status.config(
                        text=f"✅ Audio downloaded: {os.path.basename(result)}", foreground="#228B22"))
                    # Add to split list
                    self.split_files.append(result)
                    self.update_split_listbox()
                else:
                    self.root.after(0, lambda: self.combined_status.config(
                        text=f"❌ Error: {result}", foreground="#DC143C"))

            except Exception as e:
                self.root.after(0, lambda: self.combined_status.config(
                    text=f"❌ Error: {str(e)}", foreground="#DC143C"))

        threading.Thread(target=download_audio_thread, daemon=True).start()

    def download_youtube_playlist(self):
        """Download entire YouTube playlist"""
        url = self.youtube_url.get().strip()
        if not url:
            self.combined_status.config(text="Please enter a YouTube playlist URL", foreground="#DC143C")
            return

        self._init_youtube_downloader()
        self.combined_status.config(text="Downloading playlist...", foreground="#2E8B57")

        def download_playlist_thread():
            try:
                output_path = filedialog.askdirectory(title="Select Download Directory")
                if not output_path:
                    self.combined_status.config(text="Download cancelled", foreground="#FF8C00")
                    return

                def progress_callback(progress):
                    self.root.after(0, lambda: self.combined_status.config(
                        text=f"Downloading playlist... {progress:.1f}%", foreground="#2E8B57"))

                results = self.youtube_downloader.download_playlist(
                    url, output_path, self.youtube_format.get(), self.youtube_quality.get(), progress_callback)

                successful_downloads = [r for r in results if r[1]]
                failed_downloads = [r for r in results if not r[1]]

                if successful_downloads:
                    # Add all successful downloads to split list
                    for title, success, file_path in successful_downloads:
                        if success and os.path.exists(file_path):
                            self.split_files.append(file_path)

                    self.update_split_listbox()
                    self.root.after(0, lambda: self.combined_status.config(
                        text=f"✅ Downloaded {len(successful_downloads)} videos" +
                        (f", {len(failed_downloads)} failed" if failed_downloads else ""),
                        foreground="#228B22"))
                else:
                    self.root.after(0, lambda: self.combined_status.config(
                        text="❌ No videos downloaded successfully", foreground="#DC143C"))

            except Exception as e:
                self.root.after(0, lambda: self.combined_status.config(
                    text=f"❌ Error: {str(e)}", foreground="#DC143C"))

        threading.Thread(target=download_playlist_thread, daemon=True).start()

    def update_split_listbox(self):
        """Update the split files listbox"""
        self.split_listbox.delete(0, tk.END)
        for file in self.split_files:
            filename = os.path.basename(file)
            self.split_listbox.insert(tk.END, filename)

if __name__ == "__main__":
    root = tk.Tk()
    app = TabbedMediaConverter(root)
    root.mainloop()