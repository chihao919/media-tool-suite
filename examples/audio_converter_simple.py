#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import subprocess
from pathlib import Path
import json

class SimpleAudioConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Converter - Simple")
        self.root.geometry("700x500")

        # Variables
        self.input_files = []
        self.output_format = tk.StringVar(value="mp3")
        self.bitrate = tk.StringVar(value="192k")

        self.create_widgets()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(main_frame, text="🎵 Audio Converter", font=('Helvetica', 18, 'bold'))
        title.pack(pady=(0, 10))

        # File drop area (visual)
        drop_frame = tk.Frame(main_frame, bg='#e0e0e0', relief=tk.SUNKEN, bd=2)
        drop_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # List of files
        list_container = tk.Frame(drop_frame, bg='#e0e0e0')
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set,
                                       height=8, font=('Helvetica', 11))
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # Drop hint
        self.drop_hint = tk.Label(drop_frame, text="📁 Drop files here or click buttons below",
                                 bg='#e0e0e0', font=('Helvetica', 12), fg='#666')
        self.drop_hint.place(relx=0.5, rely=0.5, anchor='center')

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="➕ Add Files",
                  command=self.add_files, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="📁 Add Folder",
                  command=self.add_folder, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="❌ Remove",
                  command=self.remove_selected, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🗑 Clear All",
                  command=self.clear_files, width=15).pack(side=tk.LEFT, padx=2)

        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=10)

        # Format selection
        ttk.Label(settings_frame, text="Output Format:").grid(row=0, column=0, sticky=tk.W, padx=5)
        format_menu = ttk.Combobox(settings_frame, textvariable=self.output_format,
                                   values=["mp3", "wav", "flac", "aac", "ogg", "m4a"],
                                   state="readonly", width=10)
        format_menu.grid(row=0, column=1, padx=5)

        # Bitrate selection
        ttk.Label(settings_frame, text="Bitrate:").grid(row=0, column=2, sticky=tk.W, padx=5)
        bitrate_menu = ttk.Combobox(settings_frame, textvariable=self.bitrate,
                                    values=["128k", "192k", "256k", "320k"],
                                    state="readonly", width=10)
        bitrate_menu.grid(row=0, column=3, padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)

        # Status label
        self.status = tk.Label(main_frame, text="Ready", fg='#666')
        self.status.pack()

        # Convert button
        self.convert_btn = tk.Button(main_frame, text="🚀 Convert All",
                                     command=self.start_conversion,
                                     bg='#4CAF50', fg='white', font=('Helvetica', 12, 'bold'),
                                     height=2, width=20)
        self.convert_btn.pack(pady=10)

        # Bind file dialog to drop area click
        drop_frame.bind("<Button-1>", lambda e: self.add_files())
        self.file_listbox.bind("<Delete>", lambda e: self.remove_selected())
        self.file_listbox.bind("<BackSpace>", lambda e: self.remove_selected())

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.flac *.aac *.ogg *.m4a *.wma *.WAV *.MP3"),
                ("All Files", "*.*")
            ]
        )

        if files:
            self.drop_hint.place_forget()
            for file in files:
                if file not in self.input_files:
                    self.input_files.append(file)
                    self.file_listbox.insert(tk.END, f"🎵 {os.path.basename(file)}")

            self.status.config(text=f"{len(self.input_files)} files ready")

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self.drop_hint.place_forget()
            audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'}
            count = 0

            for file in Path(folder).glob('**/*'):
                if file.suffix.lower() in audio_extensions:
                    file_path = str(file)
                    if file_path not in self.input_files:
                        self.input_files.append(file_path)
                        self.file_listbox.insert(tk.END, f"🎵 {file.name}")
                        count += 1

            if count > 0:
                self.status.config(text=f"Added {count} files from folder")

    def remove_selected(self):
        selected = self.file_listbox.curselection()
        for index in reversed(selected):
            self.file_listbox.delete(index)
            del self.input_files[index]

        if len(self.input_files) == 0:
            self.drop_hint.place(relx=0.5, rely=0.5, anchor='center')
            self.status.config(text="Ready")

    def clear_files(self):
        self.file_listbox.delete(0, tk.END)
        self.input_files = []
        self.drop_hint.place(relx=0.5, rely=0.5, anchor='center')
        self.status.config(text="Ready")

    def start_conversion(self):
        if not self.input_files:
            messagebox.showwarning("No Files", "Please add audio files first")
            return

        # Ask user for output location preference
        result = messagebox.askyesnocancel(
            "Output Location",
            "Save converted files in the same folder as original files?\n\n"
            "Yes = Same folder as original\n"
            "No = Choose a different folder\n"
            "Cancel = Cancel conversion"
        )

        if result is None:  # Cancel
            return
        elif result is False:  # Choose different folder
            output_dir = filedialog.askdirectory(title="Select Output Folder")
            if not output_dir:
                return
            use_same_folder = False
        else:  # Yes - use same folder
            output_dir = None
            use_same_folder = True

        self.convert_btn.config(state='disabled')
        self.progress['value'] = 0

        # Start conversion in thread
        thread = threading.Thread(target=self.convert_files, args=(output_dir, use_same_folder))
        thread.daemon = True
        thread.start()

    def convert_files(self, output_dir, use_same_folder):
        total = len(self.input_files)
        converted_files = []

        for i, input_file in enumerate(self.input_files):
            # Update progress
            progress = ((i + 1) / total) * 100
            self.root.after(0, lambda p=progress: self.progress.configure(value=p))

            filename = os.path.basename(input_file)
            self.root.after(0, lambda f=filename: self.status.config(text=f"Converting: {f}"))

            try:
                # Determine output location
                if use_same_folder:
                    # Use same directory as source file
                    file_dir = os.path.dirname(input_file)
                    output_dir_for_file = file_dir
                else:
                    output_dir_for_file = output_dir

                # Create output filename
                base_name = Path(input_file).stem
                output_file = os.path.join(output_dir_for_file,
                                          f"{base_name}_converted.{self.output_format.get()}")

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

                cmd.append(output_file)

                # Run conversion
                subprocess.run(cmd, check=True, capture_output=True)
                converted_files.append(output_file)

            except Exception as e:
                print(f"Error converting {input_file}: {e}")

        # Conversion complete
        self.root.after(0, lambda: self.status.config(text=f"✅ Converted {total} files successfully!"))
        self.root.after(0, lambda: self.convert_btn.config(state='normal'))

        # Show success message
        if use_same_folder:
            msg = f"Converted {len(converted_files)} files\nFiles saved in their original folders with '_converted' suffix"
        else:
            msg = f"Converted {len(converted_files)} files\nOutput folder: {output_dir}"

        self.root.after(0, lambda: messagebox.showinfo("Success", msg))

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleAudioConverter(root)
    root.mainloop()