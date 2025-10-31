"""Convert Tab UI Component"""

import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab
from app_constants import AppConstants


class ConvertTab(BaseTab):
    """UI for media file conversion"""

    def setup_ui(self):
        """Setup the Convert tab UI"""
        # Create file list section
        self.create_file_list_section(
            title="Media Files to Convert",
            listbox_var_name="listbox",
            add_command=self.add_files,
            remove_command=self.remove_selected,
            clear_command=self.clear_files,
            add_folder_command=self.add_folder
        )

        # Settings frame
        settings_frame = ttk.Frame(self.main_frame)
        settings_frame.pack(fill=tk.X, pady=10)

        # Left side - Media Type Selection
        self._create_media_type_selector(settings_frame)

        # Middle - Format settings
        self._create_format_settings(settings_frame)

        # Right side - Options
        self._create_options(settings_frame)

        # Convert button
        self.convert_btn = ttk.Button(
            self.main_frame,
            text="🚀 Convert All Files 🚀",
            command=self.convert_files
        )
        self.convert_btn.pack(pady=15, ipadx=30, ipady=15)

        # Progress and status
        self.create_progress_section(
            progress_var_name='progress',
            status_var_name='status'
        )

    def _create_media_type_selector(self, parent):
        """Create media type selection frame"""
        type_frame = ttk.LabelFrame(parent, text="Media Type", padding="10")
        type_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        ttk.Radiobutton(
            type_frame,
            text="Auto Detect",
            variable=self.app.media_type,
            value="auto",
            command=self.update_format_ui
        ).pack(anchor=tk.W)

        ttk.Radiobutton(
            type_frame,
            text="Audio",
            variable=self.app.media_type,
            value="audio",
            command=self.update_format_ui
        ).pack(anchor=tk.W)

        ttk.Radiobutton(
            type_frame,
            text="Video",
            variable=self.app.media_type,
            value="video",
            command=self.update_format_ui
        ).pack(anchor=tk.W)

    def _create_format_settings(self, parent):
        """Create format settings frame"""
        self.format_frame = ttk.LabelFrame(parent, text="Format Settings", padding="10")
        self.format_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Configure column weights
        self.format_frame.columnconfigure(0, weight=0, minsize=120)
        self.format_frame.columnconfigure(1, weight=1, minsize=120)

        # Create audio format widgets
        self.audio_widgets = {}
        self.audio_widgets['format_label'] = ttk.Label(self.format_frame, text="Audio Format:")
        self.audio_widgets['format_combo'] = ttk.Combobox(
            self.format_frame,
            textvariable=self.app.audio_format,
            values=AppConstants.AUDIO_FORMAT_OPTIONS,
            state="readonly",
            width=15
        )
        self.audio_widgets['bitrate_label'] = ttk.Label(self.format_frame, text="Audio Bitrate:")
        self.audio_widgets['bitrate_combo'] = ttk.Combobox(
            self.format_frame,
            textvariable=self.app.audio_bitrate,
            values=["128k", "192k", "256k", "320k"],
            state="readonly",
            width=15
        )
        self.audio_widgets['sample_label'] = ttk.Label(self.format_frame, text="Sample Rate:")
        self.audio_widgets['sample_combo'] = ttk.Combobox(
            self.format_frame,
            textvariable=self.app.sample_rate,
            values=["44100", "48000", "96000"],
            state="readonly",
            width=15
        )

        # Create video format widgets
        self.video_widgets = {}
        self.video_widgets['format_label'] = ttk.Label(self.format_frame, text="Video Format:")
        self.video_widgets['format_combo'] = ttk.Combobox(
            self.format_frame,
            textvariable=self.app.video_format,
            values=AppConstants.VIDEO_FORMAT_OPTIONS,
            state="readonly",
            width=15
        )
        self.video_widgets['bitrate_label'] = ttk.Label(self.format_frame, text="Video Bitrate:")
        self.video_widgets['bitrate_combo'] = ttk.Combobox(
            self.format_frame,
            textvariable=self.app.video_bitrate,
            values=["1M", "2M", "5M", "10M", "20M"],
            state="readonly",
            width=15
        )
        self.video_widgets['audio_bitrate_label'] = ttk.Label(self.format_frame, text="Audio Bitrate:")
        self.video_widgets['audio_bitrate_combo'] = ttk.Combobox(
            self.format_frame,
            textvariable=self.app.audio_bitrate,
            values=["128k", "192k", "256k", "320k"],
            state="readonly",
            width=15
        )

        # Create auto mode labels
        self.auto_labels = {}
        self.auto_labels['audio_format'] = ttk.Label(
            self.format_frame,
            text="Audio Format:",
            font=('Helvetica', 10, 'bold')
        )
        self.auto_labels['video_format'] = ttk.Label(
            self.format_frame,
            text="Video Format:",
            font=('Helvetica', 10, 'bold')
        )
        self.auto_labels['quality'] = ttk.Label(
            self.format_frame,
            text="Quality:",
            font=('Helvetica', 10, 'italic')
        )

        # Initialize UI
        self.update_format_ui()

    def _create_options(self, parent):
        """Create options frame"""
        options_frame = ttk.LabelFrame(parent, text="Options", padding="10")
        options_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Checkbutton(
            options_frame,
            text="Normalize Audio (-16 LUFS)",
            variable=self.app.normalize
        ).pack(anchor=tk.W, pady=5)

        ttk.Label(
            options_frame,
            text="Output: Same folder as source",
            font=('Helvetica', 10, 'italic')
        ).pack(anchor=tk.W, pady=5)

    def update_format_ui(self):
        """Update format UI based on selected media type"""
        # Hide all widgets first
        for widget_dict in [self.audio_widgets, self.video_widgets]:
            for widget in widget_dict.values():
                widget.grid_remove()

        # Hide auto mode labels
        for label in self.auto_labels.values():
            label.grid_remove()

        media_type = self.app.media_type.get()

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
            # Show both formats
            row = 0
            self.auto_labels['audio_format'].grid(row=row, column=0, sticky=tk.W, pady=2)
            self.audio_widgets['format_combo'].grid(row=row, column=1, padx=5, pady=2)
            row += 1
            self.auto_labels['video_format'].grid(row=row, column=0, sticky=tk.W, pady=2)
            self.video_widgets['format_combo'].grid(row=row, column=1, padx=5, pady=2)
            row += 1
            self.auto_labels['quality'].grid(row=row, column=0, sticky=tk.W, pady=(10, 2))
            row += 1
            self.audio_widgets['bitrate_label'].grid(row=row, column=0, sticky=tk.W, pady=2)
            self.audio_widgets['bitrate_combo'].grid(row=row, column=1, padx=5, pady=2)
            row += 1
            self.video_widgets['bitrate_label'].grid(row=row, column=0, sticky=tk.W, pady=2)
            self.video_widgets['bitrate_combo'].grid(row=row, column=1, padx=5, pady=2)

    # Delegate methods to app context
    def add_files(self):
        """Add files to convert"""
        self.app.add_files('convert')

    def add_folder(self):
        """Add folder of files"""
        self.app.add_folder('convert')

    def remove_selected(self):
        """Remove selected files"""
        self.app.remove_selected('convert')

    def clear_files(self):
        """Clear all files"""
        self.app.clear_files('convert')

    def convert_files(self):
        """Start conversion process"""
        self.app.convert_files()
