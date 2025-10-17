#!/usr/bin/env python3
"""
UI Progress Bar Test
測試UI環境中的YouTube下載進度條
"""

import sys
import os
import tempfile
import tkinter as tk
from tkinter import ttk

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from youtube_downloader import YouTubeDownloader


def test_ui_progress():
    """測試UI環境中的YouTube下載進度回調"""
    print("🎯 測試UI環境中的YouTube下載進度回調...")

    # Create a simple tkinter window
    root = tk.Tk()
    root.title("Progress Test")
    root.geometry("400x200")

    progress_updates = []
    ui_updates = []

    def progress_callback(progress):
        progress_updates.append(progress)
        print(f"🔄 DEBUG: UI progress_callback called with {progress}%")

        def update_progress_ui(p=progress):
            ui_updates.append(p)
            print(f"🔄 DEBUG: UI update_progress_ui called with {p}%")
            # Simulate UI update
            label.config(text=f"Progress: {p:.1f}%")
            root.update()  # Force UI update

        root.after(0, update_progress_ui)

    # Create UI elements
    label = tk.Label(root, text="Progress: 0%", font=("Arial", 14))
    label.pack(pady=20)

    status_label = tk.Label(root, text="Ready to download", fg="blue")
    status_label.pack(pady=10)

    # Create downloader
    downloader = YouTubeDownloader()
    temp_dir = tempfile.mkdtemp()

    print(f"📁 臨時目錄: {temp_dir}")
    print("⬇️ 開始UI下載測試...")

    def start_download():
        status_label.config(text="Downloading...", fg="orange")

        def download_thread():
            try:
                success, result = downloader.download_video(
                    'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                    temp_dir,
                    'mp4',
                    '360p',
                    progress_callback
                )

                def finish_download():
                    if success:
                        status_label.config(text=f"✅ Download completed: {result}", fg="green")
                    else:
                        status_label.config(text=f"❌ Download failed: {result}", fg="red")

                    print(f"\\n📊 測試結果:")
                    print(f"進度回調次數: {len(progress_updates)}")
                    print(f"UI更新次數: {len(ui_updates)}")

                    if progress_updates:
                        print(f"進度範圍: {min(progress_updates):.1f}% - {max(progress_updates):.1f}%")

                    # Close after a few seconds
                    root.after(3000, root.quit)

                root.after(0, finish_download)

            except Exception as e:
                def error_handler():
                    status_label.config(text=f"❌ 測試異常: {e}", fg="red")
                    root.after(3000, root.quit)
                root.after(0, error_handler)

        import threading
        threading.Thread(target=download_thread, daemon=True).start()

    # Auto start download after 1 second
    root.after(1000, start_download)

    try:
        # Run UI loop with timeout
        import time
        start_time = time.time()
        timeout = 300  # 5 minutes

        while time.time() - start_time < timeout:
            try:
                root.update()
                time.sleep(0.1)
            except tk.TclError:
                # Window was closed
                break
    except:
        pass
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    # Results
    success = len(progress_updates) > 0 and len(ui_updates) > 0
    print(f"\\n🎯 UI測試結果: {'✅ 成功' if success else '❌ 失敗'}")

    return success


if __name__ == "__main__":
    print("🤖 UI環境YouTube下載進度條測試")
    print("=" * 50)

    import time
    result = test_ui_progress()

    print("\\n" + "=" * 50)
    if result:
        print("🎉 UI進度條測試成功！")
        sys.exit(0)
    else:
        print("❌ UI進度條測試失敗")
        sys.exit(1)