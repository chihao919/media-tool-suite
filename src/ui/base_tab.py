"""Base class for all tabs in the application"""

import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod


class BaseTab(ABC):
    """Base class for all tab UI components"""

    def __init__(self, parent, app_context):
        """
        Initialize the tab

        Args:
            parent: The parent frame (notebook tab frame)
            app_context: Reference to the main application for shared resources
        """
        self.parent = parent
        self.app = app_context
        self.main_frame = ttk.Frame(parent, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Setup the tab UI
        self.setup_ui()

    @abstractmethod
    def setup_ui(self):
        """Setup the tab's UI components - must be implemented by subclasses"""
        pass

    def create_file_list_section(self, title, listbox_var_name, add_command,
                                 remove_command, clear_command, add_folder_command=None):
        """
        Create a standard file list section with add/remove/clear buttons

        Args:
            title: Section title
            listbox_var_name: Name to store the listbox widget
            add_command: Command for add files button
            remove_command: Command for remove button
            clear_command: Command for clear button
            add_folder_command: Optional command for add folder button

        Returns:
            The listbox widget
        """
        list_frame = ttk.LabelFrame(self.main_frame, text=title, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Listbox with scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(list_frame, height=8, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # Store listbox reference
        setattr(self, listbox_var_name, listbox)

        # Buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(btn_frame, text="Add Files",
                  command=add_command).pack(side=tk.LEFT, padx=5, ipadx=20, ipady=10)

        if add_folder_command:
            ttk.Button(btn_frame, text="Add Folder",
                      command=add_folder_command).pack(side=tk.LEFT, padx=5, ipadx=20, ipady=10)

        ttk.Button(btn_frame, text="Remove",
                  command=remove_command).pack(side=tk.LEFT, padx=5, ipadx=20, ipady=10)
        ttk.Button(btn_frame, text="Clear",
                  command=clear_command).pack(side=tk.LEFT, padx=5, ipadx=20, ipady=10)

        return listbox

    def create_progress_section(self, progress_var_name='progress',
                               status_var_name='status'):
        """
        Create a standard progress bar and status label section

        Args:
            progress_var_name: Name to store the progress bar widget
            status_var_name: Name to store the status label widget
        """
        # Progress bar
        progress = ttk.Progressbar(self.main_frame, mode='determinate')
        progress.pack(fill=tk.X, pady=5, padx=20)
        setattr(self, progress_var_name, progress)

        # Status label
        status = ttk.Label(self.main_frame, text="Ready")
        status.pack(pady=5)
        setattr(self, status_var_name, status)

    def update_status(self, message, status_var_name='status'):
        """Update status label with a message"""
        status_widget = getattr(self, status_var_name, None)
        if status_widget:
            status_widget.config(text=message)

    def update_progress(self, value, progress_var_name='progress'):
        """Update progress bar value (0-100)"""
        progress_widget = getattr(self, progress_var_name, None)
        if progress_widget:
            progress_widget['value'] = value
