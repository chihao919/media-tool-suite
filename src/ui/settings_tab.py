"""Settings Tab UI Component"""

import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab
from app_constants import AppConstants


class SettingsTab(BaseTab):
    """UI for application settings"""

    def setup_ui(self):
        """Setup the Settings tab UI"""
        # Title and description
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(
            title_frame,
            text="Default Settings",
            font=('Helvetica', 14, 'bold')
        ).pack(anchor=tk.W)

        description_text = ("這些預設值會自動套用到 Convert 和 Split 功能。\n"
                          "修改後點擊「Apply Settings」套用到目前工作區,或「Save Settings」永久儲存。")
        ttk.Label(
            title_frame,
            text=description_text,
            font=('Helvetica', 9),
            foreground='#666666',
            wraplength=650
        ).pack(anchor=tk.W, pady=(5, 0))

        # Create scrollable frame
        self._create_scrollable_settings()

        # Buttons
        self._create_buttons()

    def _create_scrollable_settings(self):
        """Create scrollable settings frame"""
        canvas = tk.Canvas(self.main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Convert defaults
        self._create_convert_defaults(scrollable_frame)

        # Split defaults
        self._create_split_defaults(scrollable_frame)

        # General settings
        self._create_general_settings(scrollable_frame)

    def _create_convert_defaults(self, parent):
        """Create convert defaults section"""
        convert_frame = ttk.LabelFrame(parent, text="Convert 預設設定", padding="10")
        convert_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            convert_frame,
            text="轉檔預設設定",
            font=('Helvetica', 11, 'bold')
        ).pack(anchor=tk.W)

        # Format
        format_frame = ttk.Frame(convert_frame)
        format_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(format_frame, text="Output format:").pack(side=tk.LEFT, padx=(0, 10))

        all_formats = AppConstants.AUDIO_FORMAT_OPTIONS + AppConstants.VIDEO_FORMAT_OPTIONS
        ttk.Combobox(
            format_frame,
            textvariable=self.app.default_format,
            values=all_formats,
            state="readonly",
            width=8
        ).pack(side=tk.LEFT)

        # Bitrate
        bitrate_frame = ttk.Frame(convert_frame)
        bitrate_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(bitrate_frame, text="Bitrate:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Combobox(
            bitrate_frame,
            textvariable=self.app.default_bitrate,
            values=AppConstants.BITRATE_OPTIONS,
            state="readonly",
            width=8
        ).pack(side=tk.LEFT)

        # Sample rate
        sample_frame = ttk.Frame(convert_frame)
        sample_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(sample_frame, text="Sample rate:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Combobox(
            sample_frame,
            textvariable=self.app.default_sample_rate,
            values=AppConstants.SAMPLE_RATE_OPTIONS,
            state="readonly",
            width=8
        ).pack(side=tk.LEFT)

        # Normalize
        ttk.Checkbutton(
            convert_frame,
            text="Enable audio normalization by default",
            variable=self.app.default_normalize
        ).pack(anchor=tk.W, pady=5)

    def _create_split_defaults(self, parent):
        """Create split defaults section"""
        split_frame = ttk.LabelFrame(parent, text="Split 預設設定", padding="10")
        split_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            split_frame,
            text="分割預設設定",
            font=('Helvetica', 11, 'bold')
        ).pack(anchor=tk.W)

        # Split mode
        mode_frame = ttk.Frame(split_frame)
        mode_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(mode_frame, text="Default split mode:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Combobox(
            mode_frame,
            textvariable=self.app.default_split_mode,
            values=AppConstants.SPLIT_MODE_OPTIONS,
            state="readonly",
            width=10
        ).pack(side=tk.LEFT)

        # Duration
        duration_frame = ttk.Frame(split_frame)
        duration_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(duration_frame, text="Default duration (seconds):").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(
            duration_frame,
            textvariable=self.app.default_split_duration,
            width=10
        ).pack(side=tk.LEFT)

        # Keep original
        ttk.Checkbutton(
            split_frame,
            text="Keep original files after splitting by default",
            variable=self.app.default_keep_original
        ).pack(anchor=tk.W, pady=5)

    def _create_general_settings(self, parent):
        """Create general settings section"""
        general_frame = ttk.LabelFrame(parent, text="一般預設設定", padding="10")
        general_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            general_frame,
            text="一般預設設定",
            font=('Helvetica', 11, 'bold')
        ).pack(anchor=tk.W)

        ttk.Label(
            general_frame,
            text="設定檔案輸出位置、命名規則和自動化行為",
            font=('Helvetica', 9),
            foreground='#666666'
        ).pack(anchor=tk.W, pady=(2, 10))

        # Output location
        ttk.Label(general_frame, text="Default output location:").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(
            general_frame,
            text="Same as source file",
            value="same",
            variable=self.app.output_location
        ).pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(
            general_frame,
            text="Ask every time",
            value="ask",
            variable=self.app.output_location
        ).pack(anchor=tk.W, padx=20)

        # Naming style
        ttk.Label(general_frame, text="File naming:").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(
            general_frame,
            text="Keep original name",
            value="original",
            variable=self.app.naming_style
        ).pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(
            general_frame,
            text="Add suffix '_converted'",
            value="suffix",
            variable=self.app.naming_style
        ).pack(anchor=tk.W, padx=20)

        # Auto-clear
        ttk.Checkbutton(
            general_frame,
            text="Auto-clear completed files from lists",
            variable=self.app.auto_clear
        ).pack(anchor=tk.W, pady=5)

    def _create_buttons(self):
        """Create control buttons"""
        buttons_section = ttk.Frame(self.main_frame)
        buttons_section.pack(fill=tk.X, pady=(20, 0))

        ttk.Label(
            buttons_section,
            text="Instructions:",
            font=('Helvetica', 12, 'bold')
        ).pack(anchor=tk.W)

        instructions = ("• Apply Settings: Immediately apply settings to Convert and Split tabs\n"
                       "• Reset to Defaults: Reset all settings to factory defaults\n"
                       "• Save Settings: Permanently save settings (persist after restart)")
        ttk.Label(
            buttons_section,
            text=instructions,
            font=('Helvetica', 10),
            foreground='#555555',
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(5, 10))

        buttons_frame = ttk.Frame(buttons_section)
        buttons_frame.pack(fill=tk.X)

        ttk.Button(
            buttons_frame,
            text="Apply Settings",
            command=self.app.apply_all_settings
        ).pack(side=tk.LEFT, padx=8, ipadx=15, ipady=8)

        ttk.Button(
            buttons_frame,
            text="Reset to Defaults",
            command=self.app.reset_to_defaults
        ).pack(side=tk.LEFT, padx=8, ipadx=15, ipady=8)

        ttk.Button(
            buttons_frame,
            text="Save Settings",
            command=self.app.save_settings
        ).pack(side=tk.LEFT, padx=8, ipadx=15, ipady=8)
