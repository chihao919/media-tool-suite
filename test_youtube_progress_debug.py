#!/usr/bin/env python3
"""
YouTube下載進度條Debug測試（帶UI progressbar檢查）
"""

import sys
import os
import tempfile
import tkinter as tk
from tkinter import ttk

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from youtube_downloader import YouTubeDownloader


class ProgressTestApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Progress Debug Test")
        self.root.geometry("500x400")

        # Progress tracking
        self.progress_updates = []
        self.ui_updates = []

        # Create UI elements similar to main app
        self.status_label = tk.Label(self.root, text="Ready", font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.progress_percent = tk.Label(self.root, text="0%", font=("Arial", 14, "bold"))
        self.progress_percent.pack(pady=5)

        # Create custom progress bar like main app
        self.shared_progress = tk.Canvas(self.root, width=40, height=400, bg='white', relief='sunken', bd=2)
        self.shared_progress.pack(pady=10)

        # Create progress bar elements
        self._progress_value = 0
        self._progress_fill = self.shared_progress.create_rectangle(0, 400, 38, 400, fill='#4CAF50', outline='')

        # Test button
        self.test_button = tk.Button(self.root, text="Start YouTube Download Test",
                                   command=self.start_test, font=("Arial", 12))
        self.test_button.pack(pady=20)

        # Log area
        self.log_text = tk.Text(self.root, height=10, width=60)
        self.log_text.pack(pady=10)

        self.downloader = YouTubeDownloader()

    def log(self, message):
        """Add log message"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        print(message)

    def update_progress_bar(self, value):
        """Update the custom progress bar (value: 0-100)"""
        print(f"🔄 DEBUG: update_progress_bar called with value: {value}")
        self.log(f"🔄 UI Progress Bar Update: {value:.1f}%")
        self._progress_value = max(0, min(100, value))

        # Calculate fill height
        fill_height = (self._progress_value / 100) * 400
        fill_top = 400 - fill_height

        print(f"🔄 DEBUG: Updating progress bar - value: {self._progress_value:.1f}%, fill_height: {fill_height}, fill_top: {fill_top}")

        # Update the progress fill rectangle
        self.shared_progress.coords(self._progress_fill, 0, fill_top, 38, 400)

    def start_test(self):
        """Start the YouTube download test"""
        self.test_button.config(state='disabled')
        self.log("🎯 Starting YouTube Download Progress Test...")

        import threading
        threading.Thread(target=self.test_download, daemon=True).start()

    def test_download(self):
        """Test download with progress callbacks"""
        try:
            temp_dir = tempfile.mkdtemp()
            self.log(f"📁 Created temp directory: {temp_dir}")

            def progress_callback(progress):
                self.progress_updates.append(progress)
                print(f"🔄 DEBUG: progress_callback called with {progress}%")
                self.log(f"📊 Progress Callback: {progress:.1f}%")

                def update_progress_yt(p=progress):
                    self.ui_updates.append(p)
                    print(f"🔄 DEBUG: update_progress_yt called with {p}%")
                    self.log(f"🔧 UI Update Function: {p:.1f}%")

                    # Update UI elements
                    self.update_progress_bar(p)
                    self.progress_percent.config(text=f"{int(p)}%")
                    self.status_label.config(text=f"Downloading... {p:.1f}%")

                self.root.after(0, update_progress_yt)

            self.log("⬇️ Starting download...")
            success, result = self.downloader.download_video(
                'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                temp_dir,
                'mp4',
                '360p',
                progress_callback
            )

            # Final update
            def finish_test():
                if success:
                    self.status_label.config(text=f"✅ Download completed: {os.path.basename(result)}")
                    self.log(f"✅ Download successful: {result}")
                else:
                    self.status_label.config(text=f"❌ Download failed: {result}")
                    self.log(f"❌ Download failed: {result}")

                self.log(f"\n📊 Test Results:")
                self.log(f"Progress callbacks received: {len(self.progress_updates)}")
                self.log(f"UI updates performed: {len(self.ui_updates)}")

                if self.progress_updates:
                    self.log(f"Progress range: {min(self.progress_updates):.1f}% - {max(self.progress_updates):.1f}%")

                self.test_button.config(state='normal')

                # Cleanup
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                self.log("🧹 Cleaned up temp directory")

            self.root.after(0, finish_test)

        except Exception as e:
            def error_handler():
                self.status_label.config(text=f"❌ Test error: {e}")
                self.log(f"❌ Test error: {e}")
                import traceback
                self.log(traceback.format_exc())
                self.test_button.config(state='normal')
            self.root.after(0, error_handler)

    def run(self):
        """Run the test app"""
        self.log("🤖 YouTube Progress Debug Test App")
        self.log("Click the button to start testing...")
        self.root.mainloop()


if __name__ == "__main__":
    app = ProgressTestApp()
    app.run()