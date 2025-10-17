#!/usr/bin/env python3
"""
Complete Progress Bar Integration Test
Test both Split functionality and progress callback integration
"""

import sys
import os
import tempfile
import threading
import time
import tkinter as tk
from tkinter import ttk

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from process_strategies import SplitStrategy
from media_processor import MediaProcessorBuilder

def create_test_video(size_mb=50, duration=30):
    """Create a test video file using ffmpeg"""
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    temp_file.close()

    try:
        import subprocess
        # Create a test video using ffmpeg
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', f'testsrc=duration={duration}:size=320x240:rate=1',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
            '-y', temp_file.name
        ]

        print(f"Creating test video: {temp_file.name}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            return None

        actual_size = os.path.getsize(temp_file.name) / (1024 * 1024)
        print(f"Created test video: {actual_size:.2f}MB, Duration: {duration}s")
        return temp_file.name

    except Exception as e:
        print(f"Error creating test video: {e}")
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        return None

class ProgressBarTestApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Progress Bar Integration Test")
        self.root.geometry("400x700")

        # Create Canvas progress bar (same as media_converter.py)
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(pady=20)

        ttk.Label(progress_frame, text="Progress Test", font=('Helvetica', 12, 'bold')).pack(pady=(0, 10))

        self.progress_canvas = tk.Canvas(progress_frame, width=38, height=400, bg='#E0E0E0',
                                       relief='sunken', bd=1, highlightthickness=0)
        self.progress_canvas.pack(pady=5)

        # Initialize progress bar components
        self._progress_bg = self.progress_canvas.create_rectangle(0, 0, 38, 400,
                                                                fill='#E0E0E0', outline='')
        self._progress_fill = self.progress_canvas.create_rectangle(0, 400, 38, 400,
                                                                  fill='#2E8B57', outline='')
        self._progress_value = 0

        # Progress percentage label
        self.progress_percent = ttk.Label(progress_frame, text="0%", font=('Helvetica', 14, 'bold'))
        self.progress_percent.pack(pady=(10, 0))

        # Status label
        self.status_label = ttk.Label(self.root, text="Ready for testing",
                                    font=('Helvetica', 10), foreground='blue')
        self.status_label.pack(pady=10)

        # Test buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Test Manual Progress",
                  command=self.test_manual_progress).pack(pady=5)
        ttk.Button(button_frame, text="Test Split Progress",
                  command=self.test_split_progress).pack(pady=5)
        ttk.Button(button_frame, text="Test YouTube Download",
                  command=self.test_youtube_download).pack(pady=5)
        ttk.Button(button_frame, text="Reset Progress",
                  command=self.reset_progress).pack(pady=5)

        # Log area
        log_frame = ttk.Frame(self.root)
        log_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        ttk.Label(log_frame, text="Test Log:", font=('Helvetica', 10, 'bold')).pack(anchor=tk.W)

        self.log_text = tk.Text(log_frame, height=8, width=50, font=('Courier', 9))
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def log(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        print(f"[{timestamp}] {message}")

    def update_progress_bar(self, value):
        """Update the custom progress bar (value: 0-100) - Same as media_converter.py"""
        self._progress_value = max(0, min(100, value))

        # Calculate fill height
        fill_height = (self._progress_value / 100) * 400
        fill_top = 400 - fill_height

        # Update the progress fill rectangle
        self.progress_canvas.coords(self._progress_fill, 0, fill_top, 38, 400)

        # Update percentage label
        self.progress_percent.config(text=f"{int(self._progress_value)}%")

        self.log(f"Progress updated: {self._progress_value:.1f}%")

    def test_manual_progress(self):
        """Test manual progress updates"""
        self.log("=== Starting Manual Progress Test ===")
        self.status_label.config(text="Testing manual progress...")

        test_values = [0, 25, 50, 75, 100]

        for i, value in enumerate(test_values):
            def update_ui(v=value, step=i):
                self.update_progress_bar(v)
                self.status_label.config(text=f"Manual test step {step+1}: {v}%")

            self.root.after(i * 1000, update_ui)

        self.root.after(len(test_values) * 1000,
                       lambda: [self.status_label.config(text="Manual test completed"),
                               self.log("=== Manual Progress Test Completed ===")])

    def test_split_progress(self):
        """Test split functionality with progress callback"""
        self.log("=== Starting Split Progress Test ===")

        # Create test video
        test_video = create_test_video(size_mb=30, duration=60)
        if not test_video:
            self.log("❌ Failed to create test video")
            return

        def run_split_test():
            try:
                self.log(f"Created test video: {test_video}")

                # Test size-based splitting
                self.log("Testing size-based split (10MB target)...")

                def progress_callback(progress):
                    def update_ui(p=progress):
                        self.update_progress_bar(p)
                        self.status_label.config(text=f"Splitting... {p:.1f}%")
                    self.root.after(0, update_ui)

                # Create splitter
                processor = MediaProcessorBuilder.create_splitter('size', size=10)

                output_params = {
                    'keep_original': True,
                    'progress_callback': progress_callback
                }

                self.log("Starting split operation...")
                success = processor.process_file(test_video, output_params)

                def finish_test():
                    if success:
                        self.log("✅ Split test completed successfully!")
                        self.status_label.config(text="Split test completed")
                    else:
                        self.log("❌ Split test failed")
                        self.status_label.config(text="Split test failed")

                    # Clean up
                    if os.path.exists(test_video):
                        os.unlink(test_video)
                        self.log("🧹 Cleaned up test video")

                self.root.after(0, finish_test)

            except Exception as e:
                def show_error():
                    self.log(f"❌ Split test error: {e}")
                    import traceback
                    traceback.print_exc()
                    if os.path.exists(test_video):
                        os.unlink(test_video)

                self.root.after(0, show_error)

        # Run in thread
        self.status_label.config(text="Creating test video...")
        thread = threading.Thread(target=run_split_test)
        thread.daemon = True
        thread.start()

    def test_youtube_download(self):
        """Test YouTube download with the specified URL"""
        self.log("=== Starting YouTube Download Test ===")

        url = "https://www.youtube.com/watch?v=1ImEcPSdlEM&t=736s"

        def run_youtube_test():
            try:
                # Import YouTube downloader
                from youtube_downloader import YouTubeDownloader

                downloader = YouTubeDownloader()

                def progress_callback(progress):
                    def update_ui(p=progress):
                        self.update_progress_bar(p)
                        self.status_label.config(text=f"Downloading... {p:.1f}%")
                    self.root.after(0, update_ui)

                self.log(f"Testing download from: {url}")

                # Create temp directory for download
                temp_dir = tempfile.mkdtemp()
                self.log(f"Download directory: {temp_dir}")

                success, result = downloader.download_video(
                    url, temp_dir, 'mp4', '720p', progress_callback
                )

                def finish_youtube_test():
                    if success:
                        self.log(f"✅ YouTube download completed: {result}")
                        self.status_label.config(text="YouTube download completed")
                    else:
                        self.log(f"❌ YouTube download failed: {result}")
                        self.status_label.config(text="YouTube download failed")

                    # Clean up
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    self.log("🧹 Cleaned up download directory")

                self.root.after(0, finish_youtube_test)

            except Exception as e:
                def show_error():
                    self.log(f"❌ YouTube test error: {e}")
                    import traceback
                    traceback.print_exc()

                self.root.after(0, show_error)

        # Run in thread
        self.status_label.config(text="Starting YouTube download...")
        thread = threading.Thread(target=run_youtube_test)
        thread.daemon = True
        thread.start()

    def reset_progress(self):
        """Reset progress to 0"""
        self.update_progress_bar(0)
        self.status_label.config(text="Progress reset")
        self.log("Progress reset to 0%")

    def run(self):
        """Start the test application"""
        self.log("🎯 Progress Bar Integration Test Started")
        self.log("Click buttons to test different progress scenarios")
        self.root.mainloop()

if __name__ == "__main__":
    # Check if ffmpeg is available
    try:
        import subprocess
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg detected")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  FFmpeg not available - some tests will be skipped")

    test_app = ProgressBarTestApp()
    test_app.run()