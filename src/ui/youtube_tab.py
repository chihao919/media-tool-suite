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
        self.progress.pack(fill=tk.X, pady=5)

        self.status = ttk.Label(youtube_frame, text="Ready")
        self.status.pack()

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

    def download_youtube(self):
        """Start YouTube download"""
        self.app.download_youtube_unified()
