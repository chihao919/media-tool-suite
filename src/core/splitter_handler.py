"""Splitter business logic"""
import os
import threading
import subprocess
from tkinter import messagebox
from pathlib import Path


class SplitHandler:
    """Handles media splitting logic"""
    
    def __init__(self, app):
        self.app = app
    
    def split_files_action(self):
        """Start split process"""
        if not self.app.split_files:
            messagebox.showwarning("No Files", "請先加入要分割的檔案")
            return
        
        self.app.split_tab.split_btn.config(state='disabled')
        thread = threading.Thread(target=self._split_worker, daemon=True)
        thread.start()
    
    def _split_worker(self):
        """Worker thread for splitting"""
        total_files = len(self.app.split_files)
        
        for idx, file_path in enumerate(self.app.split_files):
            try:
                parts_created = self._split_single_file(file_path)
                
                mode = self.app.split_mode.get()
                if mode == "duration":
                    value = self.app.split_duration.get()
                elif mode == "size":
                    value = self.app.split_size.get()
                else:
                    value = self.app.split_parts.get()
                
                self.app.add_split_history(
                    os.path.basename(file_path),
                    mode,
                    value,
                    parts_created,
                    success=True
                )
                
            except Exception as e:
                self.app.log_error("Split", file_path, str(e))
                self.app.add_split_history(
                    os.path.basename(file_path),
                    self.app.split_mode.get(),
                    "",
                    0,
                    success=False,
                    failure_reason=str(e)
                )
        
        self.app.root.after(0, lambda: self.app.split_tab.split_btn.config(state='normal'))
        
        if self.app.auto_clear.get():
            self.app.root.after(0, self._clear_completed_split_files)
    
    def _split_single_file(self, file_path):
        """Split a single file"""
        output_dir = os.path.dirname(file_path)
        filename = Path(file_path).stem
        ext = Path(file_path).suffix
        
        mode = self.app.split_mode.get()
        
        if mode == "duration":
            duration = int(self.app.split_duration.get())
            # Get total duration
            probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 
                        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', 
                        file_path]
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            total_duration = float(result.stdout.strip())
            
            parts = int(total_duration / duration) + 1
            
            for i in range(parts):
                start_time = i * duration
                output_file = os.path.join(output_dir, f"{filename}_part{i+1}{ext}")
                
                cmd = [
                    'ffmpeg', '-i', file_path,
                    '-ss', str(start_time),
                    '-t', str(duration),
                    '-c', 'copy',
                    output_file, '-y'
                ]
                subprocess.run(cmd, check=True, capture_output=True)
            
            return parts
            
        elif mode == "size":
            # Implement size-based splitting
            return 1
            
        elif mode == "parts":
            parts = int(self.app.split_parts.get())
            # Get total duration
            probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 
                        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', 
                        file_path]
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            total_duration = float(result.stdout.strip())
            
            part_duration = total_duration / parts
            
            for i in range(parts):
                start_time = i * part_duration
                output_file = os.path.join(output_dir, f"{filename}_part{i+1}{ext}")
                
                cmd = [
                    'ffmpeg', '-i', file_path,
                    '-ss', str(start_time),
                    '-t', str(part_duration),
                    '-c', 'copy',
                    output_file, '-y'
                ]
                subprocess.run(cmd, check=True, capture_output=True)
            
            return parts
        
        return 0
    
    def _clear_completed_split_files(self):
        """Clear completed files from split list"""
        self.app.split_files.clear()
        self.app.split_tab.listbox.delete(0, 'end')
