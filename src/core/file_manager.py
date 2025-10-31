"""File management operations"""
import os
from tkinter import filedialog, messagebox
from pathlib import Path


class FileManager:
    """Handles file operations"""
    
    def __init__(self, app):
        self.app = app
    
    def add_files(self, tab):
        """Add files to specified tab"""
        files = filedialog.askopenfilenames(
            title="選擇檔案",
            filetypes=[
                ("All Media", "*.mp3 *.wav *.mp4 *.avi *.mkv *.mov *.m4a *.flac"),
                ("Audio", "*.mp3 *.wav *.m4a *.flac *.aac"),
                ("Video", "*.mp4 *.avi *.mkv *.mov *.flv"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            if tab == 'convert':
                for file in files:
                    if file not in self.app.convert_file_list:
                        self.app.convert_file_list.append(file)
                        self.app.convert_tab.listbox.insert('end', os.path.basename(file))
            
            elif tab == 'split':
                for file in files:
                    if file not in self.app.split_files:
                        self.app.split_files.append(file)
                        self.app.split_tab.listbox.insert('end', os.path.basename(file))
    
    def add_folder(self, tab):
        """Add all media files from a folder"""
        folder = filedialog.askdirectory(title="選擇資料夾")
        
        if folder:
            media_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.aac', 
                              '.mp4', '.avi', '.mkv', '.mov', '.flv'}
            
            for file in Path(folder).rglob('*'):
                if file.suffix.lower() in media_extensions:
                    file_path = str(file)
                    
                    if tab == 'convert':
                        if file_path not in self.app.convert_file_list:
                            self.app.convert_file_list.append(file_path)
                            self.app.convert_tab.listbox.insert('end', file.name)
                    
                    elif tab == 'split':
                        if file_path not in self.app.split_files:
                            self.app.split_files.append(file_path)
                            self.app.split_tab.listbox.insert('end', file.name)
    
    def add_large_files(self):
        """Add large files for splitting"""
        files = filedialog.askopenfilenames(
            title="選擇大型檔案",
            filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov"), ("All files", "*.*")]
        )
        
        if files:
            for file in files:
                if file not in self.app.split_files:
                    self.app.split_files.append(file)
                    
                    size_mb = os.path.getsize(file) / (1024 * 1024)
                    self.app.split_tab.listbox.insert('end', f"{Path(file).name} ({size_mb:.1f} MB)")
    
    def remove_selected(self, tab):
        """Remove selected files from list"""
        if tab == 'convert':
            listbox = self.app.convert_tab.listbox
            file_list = self.app.convert_file_list
        elif tab == 'split':
            listbox = self.app.split_tab.listbox
            file_list = self.app.split_files
        else:
            return
        
        selected = listbox.curselection()
        if selected:
            index = selected[0]
            listbox.delete(index)
            if index < len(file_list):
                del file_list[index]
    
    def clear_files(self, tab):
        """Clear all files from list"""
        if tab == 'convert':
            self.app.convert_file_list.clear()
            self.app.convert_tab.listbox.delete(0, 'end')
        elif tab == 'split':
            self.app.split_files.clear()
            self.app.split_tab.listbox.delete(0, 'end')
