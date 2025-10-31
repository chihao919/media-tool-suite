"""History Tab UI Component"""

import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab


class HistoryTab(BaseTab):
    """UI for conversion and split history"""

    def setup_ui(self):
        """Setup the History tab UI"""
        # Statistics section
        self._create_statistics_section()

        # History notebook
        self._create_history_notebook()

        # Clear button
        ttk.Button(
            self.main_frame,
            text="Clear All History",
            command=self.clear_history
        ).pack(pady=10)

    def _create_statistics_section(self):
        """Create statistics section"""
        stats_frame = ttk.LabelFrame(self.main_frame, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        # Total conversions
        self.total_conversions_label = ttk.Label(
            stats_frame,
            text="Total Conversions: 0",
            font=('Helvetica', 11)
        )
        self.total_conversions_label.pack(anchor=tk.W, pady=2)

        # Total splits
        self.total_splits_label = ttk.Label(
            stats_frame,
            text="Total Splits: 0",
            font=('Helvetica', 11)
        )
        self.total_splits_label.pack(anchor=tk.W, pady=2)

        # Success rate
        self.success_rate_label = ttk.Label(
            stats_frame,
            text="Success Rate: 0%",
            font=('Helvetica', 11)
        )
        self.success_rate_label.pack(anchor=tk.W, pady=2)

    def _create_history_notebook(self):
        """Create history notebook with tabs"""
        history_notebook = ttk.Notebook(self.main_frame)
        history_notebook.pack(fill=tk.BOTH, expand=True)

        # Conversion history tab
        convert_history_frame = ttk.Frame(history_notebook, padding="10")
        history_notebook.add(convert_history_frame, text="Conversion History")

        self.convert_history_tree = self._create_treeview(
            convert_history_frame,
            columns=("File", "From", "To", "Status", "Time"),
            headings=("File", "From", "To", "Status", "Time")
        )

        # Split history tab
        split_history_frame = ttk.Frame(history_notebook, padding="10")
        history_notebook.add(split_history_frame, text="Split History")

        self.split_history_tree = self._create_treeview(
            split_history_frame,
            columns=("File", "Mode", "Value", "Parts", "Status", "Time"),
            headings=("File", "Mode", "Value", "Parts", "Status", "Time")
        )

    def _create_treeview(self, parent, columns, headings):
        """Create a treeview with scrollbar"""
        # Create frame
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        # Treeview
        tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        # Set headings
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=100)

        # Pack
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        return tree

    def clear_history(self):
        """Clear all history"""
        self.app.clear_history()

    def update_statistics(self):
        """Update statistics display"""
        self.app.update_statistics()
