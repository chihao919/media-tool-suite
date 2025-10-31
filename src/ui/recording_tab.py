"""Screen Recording Tab UI Component"""

import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab


class RecordingTab(BaseTab):
    """UI for screen recording"""

    def setup_ui(self):
        """Setup the Recording tab UI"""
        # Recording status
        self._create_status_section()

        # Settings
        self._create_settings_section()

        # Control buttons
        self._create_control_buttons()

        # Output info
        self._create_output_section()

    def _create_status_section(self):
        """Create recording status section"""
        status_frame = ttk.LabelFrame(self.main_frame, text="Recording Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = ttk.Label(
            status_frame,
            text="Ready to record",
            font=('Helvetica', 12, 'bold')
        )
        self.status_label.pack()

        self.time_label = ttk.Label(status_frame, text="00:00:00")
        self.time_label.pack()

    def _create_settings_section(self):
        """Create recording settings section"""
        settings_frame = ttk.LabelFrame(self.main_frame, text="Recording Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Framerate
        framerate_frame = ttk.Frame(settings_frame)
        framerate_frame.pack(fill=tk.X, pady=5)
        ttk.Label(framerate_frame, text="Framerate:", width=15).pack(side=tk.LEFT)
        ttk.Combobox(
            framerate_frame,
            textvariable=self.app.recording_framerate,
            values=["15", "24", "30", "60"],
            state="readonly",
            width=10
        ).pack(side=tk.LEFT)

        # Quality
        quality_frame = ttk.Frame(settings_frame)
        quality_frame.pack(fill=tk.X, pady=5)
        ttk.Label(quality_frame, text="Quality:", width=15).pack(side=tk.LEFT)
        ttk.Combobox(
            quality_frame,
            textvariable=self.app.recording_quality,
            values=["low", "medium", "high", "ultra"],
            state="readonly",
            width=10
        ).pack(side=tk.LEFT)

        # Video device
        video_frame = ttk.Frame(settings_frame)
        video_frame.pack(fill=tk.X, pady=5)
        ttk.Label(video_frame, text="Video Device:", width=15).pack(side=tk.LEFT)
        self.video_device_combo = ttk.Combobox(
            video_frame,
            textvariable=self.app.recording_video_device,
            state="readonly",
            width=30
        )
        self.video_device_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Audio device
        audio_frame = ttk.Frame(settings_frame)
        audio_frame.pack(fill=tk.X, pady=5)
        ttk.Label(audio_frame, text="Audio Device:", width=15).pack(side=tk.LEFT)
        self.audio_device_combo = ttk.Combobox(
            audio_frame,
            textvariable=self.app.recording_audio_device,
            state="readonly",
            width=30
        )
        self.audio_device_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Refresh button
        ttk.Button(
            settings_frame,
            text="🔄 Refresh Devices",
            command=lambda: self.app.refresh_recording_devices(show_message=True)
        ).pack(pady=10)

    def _create_control_buttons(self):
        """Create control buttons"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.start_btn = ttk.Button(
            button_frame,
            text="🔴 Start Recording",
            command=self.start_recording,
            style="Accent.TButton"
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹ Stop Recording",
            command=self.stop_recording,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

    def _create_output_section(self):
        """Create output info section"""
        output_frame = ttk.LabelFrame(self.main_frame, text="Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True)

        self.output_label = ttk.Label(
            output_frame,
            text="Output will be saved to: ~/Downloads/",
            wraplength=400
        )
        self.output_label.pack(pady=10)

    def start_recording(self):
        """Start recording"""
        self.app.start_recording()

    def stop_recording(self):
        """Stop recording"""
        self.app.stop_recording()
