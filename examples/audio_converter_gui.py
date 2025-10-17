#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import threading
import subprocess
from pathlib import Path
import json
import platform

class AudioConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Converter - macOS")
        self.root.geometry("800x600")

        # Configure style for macOS
        style = ttk.Style()
        style.theme_use('aqua')

        # Variables
        self.input_files = []
        self.output_format = tk.StringVar(value="mp3")
        self.bitrate = tk.StringVar(value="192k")
        self.output_dir = tk.StringVar(value="")
        self.normalize = tk.BooleanVar(value=False)
        self.split_audio = tk.BooleanVar(value=False)
        self.split_duration = tk.StringVar(value="300")  # 5 minutes default

        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        # Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Files...", command=self.add_files, accelerator="⌘O")
        file_menu.add_command(label="Add Folder...", command=self.add_folder, accelerator="⌘⇧O")
        file_menu.add_separator()
        file_menu.add_command(label="Clear All", command=self.clear_files)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.root.quit, accelerator="⌘Q")

        # Bind keyboard shortcuts
        self.root.bind('<Command-o>', lambda e: self.add_files())
        self.root.bind('<Command-Shift-O>', lambda e: self.add_folder())
        self.root.bind('<Command-q>', lambda e: self.root.quit())

        # Main Frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # File List Section
        list_frame = ttk.LabelFrame(main_frame, text="Audio Files", padding="10")
        list_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # File Listbox with Scrollbar and Drag & Drop
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(list_frame, height=10, yscrollcommand=scrollbar.set,
                                       selectmode=tk.EXTENDED, bg='#f5f5f5')
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # Enable drag and drop on the listbox
        self.setup_drag_drop(self.file_listbox)

        # Add drag & drop hint
        if len(self.input_files) == 0:
            self.file_listbox.insert(tk.END, "[ Drag audio files here or use buttons below ]")
            self.file_listbox.config(fg='gray')

        # Buttons for file management
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

        ttk.Button(button_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Add Folder", command=self.add_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear All", command=self.clear_files).pack(side=tk.LEFT, padx=2)

        # Settings Section
        settings_frame = ttk.LabelFrame(main_frame, text="Conversion Settings", padding="10")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(0, 5))

        # Output Format
        ttk.Label(settings_frame, text="Output Format:").grid(row=0, column=0, sticky=tk.W, pady=2)
        format_combo = ttk.Combobox(settings_frame, textvariable=self.output_format,
                                    values=["mp3", "wav", "flac", "aac", "ogg", "m4a"],
                                    state="readonly", width=10)
        format_combo.grid(row=0, column=1, sticky=tk.W, pady=2)

        # Bitrate
        ttk.Label(settings_frame, text="Bitrate:").grid(row=1, column=0, sticky=tk.W, pady=2)
        bitrate_combo = ttk.Combobox(settings_frame, textvariable=self.bitrate,
                                     values=["128k", "192k", "256k", "320k"],
                                     state="readonly", width=10)
        bitrate_combo.grid(row=1, column=1, sticky=tk.W, pady=2)

        # Output Directory
        ttk.Label(settings_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=2)
        output_entry = ttk.Entry(settings_frame, textvariable=self.output_dir, width=25)
        output_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        output_entry.insert(0, "Same as source")  # Default text

        # When user clicks, clear the default text
        def on_entry_click(event):
            if output_entry.get() == "Same as source":
                output_entry.delete(0, tk.END)

        def on_focus_out(event):
            if output_entry.get() == "":
                output_entry.insert(0, "Same as source")

        output_entry.bind('<FocusIn>', on_entry_click)
        output_entry.bind('<FocusOut>', on_focus_out)

        ttk.Button(settings_frame, text="Browse", command=self.browse_output_dir).grid(row=2, column=2, padx=(5, 0))

        # Options Section
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Normalize Audio
        ttk.Checkbutton(options_frame, text="Normalize Audio (-16 LUFS)",
                       variable=self.normalize).pack(anchor=tk.W, pady=2)

        # Split Audio
        split_frame = ttk.Frame(options_frame)
        split_frame.pack(anchor=tk.W, pady=2)

        ttk.Checkbutton(split_frame, text="Split Audio Every",
                       variable=self.split_audio).pack(side=tk.LEFT)

        split_entry = ttk.Entry(split_frame, textvariable=self.split_duration, width=8)
        split_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(split_frame, text="seconds").pack(side=tk.LEFT)

        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack(anchor=tk.W)

        # Convert Button
        self.convert_button = ttk.Button(main_frame, text="Convert",
                                        command=self.start_conversion,
                                        style="Accent.TButton")
        self.convert_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def setup_drag_drop(self, widget):
        """Setup drag and drop functionality for a widget"""
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind('<<Drop>>', self.drop_files)

    def drop_files(self, event):
        """Handle dropped files"""
        # Clear hint text if present
        if self.file_listbox.get(0) == "[ Drag audio files here or use buttons below ]":
            self.file_listbox.delete(0)
            self.file_listbox.config(fg='black')

        # Get dropped files
        files = self.root.tk.splitlist(event.data)
        audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.WAV', '.MP3'}

        added_count = 0
        for file_path in files:
            # Handle both files and folders
            path = Path(file_path)

            if path.is_file():
                # Single file
                if path.suffix in audio_extensions and str(path) not in self.input_files:
                    self.input_files.append(str(path))
                    self.file_listbox.insert(tk.END, path.name)
                    added_count += 1
            elif path.is_dir():
                # Folder - add all audio files in it
                for audio_file in path.rglob('*'):
                    if audio_file.suffix.lower() in audio_extensions:
                        file_str = str(audio_file)
                        if file_str not in self.input_files:
                            self.input_files.append(file_str)
                            self.file_listbox.insert(tk.END, audio_file.name)
                            added_count += 1

        # Show feedback
        if added_count > 0:
            self.status_label.config(text=f"Added {added_count} audio file(s)")
        else:
            messagebox.showinfo("No Audio Files", "No valid audio files found in the dropped items")

    def add_files(self):
        # Clear hint text if present
        if self.file_listbox.size() > 0 and self.file_listbox.get(0) == "[ Drag audio files here or use buttons below ]":
            self.file_listbox.delete(0)
            self.file_listbox.config(fg='black')

        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.flac *.aac *.ogg *.m4a *.wma"),
                ("All Files", "*.*")
            ]
        )
        for file in files:
            if file not in self.input_files:
                self.input_files.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))

    def add_folder(self):
        # Clear hint text if present
        if self.file_listbox.size() > 0 and self.file_listbox.get(0) == "[ Drag audio files here or use buttons below ]":
            self.file_listbox.delete(0)
            self.file_listbox.config(fg='black')

        folder = filedialog.askdirectory(title="Select Folder with Audio Files")
        if folder:
            audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'}
            for file in Path(folder).rglob('*'):
                if file.suffix.lower() in audio_extensions:
                    file_path = str(file)
                    if file_path not in self.input_files:
                        self.input_files.append(file_path)
                        self.file_listbox.insert(tk.END, os.path.basename(file_path))

    def remove_selected(self):
        selected = self.file_listbox.curselection()
        for index in reversed(selected):
            self.file_listbox.delete(index)
            del self.input_files[index]

    def clear_files(self):
        self.file_listbox.delete(0, tk.END)
        self.input_files = []

    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)

    def start_conversion(self):
        if not self.input_files:
            messagebox.showwarning("No Files", "Please add audio files to convert")
            return

        # If no output directory specified, use "same as source" option
        if not self.output_dir.get():
            self.output_dir.set("same")  # Special flag for same directory as source

        # Disable convert button during conversion
        self.convert_button.config(state='disabled')

        # Start conversion in separate thread
        thread = threading.Thread(target=self.convert_files)
        thread.daemon = True
        thread.start()

    def convert_files(self):
        total_files = len(self.input_files)
        base_output_dir = self.output_dir.get()

        for i, input_file in enumerate(self.input_files):
            # Update progress
            progress = (i / total_files) * 100
            self.progress_var.set(progress)
            self.status_label.config(text=f"Converting {i+1}/{total_files}: {os.path.basename(input_file)}")

            try:
                # Determine output directory
                input_path = Path(input_file)
                if base_output_dir == "same" or base_output_dir == "":
                    # Use same directory as source file
                    output_dir = str(input_path.parent)
                else:
                    output_dir = base_output_dir

                # Build output path
                output_name = input_path.stem + '_converted.' + self.output_format.get()
                output_path = os.path.join(output_dir, output_name)

                cmd = ['ffmpeg', '-i', input_file, '-y']

                # Add format-specific options
                if self.output_format.get() == 'mp3':
                    cmd.extend(['-acodec', 'libmp3lame', '-b:a', self.bitrate.get()])
                elif self.output_format.get() == 'aac':
                    cmd.extend(['-acodec', 'aac', '-b:a', self.bitrate.get()])
                elif self.output_format.get() == 'flac':
                    cmd.extend(['-acodec', 'flac'])
                elif self.output_format.get() == 'wav':
                    cmd.extend(['-acodec', 'pcm_s16le'])

                # Add normalization if requested
                if self.normalize.get():
                    cmd.extend(['-af', 'loudnorm=I=-16:TP=-1.5:LRA=11'])

                # Add output file
                cmd.append(output_path)

                # Execute conversion
                subprocess.run(cmd, check=True, capture_output=True)

                # Handle splitting if requested
                if self.split_audio.get():
                    self.split_audio_file(output_path, float(self.split_duration.get()))

            except subprocess.CalledProcessError as e:
                self.root.after(0, lambda: messagebox.showerror("Conversion Error",
                                                               f"Failed to convert {os.path.basename(input_file)}"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        # Update final progress
        self.progress_var.set(100)
        self.status_label.config(text=f"Completed! Converted {total_files} files")

        # Re-enable convert button
        self.root.after(0, lambda: self.convert_button.config(state='normal'))

        # Show completion message
        self.root.after(0, lambda: messagebox.showinfo("Conversion Complete",
                                                      f"Successfully converted {total_files} files"))

    def split_audio_file(self, audio_path, duration):
        """Split audio file into segments"""
        try:
            # Get total duration
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                   '-of', 'default=noprint_wrappers=1:nokey=1', audio_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            total_duration = float(result.stdout.strip())

            # Calculate number of segments
            num_segments = int(total_duration // duration) + (1 if total_duration % duration > 0 else 0)

            # Split the file
            base_path = Path(audio_path)
            base_name = base_path.stem
            extension = base_path.suffix

            for i in range(num_segments):
                start_time = i * duration
                segment_duration = min(duration, total_duration - start_time)

                output_name = f"{base_name}_part{i+1}{extension}"
                output_path = base_path.parent / output_name

                cmd = ['ffmpeg', '-i', audio_path, '-ss', str(start_time),
                       '-t', str(segment_duration), '-y', str(output_path)]
                subprocess.run(cmd, check=True, capture_output=True)

            # Remove original file after splitting
            os.remove(audio_path)

        except Exception as e:
            print(f"Error splitting audio: {e}")

    def save_settings(self):
        """Save current settings to file"""
        settings = {
            'output_format': self.output_format.get(),
            'bitrate': self.bitrate.get(),
            'output_dir': self.output_dir.get(),
            'normalize': self.normalize.get(),
            'split_audio': self.split_audio.get(),
            'split_duration': self.split_duration.get()
        }

        settings_file = Path.home() / '.audio_converter_settings.json'
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)

    def load_settings(self):
        """Load settings from file"""
        settings_file = Path.home() / '.audio_converter_settings.json'
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)

                self.output_format.set(settings.get('output_format', 'mp3'))
                self.bitrate.set(settings.get('bitrate', '192k'))
                self.output_dir.set(settings.get('output_dir', ''))
                self.normalize.set(settings.get('normalize', False))
                self.split_audio.set(settings.get('split_audio', False))
                self.split_duration.set(settings.get('split_duration', '300'))
            except Exception:
                pass

    def __del__(self):
        """Save settings when closing"""
        try:
            self.save_settings()
        except:
            pass

def main():
    # Use TkinterDnD for drag and drop support
    try:
        root = TkinterDnD.Tk()
    except:
        # Fallback to regular Tk if TkinterDnD is not available
        root = tk.Tk()
        print("Note: Drag and drop not available. Install tkinterdnd2 for this feature.")

    # Set macOS specific properties
    if platform.system() == 'Darwin':
        try:
            root.tk.call('tk', 'scaling', 2.0)  # For Retina displays
        except:
            pass

    app = AudioConverterGUI(root)

    # Save settings on close
    root.protocol("WM_DELETE_WINDOW", lambda: [app.save_settings(), root.quit()])

    root.mainloop()

if __name__ == "__main__":
    main()