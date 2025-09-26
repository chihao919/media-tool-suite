#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import subprocess
from pathlib import Path
import json

class UnifiedAudioConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Converter")
        self.root.geometry("600x450")

        # Variables
        self.input_files = []
        self.output_format = tk.StringVar(value="mp3")
        self.bitrate = tk.StringVar(value="192k")
        self.output_dir = tk.StringVar(value="")
        self.advanced_mode = tk.BooleanVar(value=False)
        self.normalize = tk.BooleanVar(value=False)
        self.sample_rate = tk.StringVar(value="44100")

        self.create_widgets()

    def create_widgets(self):
        # Top bar with mode toggle
        top_bar = ttk.Frame(self.root)
        top_bar.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(top_bar, text="🎵 Audio Converter", font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT)

        # Mode toggle switch
        mode_frame = ttk.Frame(top_bar)
        mode_frame.pack(side=tk.RIGHT)
        ttk.Label(mode_frame, text="Simple").pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(mode_frame, text="Advanced",
                       variable=self.advanced_mode,
                       command=self.toggle_mode).pack(side=tk.LEFT)

        # Main container
        self.main_container = ttk.Frame(self.root, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Create both interfaces
        self.create_simple_interface()
        self.create_advanced_interface()

        # Show simple mode by default
        self.show_simple_mode()

    def create_simple_interface(self):
        """Create simple mode interface"""
        self.simple_frame = ttk.Frame(self.main_container)

        # File list area
        list_frame = ttk.LabelFrame(self.simple_frame, text="Audio Files", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.simple_listbox = tk.Listbox(list_frame, height=8, yscrollcommand=scrollbar.set)
        self.simple_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.simple_listbox.yview)

        # Buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(btn_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear", command=self.clear_files).pack(side=tk.LEFT, padx=2)

        # Simple settings
        settings_frame = ttk.Frame(self.simple_frame)
        settings_frame.pack(fill=tk.X, pady=10)

        ttk.Label(settings_frame, text="Convert to:").pack(side=tk.LEFT, padx=5)
        format_combo = ttk.Combobox(settings_frame, textvariable=self.output_format,
                                    values=["mp3", "wav", "m4a"],
                                    state="readonly", width=8)
        format_combo.pack(side=tk.LEFT)

        # Convert button
        self.simple_convert_btn = ttk.Button(self.simple_frame, text="Convert",
                                            command=self.start_conversion,
                                            style="Accent.TButton")
        self.simple_convert_btn.pack(pady=10)

        # Status
        self.simple_status = ttk.Label(self.simple_frame, text="Ready")
        self.simple_status.pack()

    def create_advanced_interface(self):
        """Create advanced mode interface"""
        self.advanced_frame = ttk.Frame(self.main_container)

        # File list (smaller in advanced mode)
        list_frame = ttk.LabelFrame(self.advanced_frame, text="Audio Files", padding="5")
        list_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.advanced_listbox = tk.Listbox(list_frame, height=6, yscrollcommand=scrollbar.set)
        self.advanced_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.advanced_listbox.yview)

        # File buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(btn_frame, text="Add Files", command=self.add_files, width=10).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_frame, text="Add Folder", command=self.add_folder, width=10).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_frame, text="Remove", command=self.remove_selected, width=10).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_frame, text="Clear", command=self.clear_files, width=10).pack(side=tk.LEFT, padx=1)

        # Format settings
        format_frame = ttk.LabelFrame(self.advanced_frame, text="Format Settings", padding="10")
        format_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5, padx=(0, 5))

        ttk.Label(format_frame, text="Output Format:").grid(row=0, column=0, sticky=tk.W)
        format_combo = ttk.Combobox(format_frame, textvariable=self.output_format,
                                    values=["mp3", "wav", "flac", "aac", "ogg", "m4a"],
                                    state="readonly", width=10)
        format_combo.grid(row=0, column=1, padx=5)

        ttk.Label(format_frame, text="Bitrate:").grid(row=1, column=0, sticky=tk.W)
        bitrate_combo = ttk.Combobox(format_frame, textvariable=self.bitrate,
                                     values=["128k", "192k", "256k", "320k"],
                                     state="readonly", width=10)
        bitrate_combo.grid(row=1, column=1, padx=5)

        ttk.Label(format_frame, text="Sample Rate:").grid(row=2, column=0, sticky=tk.W)
        sample_combo = ttk.Combobox(format_frame, textvariable=self.sample_rate,
                                    values=["44100", "48000", "96000"],
                                    state="readonly", width=10)
        sample_combo.grid(row=2, column=1, padx=5)

        # Options
        options_frame = ttk.LabelFrame(self.advanced_frame, text="Options", padding="10")
        options_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Checkbutton(options_frame, text="Normalize Audio",
                       variable=self.normalize).pack(anchor=tk.W)

        ttk.Label(options_frame, text="Output Folder:").pack(anchor=tk.W, pady=(10, 0))
        output_entry = ttk.Entry(options_frame, textvariable=self.output_dir, width=20)
        output_entry.pack(anchor=tk.W)
        ttk.Button(options_frame, text="Browse",
                  command=self.browse_output, width=10).pack(anchor=tk.W, pady=2)

        # Progress bar
        self.progress = ttk.Progressbar(self.advanced_frame, mode='determinate')
        self.progress.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Convert button
        self.advanced_convert_btn = ttk.Button(self.advanced_frame, text="Convert All",
                                              command=self.start_conversion,
                                              style="Accent.TButton")
        self.advanced_convert_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # Status
        self.advanced_status = ttk.Label(self.advanced_frame, text="Ready")
        self.advanced_status.grid(row=4, column=0, columnspan=2)

        # Configure grid weights
        self.advanced_frame.columnconfigure(0, weight=1)
        self.advanced_frame.columnconfigure(1, weight=1)
        self.advanced_frame.rowconfigure(0, weight=1)

    def toggle_mode(self):
        """Switch between simple and advanced mode"""
        if self.advanced_mode.get():
            self.show_advanced_mode()
        else:
            self.show_simple_mode()

    def show_simple_mode(self):
        """Show simple interface"""
        self.advanced_frame.pack_forget()
        self.simple_frame.pack(fill=tk.BOTH, expand=True)
        self.root.geometry("600x450")

        # Sync listbox content
        self.sync_listboxes(self.advanced_listbox, self.simple_listbox)

    def show_advanced_mode(self):
        """Show advanced interface"""
        self.simple_frame.pack_forget()
        self.advanced_frame.pack(fill=tk.BOTH, expand=True)
        self.root.geometry("700x500")

        # Sync listbox content
        self.sync_listboxes(self.simple_listbox, self.advanced_listbox)

    def sync_listboxes(self, from_listbox, to_listbox):
        """Sync content between listboxes when switching modes"""
        to_listbox.delete(0, tk.END)
        for i in range(from_listbox.size()):
            to_listbox.insert(tk.END, from_listbox.get(i))

    def get_current_listbox(self):
        """Get the currently visible listbox"""
        return self.advanced_listbox if self.advanced_mode.get() else self.simple_listbox

    def get_current_status(self):
        """Get the currently visible status label"""
        return self.advanced_status if self.advanced_mode.get() else self.simple_status

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.aac *.ogg *.m4a"), ("All Files", "*.*")]
        )

        listbox = self.get_current_listbox()
        for file in files:
            if file not in self.input_files:
                self.input_files.append(file)
                listbox.insert(tk.END, os.path.basename(file))

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
            listbox = self.get_current_listbox()

            for file in Path(folder).glob('**/*'):
                if file.suffix.lower() in audio_extensions:
                    file_path = str(file)
                    if file_path not in self.input_files:
                        self.input_files.append(file_path)
                        listbox.insert(tk.END, file.name)

    def remove_selected(self):
        listbox = self.get_current_listbox()
        selected = listbox.curselection()
        for index in reversed(selected):
            listbox.delete(index)
            del self.input_files[index]

    def clear_files(self):
        self.input_files = []
        self.simple_listbox.delete(0, tk.END)
        self.advanced_listbox.delete(0, tk.END)

    def browse_output(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)

    def start_conversion(self):
        if not self.input_files:
            messagebox.showwarning("No Files", "Please add audio files to convert")
            return

        # Determine output directory
        if self.advanced_mode.get() and self.output_dir.get():
            output_dir = self.output_dir.get()
        else:
            # Ask user in simple mode
            result = messagebox.askyesno("Output Location",
                                        "Save in same folder as original files?")
            output_dir = None if result else filedialog.askdirectory(title="Select Output Folder")
            if not result and not output_dir:
                return

        # Disable convert button
        if self.advanced_mode.get():
            self.advanced_convert_btn.config(state='disabled')
        else:
            self.simple_convert_btn.config(state='disabled')

        # Start conversion in thread
        thread = threading.Thread(target=self.convert_files, args=(output_dir,))
        thread.daemon = True
        thread.start()

    def convert_files(self, output_dir):
        total = len(self.input_files)
        status_label = self.get_current_status()

        for i, input_file in enumerate(self.input_files):
            # Update progress
            if self.advanced_mode.get():
                progress = ((i + 1) / total) * 100
                self.root.after(0, lambda p=progress: self.progress.configure(value=p))

            filename = os.path.basename(input_file)
            self.root.after(0, lambda f=filename: status_label.config(text=f"Converting: {f}"))

            try:
                # Determine output location
                if output_dir:
                    output_folder = output_dir
                else:
                    output_folder = os.path.dirname(input_file)

                # Build output path
                base_name = Path(input_file).stem
                output_file = os.path.join(output_folder,
                                          f"{base_name}.{self.output_format.get()}")

                # Build ffmpeg command
                cmd = ['ffmpeg', '-i', input_file, '-y']

                if self.output_format.get() == 'mp3':
                    cmd.extend(['-acodec', 'libmp3lame', '-b:a', self.bitrate.get()])
                elif self.output_format.get() == 'aac':
                    cmd.extend(['-acodec', 'aac', '-b:a', self.bitrate.get()])
                elif self.output_format.get() == 'flac':
                    cmd.extend(['-acodec', 'flac'])
                elif self.output_format.get() == 'wav':
                    cmd.extend(['-acodec', 'pcm_s16le'])

                # Add sample rate if in advanced mode
                if self.advanced_mode.get():
                    cmd.extend(['-ar', self.sample_rate.get()])

                # Add normalization if enabled
                if self.advanced_mode.get() and self.normalize.get():
                    cmd.extend(['-af', 'loudnorm=I=-16:TP=-1.5:LRA=11'])

                cmd.append(output_file)

                # Run conversion
                subprocess.run(cmd, check=True, capture_output=True)

            except Exception as e:
                print(f"Error converting {input_file}: {e}")

        # Conversion complete
        self.root.after(0, lambda: status_label.config(text=f"✓ Converted {total} files"))

        # Re-enable button
        if self.advanced_mode.get():
            self.root.after(0, lambda: self.advanced_convert_btn.config(state='normal'))
        else:
            self.root.after(0, lambda: self.simple_convert_btn.config(state='normal'))

        self.root.after(0, lambda: messagebox.showinfo("Success", f"Converted {total} files successfully!"))

if __name__ == "__main__":
    root = tk.Tk()
    app = UnifiedAudioConverter(root)
    root.mainloop()