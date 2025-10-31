"""YouTube Tab UI Component"""

import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab


class YouTubeTab(BaseTab):
    """UI for YouTube video downloading"""

    def setup_ui(self):
        """Setup the YouTube tab UI"""
        # YouTube download section
        youtube_frame = ttk.LabelFrame(self.main_frame, text="YouTube Download", padding="10")
        youtube_frame.pack(fill=tk.BOTH, expand=True)

        # URL input
        self._create_url_input(youtube_frame)

        # Download options
        self._create_download_options(youtube_frame)

        # Download button
        self.download_btn = ttk.Button(
            youtube_frame,
            text="🔽 DOWNLOAD",
            command=self.download_youtube,
            style="Accent.TButton"
        )
        self.download_btn.pack(pady=15, ipadx=30, ipady=15)

        # Progress and status
        self.progress = ttk.Progressbar(youtube_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5, padx=20)

        self.status = ttk.Label(youtube_frame, text="Ready")
        self.status.pack(pady=5)

    def _create_url_input(self, parent):
        """Create URL input section"""
        url_frame = ttk.Frame(parent)
        url_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(url_frame, text="YouTube URL:").pack(side=tk.LEFT, padx=(0, 10))

        url_entry = ttk.Entry(url_frame, textvariable=self.app.youtube_url, width=50)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

    def _create_download_options(self, parent):
        """Create download options section"""
        options_frame = ttk.LabelFrame(parent, text="Download Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))

        # Mode selection
        mode_frame = ttk.Frame(options_frame)
        mode_frame.pack(fill=tk.X, pady=5)

        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            mode_frame,
            text="Download",
            value="Download",
            variable=self.app.youtube_mode
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            mode_frame,
            text="Download & Split",
            value="Download & Split",
            variable=self.app.youtube_mode
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            mode_frame,
            text="Audio Only",
            value="Audio Only",
            variable=self.app.youtube_mode
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            mode_frame,
            text="Playlist",
            value="Playlist",
            variable=self.app.youtube_mode
        ).pack(side=tk.LEFT, padx=5)

        # Format and quality
        quality_frame = ttk.Frame(options_frame)
        quality_frame.pack(fill=tk.X, pady=5)

        ttk.Label(quality_frame, text="Format:").pack(side=tk.LEFT, padx=(0, 5))
        format_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.app.youtube_format,
            values=["mp4", "webm", "mkv", "flv", "avi"],
            state="readonly",
            width=8
        )
        format_combo.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(quality_frame, text="Quality:").pack(side=tk.LEFT, padx=(0, 5))
        quality_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.app.youtube_quality,
            values=["best", "1080p", "720p", "480p", "360p", "audio"],
            state="readonly",
            width=10
        )
        quality_combo.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(quality_frame, text="Max Downloads:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Spinbox(
            quality_frame,
            from_=1,
            to=10,
            textvariable=self.app.max_downloads,
            width=5
        ).pack(side=tk.LEFT)

        # Split settings (shown when Download & Split mode is selected)
        self._create_split_settings(options_frame)

    def _create_split_settings(self, parent):
        """Create split settings section"""
        self.split_settings_frame = ttk.LabelFrame(parent, text="Split Settings (for Download & Split mode)", padding="10")
        self.split_settings_frame.pack(fill=tk.X, pady=10)

        # Split mode selection
        mode_frame = ttk.Frame(self.split_settings_frame)
        mode_frame.pack(fill=tk.X, pady=5)

        ttk.Label(mode_frame, text="Split by:").pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            mode_frame,
            text="Duration (seconds)",
            value="duration",
            variable=self.app.split_mode
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            mode_frame,
            text="File Size (MB)",
            value="size",
            variable=self.app.split_mode
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            mode_frame,
            text="Number of Parts",
            value="parts",
            variable=self.app.split_mode
        ).pack(side=tk.LEFT, padx=5)

        # Split value input
        value_frame = ttk.Frame(self.split_settings_frame)
        value_frame.pack(fill=tk.X, pady=5)

        self.split_label = ttk.Label(value_frame, text="Duration (seconds):")
        self.split_label.pack(side=tk.LEFT, padx=(0, 10))

        self.split_entry = ttk.Entry(value_frame, textvariable=self.app.split_duration, width=15)
        self.split_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.split_unit = ttk.Label(value_frame, text="(5 minutes = 300)", foreground="gray")
        self.split_unit.pack(side=tk.LEFT)

        # Update UI when mode changes
        self.app.split_mode.trace_add('write', lambda *args: self._update_split_ui())

    def _update_split_ui(self):
        """Update split UI based on selected mode"""
        mode = self.app.split_mode.get()
        if mode == "duration":
            self.split_label.config(text="Duration (seconds):")
            self.split_entry.config(textvariable=self.app.split_duration)
            self.split_unit.config(text="(5 minutes = 300)")
        elif mode == "size":
            self.split_label.config(text="File size (MB):")
            self.split_entry.config(textvariable=self.app.split_size)
            self.split_unit.config(text="(1 GB = 1024 MB)")
        elif mode == "parts":
            self.split_label.config(text="Number of parts:")
            self.split_entry.config(textvariable=self.app.split_parts)
            self.split_unit.config(text="(2-10 parts)")

    def download_youtube(self):
        """Start YouTube download"""
        self.app.download_youtube_unified()
