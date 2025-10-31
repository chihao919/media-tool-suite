"""YouTube download operations"""
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from youtube_downloader import YouTubeDownloader


class YouTubeHandler:
    """Handles YouTube download operations"""

    def __init__(self, app):
        self.app = app
        self.youtube_downloader = None

    def _init_youtube_downloader(self):
        """Initialize YouTube downloader with current settings"""
        if self.youtube_downloader:
            self.youtube_downloader.cleanup()
        self.youtube_downloader = YouTubeDownloader(max_workers=self.app.max_downloads.get())

    def show_format_selection_dialog(self, url):
        """Show format selection dialog for YouTube video"""
        try:
            self.app.youtube_tab.status.config(text="正在獲取格式資訊...", foreground="#2E8B57")
            self.app.root.update()

            # Get available formats
            self._init_youtube_downloader()
            formats = self.youtube_downloader.get_available_formats(url)

            if not formats:
                self.app.youtube_tab.status.config(text="無法獲取影片格式", foreground="#DC143C")
                return None

            # Create format selection dialog
            dialog = tk.Toplevel(self.app.root)
            dialog.title("選擇下載格式")
            dialog.geometry("500x400")
            dialog.resizable(False, False)
            dialog.transient(self.app.root)
            dialog.grab_set()

            # Center the dialog
            dialog.geometry("+%d+%d" % (
                self.app.root.winfo_rootx() + 50,
                self.app.root.winfo_rooty() + 50
            ))

            selected_format = None

            # Header frame
            header_frame = tk.Frame(dialog)
            header_frame.pack(fill=tk.X, padx=10, pady=10)

            title_label = tk.Label(header_frame, text="選擇畫質和格式", font=("Arial", 14, "bold"))
            title_label.pack()

            info_label = tk.Label(header_frame, text="請選擇您要下載的格式", font=("Arial", 10))
            info_label.pack()

            # Format list frame
            list_frame = tk.Frame(dialog)
            list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            # Create listbox with scrollbar
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            format_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 10))
            format_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=format_listbox.yview)

            # Populate format list
            format_data = []
            for i, fmt in enumerate(formats):
                size_str = f"{fmt['size_mb']:.1f}MB" if fmt['size_mb'] else "Unknown"
                display_text = f"{fmt['label']:<25} | {size_str:>10}"

                # Add type indicator
                if fmt['type'] == 'audio':
                    display_text += " | 🎵 Audio"
                elif fmt['type'] == 'separate':
                    display_text += " | 🎬 Best Quality"
                else:
                    display_text += " | 📺 Video"

                format_listbox.insert(tk.END, display_text)
                format_data.append(fmt)

            # Select first format by default
            if format_data:
                format_listbox.selection_set(0)

            # Button frame
            button_frame = tk.Frame(dialog)
            button_frame.pack(fill=tk.X, padx=10, pady=10)

            def on_download():
                selection = format_listbox.curselection()
                if selection:
                    nonlocal selected_format
                    selected_format = format_data[selection[0]]
                    dialog.destroy()

            def on_cancel():
                dialog.destroy()

            # Buttons
            download_btn = tk.Button(button_frame, text="下載", command=on_download,
                                   bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                                   relief=tk.RAISED, bd=2, padx=20)
            download_btn.pack(side=tk.RIGHT, padx=5)

            cancel_btn = tk.Button(button_frame, text="取消", command=on_cancel,
                                 bg="#f44336", fg="white", font=("Arial", 12),
                                 relief=tk.RAISED, bd=2, padx=20)
            cancel_btn.pack(side=tk.RIGHT, padx=5)

            # Handle double-click on listbox
            def on_double_click(event):
                on_download()

            format_listbox.bind("<Double-Button-1>", on_double_click)

            # Wait for dialog to close
            self.app.root.wait_window(dialog)

            return selected_format

        except Exception as e:
            self.app.youtube_tab.status.config(text=f"格式獲取失敗: {str(e)}", foreground="#DC143C")
            return None

    def download_youtube_unified(self):
        """Unified YouTube download based on selected mode"""
        url = self.app.youtube_url.get().strip()
        if not url:
            self.app.youtube_tab.status.config(text="Please enter a YouTube URL", foreground="#DC143C")
            return

        # Show format selection dialog
        selected_format = self.show_format_selection_dialog(url)
        if not selected_format:
            self.app.youtube_tab.status.config(text="下載已取消", foreground="#FF8C00")
            return

        mode = self.app.youtube_mode.get()

        if "Download & Split" in mode:
            self.download_and_split_youtube_with_format(selected_format)
        elif "Audio Only" in mode:
            self.download_youtube_audio_with_format(selected_format)
        elif "Playlist" in mode:
            self.download_youtube_playlist()
        else:  # Default to "Download"
            self.download_youtube_only_with_format(selected_format)

    def download_youtube_only_with_format(self, selected_format):
        """Download YouTube video with specific format without splitting"""
        url = self.app.youtube_url.get().strip()

        # Select directory first (in main thread to avoid UI blocking)
        output_path = filedialog.askdirectory(title="Select Download Directory")
        if not output_path:
            self.app.youtube_tab.status.config(text="下載已取消", foreground="#FF8C00")
            return

        self._init_youtube_downloader()
        self.app.youtube_tab.status.config(text="下載中...", foreground="#2E8B57")
        self.app.youtube_tab.progress.set(0)
        self.app.youtube_tab.progress_label.config(text="0%")

        def download_thread():
            try:
                def progress_callback(progress):
                    def update_progress_yt(p=progress):
                        self.app.youtube_tab.progress.set(p)
                        self.app.youtube_tab.progress_label.config(text=f"{int(p)}%")
                        self.app.youtube_tab.status.config(
                            text=f"下載中... {p:.1f}%", foreground="#2E8B57")
                    self.app.root.after(0, update_progress_yt)

                success, result = self.youtube_downloader.download_video_with_format(
                    url, output_path, selected_format['format_id'], selected_format['ext'], progress_callback)

                if success:
                    self.app.root.after(0, lambda: self.app.youtube_tab.status.config(
                        text=f"✅ 下載完成: {os.path.basename(result)}", foreground="#228B22"))
                    # Add to split list
                    self.app.split_files.append(result)
                    self.app.split_tab.listbox.insert('end', os.path.basename(result))
                else:
                    self.app.root.after(0, lambda: self.app.youtube_tab.status.config(
                        text=f"❌ 下載失敗: {result}", foreground="#DC143C"))

            except Exception as e:
                self.app.root.after(0, lambda: self.app.youtube_tab.status.config(
                    text=f"❌ 錯誤: {str(e)}", foreground="#DC143C"))

        threading.Thread(target=download_thread, daemon=True).start()

    def download_youtube_audio_with_format(self, selected_format):
        """Download YouTube audio with specific format"""
        url = self.app.youtube_url.get().strip()

        # Select directory first (in main thread to avoid UI blocking)
        output_path = filedialog.askdirectory(title="Select Download Directory")
        if not output_path:
            self.app.youtube_tab.status.config(text="下載已取消", foreground="#FF8C00")
            return

        self._init_youtube_downloader()
        self.app.youtube_tab.status.config(text="下載音頻中...", foreground="#2E8B57")
        self.app.youtube_tab.progress.set(0)
        self.app.youtube_tab.progress_label.config(text="0%")

        def download_thread():
            try:
                def progress_callback(progress):
                    def update_progress_yt(p=progress):
                        self.app.youtube_tab.progress.set(p)
                        self.app.youtube_tab.progress_label.config(text=f"{int(p)}%")
                        self.app.youtube_tab.status.config(
                            text=f"下載音頻中... {p:.1f}%", foreground="#2E8B57")
                    self.app.root.after(0, update_progress_yt)

                success, result = self.youtube_downloader.download_video_with_format(
                    url, output_path, selected_format['format_id'], selected_format['ext'], progress_callback)

                if success:
                    self.app.root.after(0, lambda: self.app.youtube_tab.status.config(
                        text=f"✅ 音頻下載完成: {os.path.basename(result)}", foreground="#228B22"))
                    # Add to split list
                    self.app.split_files.append(result)
                    self.app.split_tab.listbox.insert('end', os.path.basename(result))
                else:
                    self.app.root.after(0, lambda: self.app.youtube_tab.status.config(
                        text=f"❌ 音頻下載失敗: {result}", foreground="#DC143C"))

            except Exception as e:
                self.app.root.after(0, lambda: self.app.youtube_tab.status.config(
                    text=f"❌ 錯誤: {str(e)}", foreground="#DC143C"))

        threading.Thread(target=download_thread, daemon=True).start()

    def download_and_split_youtube_with_format(self, selected_format):
        """Download YouTube video with specific format and split it"""
        url = self.app.youtube_url.get().strip()

        # Select directory first (in main thread to avoid UI blocking)
        output_path = filedialog.askdirectory(title="Select Download Directory")
        if not output_path:
            self.app.youtube_tab.status.config(text="下載已取消", foreground="#FF8C00")
            return

        self._init_youtube_downloader()
        self.app.youtube_tab.status.config(text="下載並分割中...", foreground="#2E8B57")

        def download_split_thread():
            try:
                # Get split settings from UI
                split_mode = self.app.split_mode.get()
                split_value = None

                if split_mode == "duration":
                    try:
                        split_value = int(self.app.split_duration.get())
                    except ValueError:
                        split_value = 300  # Default 5 minutes
                elif split_mode == "size":
                    try:
                        split_value = int(self.app.split_size.get())
                    except ValueError:
                        split_value = 100  # Default 100MB
                elif split_mode == "parts":
                    try:
                        split_value = int(self.app.split_parts.get())
                    except ValueError:
                        split_value = 3  # Default 3 parts

                def progress_callback(progress):
                    def update_progress_yt(p=progress):
                        self.app.youtube_tab.progress.set(p)
                        self.app.youtube_tab.progress_label.config(text=f"{int(p)}%")
                        self.app.youtube_tab.status.config(
                            text=f"下載並分割中... {p:.1f}%", foreground="#2E8B57")
                    self.app.root.after(0, update_progress_yt)

                # Use existing split functionality
                success_split, split_results = self.youtube_downloader.download_and_split_extended(
                    url, output_path, split_mode, split_value,
                    selected_format['ext'], selected_format['format_id'], progress_callback)

                if success_split:
                    self.app.root.after(0, lambda: self.app.youtube_tab.status.config(
                        text=f"✅ 下載並分割完成: {len(split_results)} 個檔案", foreground="#228B22"))
                    # Add all split files to list
                    for split_file in split_results:
                        if split_file not in self.app.split_files:
                            self.app.split_files.append(split_file)
                            self.app.split_tab.listbox.insert('end', os.path.basename(split_file))
                else:
                    self.app.root.after(0, lambda: self.app.youtube_tab.status.config(
                        text=f"❌ 分割失敗: {split_results[0] if split_results else 'Unknown error'}", foreground="#DC143C"))

            except Exception as e:
                self.app.root.after(0, lambda: self.app.youtube_tab.status.config(
                    text=f"❌ 錯誤: {str(e)}", foreground="#DC143C"))

        threading.Thread(target=download_split_thread, daemon=True).start()

    def download_youtube_playlist(self):
        """Download entire YouTube playlist"""
        url = self.app.youtube_url.get().strip()
        if not url:
            self.app.youtube_tab.status.config(text="Please enter a YouTube playlist URL", foreground="#DC143C")
            return

        self._init_youtube_downloader()
        self.app.youtube_tab.status.config(text="Downloading playlist...", foreground="#2E8B57")

        def download_playlist_thread():
            try:
                output_path = filedialog.askdirectory(title="Select Download Directory")
                if not output_path:
                    self.app.youtube_tab.status.config(text="Download cancelled", foreground="#FF8C00")
                    return

                def progress_callback(progress):
                    self.app.root.after(0, lambda: self.app.youtube_tab.status.config(
                        text=f"Downloading playlist... {progress:.1f}%", foreground="#2E8B57"))

                results = self.youtube_downloader.download_playlist(
                    url, output_path, self.app.youtube_format.get(), self.app.youtube_quality.get(), progress_callback)

                successful_downloads = [r for r in results if r[1]]
                failed_downloads = [r for r in results if not r[1]]

                if successful_downloads:
                    # Add all successful downloads to split list
                    for title, success, file_path in successful_downloads:
                        if success and os.path.exists(file_path):
                            self.app.split_files.append(file_path)
                            self.app.split_tab.listbox.insert('end', os.path.basename(file_path))

                    self.app.root.after(0, lambda: self.app.youtube_tab.status.config(
                        text=f"✅ Downloaded {len(successful_downloads)} videos" +
                        (f", {len(failed_downloads)} failed" if failed_downloads else ""),
                        foreground="#228B22"))
                else:
                    self.app.root.after(0, lambda: self.app.youtube_tab.status.config(
                        text="❌ No videos downloaded successfully", foreground="#DC143C"))

            except Exception as e:
                self.app.root.after(0, lambda: self.app.youtube_tab.status.config(
                    text=f"❌ Error: {str(e)}", foreground="#DC143C"))

        threading.Thread(target=download_playlist_thread, daemon=True).start()
