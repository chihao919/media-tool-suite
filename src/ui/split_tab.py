"""Split Tab UI Component"""

import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab


class SplitTab(BaseTab):
    """UI for media file splitting"""

    def setup_ui(self):
        """Setup the Split tab UI"""
        # File list section
        list_frame = ttk.LabelFrame(self.main_frame, text="Media Files to Split", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Split button at top
        split_btn_frame = ttk.Frame(list_frame)
        split_btn_frame.pack(fill=tk.X, pady=(0, 10))

        self.split_btn = ttk.Button(
            split_btn_frame,
            text="✂️ Split Selected Files",
            command=self.split_files
        )
        self.split_btn.pack(side=tk.LEFT, padx=5, ipadx=40, ipady=15)

        # Listbox with scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(list_frame, height=8, yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # File buttons - Two rows
        btn_frame_row1 = ttk.Frame(list_frame)
        btn_frame_row1.pack(fill=tk.X, pady=(5, 2))

        ttk.Button(
            btn_frame_row1,
            text="Add Files",
            command=self.add_files
        ).pack(side=tk.LEFT, padx=5, ipadx=20, ipady=10)

        ttk.Button(
            btn_frame_row1,
            text="Add Folder",
            command=self.add_large_files
        ).pack(side=tk.LEFT, padx=5, ipadx=20, ipady=10)

        # Second row
        btn_frame_row2 = ttk.Frame(list_frame)
        btn_frame_row2.pack(fill=tk.X, pady=(2, 5))

        ttk.Button(
            btn_frame_row2,
            text="Remove",
            command=self.remove_selected
        ).pack(side=tk.LEFT, padx=5, ipadx=20, ipady=10)

        ttk.Button(
            btn_frame_row2,
            text="Clear",
            command=self.clear_files
        ).pack(side=tk.LEFT, padx=5, ipadx=20, ipady=10)

        # Split settings
        self._create_split_settings(list_frame)

    def _create_split_settings(self, parent):
        """Create split settings section"""
        settings_frame = ttk.LabelFrame(parent, text="Split Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(10, 0))

        # Split mode
        mode_frame = ttk.Frame(settings_frame)
        mode_frame.pack(anchor=tk.W, pady=5)

        ttk.Label(mode_frame, text="Split by:").pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            mode_frame,
            text="Duration",
            value="duration",
            variable=self.app.split_mode,
            command=self.update_split_mode
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            mode_frame,
            text="File Size",
            value="size",
            variable=self.app.split_mode,
            command=self.update_split_mode
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            mode_frame,
            text="Parts",
            value="parts",
            variable=self.app.split_mode,
            command=self.update_split_mode
        ).pack(side=tk.LEFT, padx=5)

        # Split value input
        self.split_input_frame = ttk.Frame(settings_frame)
        self.split_input_frame.pack(anchor=tk.W, pady=5)

        self.split_label = ttk.Label(self.split_input_frame, text="Duration (seconds):")
        self.split_label.pack(side=tk.LEFT, padx=(0, 10))

        self.split_entry = ttk.Entry(
            self.split_input_frame,
            textvariable=self.app.split_duration,
            width=10
        )
        self.split_entry.pack(side=tk.LEFT)

        self.split_unit = ttk.Label(self.split_input_frame, text="(5 minutes = 300)")
        self.split_unit.pack(side=tk.LEFT, padx=(10, 0))

        # Options
        ttk.Checkbutton(
            settings_frame,
            text="Keep original file after splitting",
            variable=self.app.keep_original
        ).pack(anchor=tk.W, pady=5)

    def update_split_mode(self):
        """Update split mode UI"""
        self.app.update_split_mode()

    # Delegate methods to app context
    def add_files(self):
        """Add files to split"""
        self.app.add_files('split')

    def add_large_files(self):
        """Add large files"""
        self.app.add_large_files()

    def remove_selected(self):
        """Remove selected files"""
        self.app.remove_selected('split')

    def clear_files(self):
        """Clear all files"""
        self.app.clear_files('split')

    def split_files(self):
        """Start split process"""
        self.app.split_files_action()
