"""History management"""
from datetime import datetime
import tkinter as tk


class HistoryManager:
    """Handles conversion and split history"""
    
    def __init__(self, app):
        self.app = app
        self.app.conversion_history = []
        self.app.split_history = []
    
    def add_conversion_history(self, filename, input_format, output_format, success=True, failure_reason=None):
        """Add conversion to history"""
        entry = {
            'filename': filename,
            'input_format': input_format,
            'output_format': output_format,
            'success': success,
            'failure_reason': failure_reason,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.app.conversion_history.append(entry)
        
        if hasattr(self.app, 'history_tab'):
            status = "✓" if success else "✗"
            self.app.history_tab.convert_history_tree.insert(
                '',
                'end',
                values=(filename, input_format, output_format, status, entry['timestamp'])
            )
        
        self.update_statistics()
    
    def add_split_history(self, filename, mode, value, parts_created, success=True, failure_reason=None):
        """Add split to history"""
        entry = {
            'filename': filename,
            'mode': mode,
            'value': value,
            'parts_created': parts_created,
            'success': success,
            'failure_reason': failure_reason,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.app.split_history.append(entry)
        
        if hasattr(self.app, 'history_tab'):
            status = "✓" if success else "✗"
            self.app.history_tab.split_history_tree.insert(
                '',
                'end',
                values=(filename, mode, value, parts_created, status, entry['timestamp'])
            )
        
        self.update_statistics()
    
    def update_statistics(self):
        """Update statistics display"""
        if not hasattr(self.app, 'history_tab'):
            return
        
        total_conversions = len(self.app.conversion_history)
        total_splits = len(self.app.split_history)
        
        successful_conversions = sum(1 for h in self.app.conversion_history if h['success'])
        successful_splits = sum(1 for h in self.app.split_history if h['success'])
        
        total_operations = total_conversions + total_splits
        successful_operations = successful_conversions + successful_splits
        
        success_rate = (successful_operations / total_operations * 100) if total_operations > 0 else 0
        
        self.app.history_tab.total_conversions_label.config(
            text=f"Total Conversions: {total_conversions}"
        )
        self.app.history_tab.total_splits_label.config(
            text=f"Total Splits: {total_splits}"
        )
        self.app.history_tab.success_rate_label.config(
            text=f"Success Rate: {success_rate:.1f}%"
        )
    
    def clear_history(self):
        """Clear all history"""
        self.app.conversion_history.clear()
        self.app.split_history.clear()
        
        if hasattr(self.app, 'history_tab'):
            for item in self.app.history_tab.convert_history_tree.get_children():
                self.app.history_tab.convert_history_tree.delete(item)
            
            for item in self.app.history_tab.split_history_tree.get_children():
                self.app.history_tab.split_history_tree.delete(item)
        
        self.update_statistics()
    
    def log_error(self, operation, filename, error_msg):
        """Log an error"""
        print(f"ERROR [{operation}] {filename}: {error_msg}")
