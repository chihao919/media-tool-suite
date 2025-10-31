"""Settings management"""
import json
import os
from pathlib import Path
from tkinter import filedialog, messagebox
import tkinter as tk
from app_constants import AppConstants


class SettingsManager:
    """Handles application settings"""
    
    def __init__(self, app):
        self.app = app
        self.settings_file = os.path.expanduser("~/.media_converter_settings.json")
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    
                    # Apply settings
                    if 'convert' in settings:
                        self.app.audio_format.set(settings['convert'].get('format', 'mp3'))
                        self.app.audio_bitrate.set(settings['convert'].get('bitrate', '192k'))
                        self.app.sample_rate.set(settings['convert'].get('sample_rate', '44100'))
                        self.app.normalize.set(settings['convert'].get('normalize', False))
                    
                    if 'split' in settings:
                        self.app.split_mode.set(settings['split'].get('mode', 'duration'))
                        self.app.split_duration.set(settings['split'].get('duration', '300'))
                        self.app.keep_original.set(settings['split'].get('keep_original', True))
                    
                    return True
        except Exception as e:
            print(f"Failed to load settings: {e}")
            return False
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            settings = {
                'convert': {
                    'format': self.app.audio_format.get(),
                    'bitrate': self.app.audio_bitrate.get(),
                    'sample_rate': self.app.sample_rate.get(),
                    'normalize': self.app.normalize.get(),
                },
                'split': {
                    'mode': self.app.split_mode.get(),
                    'duration': self.app.split_duration.get(),
                    'keep_original': self.app.keep_original.get(),
                },
                'general': {
                    'output_location': self.app.output_location.get() if hasattr(self.app, 'output_location') else 'same',
                    'naming_style': self.app.naming_style.get() if hasattr(self.app, 'naming_style') else 'original',
                    'auto_clear': self.app.auto_clear.get() if hasattr(self.app, 'auto_clear') else False,
                }
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            messagebox.showinfo("Success", "設定已儲存")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"儲存設定失敗: {str(e)}")
            return False
    
    def init_default_variables(self):
        """Initialize default settings variables"""
        self.app.default_format = tk.StringVar(value=AppConstants.DEFAULT_SETTINGS['convert']['format'])
        self.app.default_bitrate = tk.StringVar(value=AppConstants.DEFAULT_SETTINGS['convert']['bitrate'])
        self.app.default_sample_rate = tk.StringVar(value=AppConstants.DEFAULT_SETTINGS['convert']['sample_rate'])
        self.app.default_normalize = tk.BooleanVar(value=AppConstants.DEFAULT_SETTINGS['convert']['normalize'])
        
        self.app.default_split_mode = tk.StringVar(value=AppConstants.DEFAULT_SETTINGS['split']['mode'])
        self.app.default_split_duration = tk.StringVar(value=AppConstants.DEFAULT_SETTINGS['split']['duration'])
        self.app.default_keep_original = tk.BooleanVar(value=AppConstants.DEFAULT_SETTINGS['split']['keep_original'])
        
        self.app.output_location = tk.StringVar(value=AppConstants.DEFAULT_SETTINGS['general']['output_location'])
        self.app.fixed_output_dir = tk.StringVar()
        self.app.naming_style = tk.StringVar(value=AppConstants.DEFAULT_SETTINGS['general']['naming_style'])
        self.app.auto_clear = tk.BooleanVar(value=AppConstants.DEFAULT_SETTINGS['general']['auto_clear'])
    
    def apply_all_settings(self):
        """Apply default settings to current session"""
        self.app.audio_format.set(self.app.default_format.get())
        self.app.audio_bitrate.set(self.app.default_bitrate.get())
        self.app.sample_rate.set(self.app.default_sample_rate.get())
        self.app.normalize.set(self.app.default_normalize.get())
        
        self.app.split_mode.set(self.app.default_split_mode.get())
        self.app.split_duration.set(self.app.default_split_duration.get())
        self.app.keep_original.set(self.app.default_keep_original.get())
        
        messagebox.showinfo("Applied", "設定已套用到目前工作區")
    
    def reset_to_defaults(self):
        """Reset all settings to factory defaults"""
        self.app.default_format.set(AppConstants.DEFAULT_SETTINGS['convert']['format'])
        self.app.default_bitrate.set(AppConstants.DEFAULT_SETTINGS['convert']['bitrate'])
        self.app.default_sample_rate.set(AppConstants.DEFAULT_SETTINGS['convert']['sample_rate'])
        self.app.default_normalize.set(AppConstants.DEFAULT_SETTINGS['convert']['normalize'])
        
        self.app.default_split_mode.set(AppConstants.DEFAULT_SETTINGS['split']['mode'])
        self.app.default_split_duration.set(AppConstants.DEFAULT_SETTINGS['split']['duration'])
        self.app.default_keep_original.set(AppConstants.DEFAULT_SETTINGS['split']['keep_original'])
        
        self.app.output_location.set(AppConstants.DEFAULT_SETTINGS['general']['output_location'])
        self.app.naming_style.set(AppConstants.DEFAULT_SETTINGS['general']['naming_style'])
        self.app.auto_clear.set(AppConstants.DEFAULT_SETTINGS['general']['auto_clear'])
        
        messagebox.showinfo("Reset", "已重置為預設值")
    
    def browse_fixed_dir(self):
        """Browse for fixed output directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.app.fixed_output_dir.set(directory)
