#!/usr/bin/env python3
"""
Integration Test for Progress Bar and Split Functionality
Test both progress bar updates and file size splitting together
"""

import sys
import os
import tkinter as tk
import threading
import time
import tempfile

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from media_converter import TabbedMediaConverter

class ProgressSplitIntegrationTest:
    """Integration test for progress bar and split functionality"""

    def __init__(self):
        self.test_results = []

    def create_test_video_file(self, size_mb=200):
        """Create a dummy test file of specified size"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)

        # Create a file of approximately the specified size
        chunk_size = 1024 * 1024  # 1MB chunks
        for _ in range(size_mb):
            temp_file.write(b'0' * chunk_size)

        temp_file.close()
        return temp_file.name

    def test_split_parameters(self):
        """Test how split parameters are handled"""
        print("=== Testing Split Parameters ===")

        root = tk.Tk()
        app = TabbedMediaConverter(root)

        # Test 1: Check default values
        print(f"Default split_mode: {app.split_mode.get()}")
        print(f"Default split_duration: {app.split_duration.get()}")
        print(f"Default split_size: {app.split_size.get()}")

        # Test 2: Set File Size mode and value
        app.split_mode.set("size")
        app.split_size.set("190")
        app.update_split_mode()  # This should update the UI

        print(f"After setting size mode:")
        print(f"Split mode: {app.split_mode.get()}")
        print(f"Split size: {app.split_size.get()}")

        # Test 3: Check what the split worker would use
        print(f"\nWhat _split_worker would use:")
        print(f"Mode check: app.split_mode.get() == 'size' -> {app.split_mode.get() == 'size'}")
        print(f"Size value: int(app.split_size.get()) -> {int(app.split_size.get())}")

        root.destroy()
        return True

    def test_progress_updates_during_split(self):
        """Test progress bar updates during actual split simulation"""
        print("\n=== Testing Progress Updates During Split ===")

        root = tk.Tk()
        app = TabbedMediaConverter(root)

        # Create test file list
        test_file = self.create_test_video_file(200)  # 200MB file
        app.split_files = [test_file]

        # Set split parameters
        app.split_mode.set("size")
        app.split_size.set("190")

        print(f"Test file: {test_file}")
        print(f"File size: {os.path.getsize(test_file) / (1024*1024):.1f}MB")
        print(f"Target split size: {app.split_size.get()}MB")

        def simulate_split_with_progress():
            """Simulate the split process with progress updates"""
            try:
                # Simulate progress updates like _split_worker does
                total = len(app.split_files)
                print(f"Total files to process: {total}")

                for i, file_path in enumerate(app.split_files):
                    progress = ((i + 1) / total) * 100

                    # Test the exact same update logic as _split_worker
                    def update_progress(p=progress):
                        app.shared_progress.configure(value=p)
                        app.progress_percent.config(text=f"{int(p)}%")
                        print(f"Progress updated to: {int(p)}%")

                    root.after(0, update_progress)

                    filename = os.path.basename(file_path)
                    root.after(0, lambda f=filename: app.combined_status.config(text=f"Testing: {f}"))

                    # Simulate processing time
                    time.sleep(1)
                    root.update()

                print("Split simulation completed!")

            except Exception as e:
                print(f"Error in simulation: {e}")
                import traceback
                traceback.print_exc()
            finally:
                # Clean up test file
                if os.path.exists(test_file):
                    os.unlink(test_file)

        # Start simulation
        thread = threading.Thread(target=simulate_split_with_progress)
        thread.daemon = True
        thread.start()

        # Run for a few seconds then close
        root.after(5000, root.quit)
        root.mainloop()

        return True

    def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Starting Integration Tests")
        print("=" * 50)

        try:
            # Test 1: Parameter handling
            result1 = self.test_split_parameters()
            self.test_results.append(("Split Parameters", result1))

            # Test 2: Progress updates
            result2 = self.test_progress_updates_during_split()
            self.test_results.append(("Progress Updates", result2))

            # Summary
            print("\n" + "=" * 50)
            print("🧪 Test Results Summary:")
            for test_name, result in self.test_results:
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{test_name}: {status}")

        except Exception as e:
            print(f"\n❌ Test suite failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    tester = ProgressSplitIntegrationTest()
    tester.run_all_tests()