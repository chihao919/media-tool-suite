"""Converter business logic"""
import os
import threading
from tkinter import filedialog, messagebox
from pathlib import Path
from media_processor import MediaProcessor, MediaProcessorBuilder
from media_handlers import MediaHandlerFactory


class ConvertHandler:
    """Handles media conversion logic"""
    
    def __init__(self, app):
        self.app = app
    
    def convert_files(self):
        """Start conversion process"""
        if not self.app.convert_file_list:
            messagebox.showwarning("No Files", "請先加入要轉換的檔案")
            return
        
        self.app.convert_tab.convert_btn.config(state='disabled')
        self.app.convert_tab.progress['value'] = 0
        self.app.convert_tab.status.config(text="Converting...")
        
        thread = threading.Thread(target=self._convert_worker, daemon=True)
        thread.start()
    
    def _convert_worker(self, custom_output_dir=None):
        """Worker thread for conversion"""
        total_files = len(self.app.convert_file_list)
        
        for idx, file_path in enumerate(self.app.convert_file_list):
            try:
                # Determine output format
                media_type = self.app.media_type.get()
                
                if media_type == "audio" or self.app.audio_format.get():
                    output_format = self.app.audio_format.get()
                elif media_type == "video" or self.app.video_format.get():
                    output_format = self.app.video_format.get()
                else:
                    output_format = "mp3"
                
                # Build processor
                builder = MediaProcessorBuilder()
                builder.with_input_file(file_path)
                
                # Determine output path
                if custom_output_dir:
                    output_file = os.path.join(
                        custom_output_dir,
                        f"{Path(file_path).stem}.{output_format}"
                    )
                else:
                    output_file = str(Path(file_path).with_suffix(f".{output_format}"))
                
                builder.with_output_file(output_file)
                
                # Add conversion options
                if output_format in ['mp3', 'wav', 'm4a', 'flac', 'aac']:
                    builder.with_audio_bitrate(self.app.audio_bitrate.get())
                    builder.with_sample_rate(self.app.sample_rate.get())
                    if self.app.normalize.get():
                        builder.with_normalization()
                else:
                    builder.with_video_bitrate(self.app.video_bitrate.get())
                    builder.with_audio_bitrate(self.app.audio_bitrate.get())
                
                processor = builder.build()
                success = processor.process()
                
                if success:
                    input_format = Path(file_path).suffix[1:]
                    self.app.add_conversion_history(
                        os.path.basename(file_path),
                        input_format,
                        output_format,
                        success=True
                    )
                else:
                    self.app.add_conversion_history(
                        os.path.basename(file_path),
                        Path(file_path).suffix[1:],
                        output_format,
                        success=False,
                        failure_reason="Conversion failed"
                    )
                
                # Update progress
                progress = ((idx + 1) / total_files) * 100
                self.app.root.after(0, lambda p=progress: self.app.convert_tab.progress.configure(value=p))
                
            except Exception as e:
                self.app.log_error("Convert", file_path, str(e))
        
        # Completion
        self.app.root.after(0, lambda: self.app.convert_tab.status.config(text="完成!"))
        self.app.root.after(0, lambda: self.app.convert_tab.convert_btn.config(state='normal'))
        
        if self.app.auto_clear.get():
            self.app.root.after(0, self._clear_completed_convert_files)
    
    def _clear_completed_convert_files(self):
        """Clear completed files from convert list"""
        self.app.convert_file_list.clear()
        self.app.convert_tab.listbox.delete(0, 'end')
