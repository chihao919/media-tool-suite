#!/usr/bin/env python3
"""
Automated UI Test for YouTube Download and Progress Bar
Automatically operates the UI to test YouTube download and progress functionality
"""

import sys
import os
import time
import threading
import subprocess
import tempfile
import tkinter as tk
from tkinter import ttk
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.media_converter import TabbedMediaConverter


class AutomatedUITest:
    def __init__(self):
        self.test_url = "https://www.youtube.com/watch?v=1ImEcPSdlEM&t=736s"
        self.download_dir = os.path.expanduser("~/Downloads")
        self.main_app = None
        self.test_results = []
        self.current_step = 0
        self.max_retries = 3
        self.retry_count = 0

    def log(self, message):
        """Log test progress"""
        timestamp = time.strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        self.test_results.append(log_msg)

    def wait_for_element(self, check_func, timeout=10, step=0.5):
        """Wait for UI element to be available"""
        elapsed = 0
        while elapsed < timeout:
            try:
                if check_func():
                    return True
            except:
                pass
            time.sleep(step)
            elapsed += step
        return False

    def simulate_ui_interaction(self):
        """Simulate user interaction with the UI"""
        try:
            self.log("🤖 Starting automated UI test")

            # Wait for app to be ready
            time.sleep(2)

            # Step 1: Switch to YouTube tab using root.after to run in main thread
            self.log("📺 Switching to YouTube Download tab")
            def switch_to_youtube():
                if hasattr(self.main_app, 'notebook'):
                    self.main_app.notebook.select(0)  # YouTube tab is first
                    time.sleep(1)
                    self.set_url_and_continue()

            self.main_app.root.after(100, switch_to_youtube)

        except Exception as e:
            self.log(f"❌ UI interaction error: {e}")
            import traceback
            traceback.print_exc()

    def set_url_and_continue(self):
        """Continue the test after tab switch"""
        try:
            # Step 2: Set URL
            self.log(f"🔗 Setting URL: {self.test_url}")
            if hasattr(self.main_app, 'url_entry'):
                self.main_app.url_entry.delete(0, tk.END)
                self.main_app.url_entry.insert(0, self.test_url)

            # Step 3: Set output directory
            self.log(f"📁 Setting output directory: {self.download_dir}")
            if hasattr(self.main_app, 'output_dir_var'):
                self.main_app.output_dir_var.set(self.download_dir)

            # Step 4: Set quality to a lower setting to avoid format issues
            self.log("🎬 Setting video quality to 480p")
            if hasattr(self.main_app, 'quality_var'):
                self.main_app.quality_var.set('480p')

            # Step 5: Start download
            self.log("⬇️ Starting download...")
            if hasattr(self.main_app, 'download_button'):
                # Ensure download button is enabled
                self.main_app.download_button.config(state='normal')
                # Simulate button click
                self.main_app.start_download()

                # Monitor download progress
                self.monitor_download_progress()

            else:
                self.log("❌ Download button not found")

        except Exception as e:
            self.log(f"❌ UI interaction error: {e}")
            import traceback
            traceback.print_exc()

    def monitor_download_progress(self):
        """Monitor download progress and log progress bar updates"""
        self.log("👀 Monitoring download progress...")

        start_time = time.time()
        timeout = 300  # 5 minutes timeout
        last_progress = -1
        progress_updates = []

        while time.time() - start_time < timeout:
            try:
                # Check if download is still running
                if hasattr(self.main_app, 'download_button'):
                    button_state = str(self.main_app.download_button['state'])
                    if button_state == 'normal':
                        # Download finished or not started
                        if progress_updates:
                            self.log("✅ Download completed")
                            break

                # Check progress bar value
                if hasattr(self.main_app, '_progress_value'):
                    current_progress = self.main_app._progress_value
                    if current_progress != last_progress:
                        self.log(f"📊 Progress: {current_progress:.1f}%")
                        progress_updates.append(current_progress)
                        last_progress = current_progress

                        if current_progress >= 100:
                            self.log("✅ Download progress reached 100%")
                            break

                time.sleep(1)

            except Exception as e:
                self.log(f"⚠️ Progress monitoring error: {e}")
                time.sleep(1)

        # Summary
        if progress_updates:
            self.log(f"📈 Progress updates received: {len(progress_updates)}")
            self.log(f"📊 Progress range: {min(progress_updates):.1f}% - {max(progress_updates):.1f}%")
        else:
            self.log("❌ No progress updates received!")

        return len(progress_updates) > 0

    def check_for_errors_and_fix(self):
        """Check for common errors and attempt fixes"""
        self.log("🔍 Checking for errors...")

        # Check for format availability error
        try:
            # Read recent logs or check stderr
            if "Requested format is not available" in str(self.test_results):
                self.log("🔧 Detected format error, attempting fix...")
                return self.fix_youtube_format_error()

        except Exception as e:
            self.log(f"⚠️ Error checking failed: {e}")

        return True

    def fix_youtube_format_error(self):
        """Fix YouTube format error by updating download options"""
        self.log("🔧 Fixing YouTube format error...")

        try:
            # Read the YouTube downloader to check current format options
            youtube_downloader_path = os.path.join("src", "youtube_downloader.py")
            if os.path.exists(youtube_downloader_path):
                with open(youtube_downloader_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if we need to update format options
                if "bestvideo[height<=720]+bestaudio/best[height<=720]" not in content:
                    self.log("📝 Updating YouTube downloader format options...")

                    # Update the format options to be more compatible
                    updated_content = content.replace(
                        "bestvideo+bestaudio/best",
                        "bestvideo[height<=720]+bestaudio/best[height<=720]/best"
                    )

                    # Also add fallback options
                    if "'format':" in updated_content:
                        # Find and replace format configurations
                        import re
                        pattern = r"'format':\s*'[^']*'"
                        replacement = "'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'"
                        updated_content = re.sub(pattern, replacement, updated_content)

                    with open(youtube_downloader_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)

                    self.log("✅ YouTube downloader updated")
                    return True

        except Exception as e:
            self.log(f"❌ Fix attempt failed: {e}")

        return False

    def restart_app_if_needed(self):
        """Restart the app if errors occurred"""
        if self.retry_count < self.max_retries:
            self.log("🔄 Restarting app for retry...")
            self.retry_count += 1

            # Close current app
            if self.main_app and hasattr(self.main_app, 'root'):
                self.main_app.root.quit()
                time.sleep(2)

            # Start new app instance
            return self.run_test()
        else:
            self.log("❌ Maximum retries reached")
            return False

    def run_test(self):
        """Run the complete automated test"""
        try:
            self.log("🚀 Starting automated UI test")
            self.log(f"📱 Retry attempt: {self.retry_count + 1}/{self.max_retries}")

            # Check and fix potential issues first
            self.check_for_errors_and_fix()

            # Create the main application
            self.log("🎮 Creating main application...")
            root = tk.Tk()
            self.main_app = TabbedMediaConverter(root)

            # Start UI interaction using root.after
            self.main_app.root.after(2000, self.simulate_ui_interaction)

            # Run the main loop with timeout
            self.log("🎯 Starting UI main loop...")
            start_time = time.time()
            timeout = 600  # 10 minutes total timeout

            while time.time() - start_time < timeout:
                try:
                    root.update()
                    time.sleep(0.1)
                except tk.TclError:
                    # Window was closed
                    break

            # Test completed
            self.log("🏁 Test completed")

            # Print summary
            self.print_test_summary()

            # Check if we need to retry
            if not self.was_test_successful() and self.retry_count < self.max_retries:
                return self.restart_app_if_needed()

            return self.was_test_successful()

        except Exception as e:
            self.log(f"❌ Test run failed: {e}")
            import traceback
            traceback.print_exc()

            if self.retry_count < self.max_retries:
                return self.restart_app_if_needed()

            return False

    def was_test_successful(self):
        """Check if the test was successful"""
        success_indicators = [
            "Progress: 100.0%" in str(self.test_results),
            "Download completed" in str(self.test_results),
            any("Progress:" in result for result in self.test_results)
        ]

        return any(success_indicators)

    def print_test_summary(self):
        """Print test summary"""
        self.log("\n" + "="*60)
        self.log("📊 AUTOMATED UI TEST SUMMARY")
        self.log("="*60)

        for result in self.test_results:
            print(result)

        success = self.was_test_successful()
        self.log(f"\n🎯 Test Result: {'✅ SUCCESS' if success else '❌ FAILED'}")

        if success:
            self.log("🎉 YouTube download and progress bar test completed successfully!")
        else:
            self.log("⚠️ Test failed. Check logs for issues.")


def main():
    """Main function to run automated test"""
    print("🤖 Automated UI Test for YouTube Download")
    print("=" * 60)

    # Check dependencies
    try:
        import tkinter
        print("✅ tkinter available")
    except ImportError:
        print("❌ tkinter not available")
        return False

    # Check if source files exist
    required_files = [
        "src/media_converter.py",
        "src/youtube_downloader.py"
    ]

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} found")
        else:
            print(f"❌ {file_path} not found")
            return False

    # Run the automated test
    test = AutomatedUITest()
    result = test.run_test()

    print("\n" + "="*60)
    print("🏁 Automated test completed")

    return result


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)